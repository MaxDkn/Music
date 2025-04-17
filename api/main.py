#  https://github.com/Zxce3/shadcn-sveltekit-landing-page
import os
import re
import time
from typing import List, Dict, Optional
from app.enums.waitlist import WaitlistStatus
from sqlalchemy.orm import Session
from app import models, crud, downloader
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.schemas import MusicDBResponse, ITunesResponse
from app.database import Base, engine, SessionLocal, wait_for_db
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import io
from fastapi.middleware.cors import CORSMiddleware
import datetime
import random


app = FastAPI(
    title="MusicAPI",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pour tester, sinon utilise ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(message)s",
    handlers=[logging.StreamHandler()]
)
recurring_job = None


def _compute_next_run_seconds():
    if not recurring_job or not recurring_job.next_run_time:
        return None
    next_run = recurring_job.next_run_time
    now = datetime.datetime.now(next_run.tzinfo) if next_run.tzinfo else datetime.datetime.now()
    return int((next_run - now).total_seconds())


#  attend que la base de donnée se crée, le script dégueux est pour récuperer à partir de l'url de la bdd, le host name et port.
wait_for_db(*re.search(r'@([^/]+)', os.getenv('DATABASE_URL')).group(1).split(':'), logger)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def recurring_task():
    db = SessionLocal()
    try:
        results = []
        # Parcourir les pistes en attente
        for track in db.query(models.Waitlist).filter(models.Waitlist.status == WaitlistStatus.WAITING.value).all():
            try:
                # Télécharger la musique et ajouter le résultat
                result = downloader.download_music(track.trackId, db, logger)
                results.append({track.trackId: result})
            except Exception as e:
                # Gérer les erreurs pour chaque piste individuellement
                logger.error(f"Erreur lors du téléchargement de la piste {track.trackId}: {e}")
                results.append({track.trackId: {"error": str(e)}})
        if results:
            for result in results:
                for track_id, data in result.items():
                    if isinstance(data, dict) and "error" in data:
                        logger.error(f"Erreur pour la piste {track_id}: {data['error']}")
                    else:
                        logger.info(f"Piste {track_id} téléchargée avec succès.")
    except Exception as e:
        logger.error(f"Erreur lors du processus de téléchargement : {e}")
    finally:
        db.close()


def start_scheduler():
    global recurring_job
    logging.getLogger('apscheduler').setLevel(logging.WARNING)
    scheduler = BackgroundScheduler()
    recurring_job = scheduler.add_job(recurring_task, 'interval', minutes=0.5)
    scheduler.start()


@app.on_event("startup")
async def startup_event():
    start_scheduler()


@app.get('/api/music/search', response_model=List[ITunesResponse], tags=["search"])
async def itunes_query(q: str, db: Session = Depends(get_db)):
    results = downloader.seek_itunes_music(query=q)

    if results:
        for result in results:
            statusCode = crud.get_status_code(db, result['trackId'])
            result['statusCode'] = statusCode
            result['statusDescription'] = WaitlistStatus(statusCode).description()
        return results
    else:
        raise HTTPException(status_code=404, detail=f"Result not found.")


@app.get('/api/music/search_track/{id}', response_model=ITunesResponse, tags=['search'])
async def search_track_with_track_id(id: int, db: Session = Depends(get_db)):
    result = downloader.get_track_info(db=db, track_id=id)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail=f"Result not found.")


@app.get('/api/music/status/all', tags=["status"])
def get_all_status_code(db: Session = Depends(get_db)):
    return {music.trackId: WaitlistStatus(music.status).description() for music in db.query(models.Waitlist).all()}


@app.get("/api/audio", tags=["download"])
def stream_track(trackId: str, request: Request, db: Session = Depends(get_db)) -> Dict[str, str]:
    music = db.query(models.Music).filter(models.Music.trackId == trackId).first()
    if not music:
        raise HTTPException(status_code=404, detail=f"Music with id {trackId} not found")
    musicBuffer = io.BytesIO(music.musicBuffer)
    file_size = musicBuffer.getbuffer().nbytes
    range_header = request.headers.get("range")

    if range_header:
        start = int(range_header.replace("bytes=", "").split("-")[0])
        end = file_size - 1
        chunk_size = end - start + 1

        def iterfile():
            musicBuffer.seek(start)
            yield musicBuffer.read(chunk_size)

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(chunk_size),
            "Content-Type": "audio/mpeg",
        }
        return StreamingResponse(iterfile(), status_code=206, headers=headers)

    return StreamingResponse(musicBuffer, media_type="audio/mpeg")


@app.get('/api/music/download', tags=["download"])
def download_music(trackId: int, db: Session = Depends(get_db)):
    music = db.query(models.Waitlist).filter_by(trackId=trackId).first()
    if not music:
        # Vérifie que la piste existe bien sur iTunes avant insertion
        track_info = downloader.get_track_info(db, track_id=trackId)
        if not track_info or (isinstance(track_info, dict) and 'error' in track_info):
            raise HTTPException(status_code=404, detail=f"Music with id {trackId} not found")
        music = crud.add_waitlist_entry(db, track_id=trackId, status=WaitlistStatus.WAITING.value)
    if music.status == WaitlistStatus.INDEXED.value:
        music = crud.modify_status(db, track_id=trackId, status=WaitlistStatus.WAITING.value)

    if not music:
        raise HTTPException(status_code=404, detail=f"Error with {trackId}, please check the database.")

    status = WaitlistStatus(music.status)
    return {
        "statusCode": status.value,
        "statusDescription": status.description(),
        "nextRun": _compute_next_run_seconds(),
    }


@app.get('/api/music/all', tags=['music'], response_model=List[MusicDBResponse])
def get_all_music_id_downloaded(db: Session = Depends(get_db)):
    return db.query(models.Music).all()


@app.get("/api/foryou", tags=["foryou"], response_model=List[MusicDBResponse])
def get_foryou(limit: Optional[int] = 4, db: Session = Depends(get_db)):
    # 1. Compter les IDs disponibles (plus rapide que .all())
    music_ids = db.query(models.Music.trackId).all()
    if not music_ids:
        return []

    # 2. Sélection aléatoire d'IDs
    random_ids = random.sample([id[0] for id in music_ids], min(limit, len(music_ids)))

    # 3. Requête uniquement sur les colonnes nécessaires
    results = db.query(
        models.Music.trackId,
        models.Music.trackName,
        models.Music.artistName,
        models.Music.coverImageUrl
    ).filter(models.Music.trackId.in_(random_ids)).all()

    return [dict(row._mapping) for row in results]