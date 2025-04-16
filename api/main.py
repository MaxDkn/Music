#  https://github.com/Zxce3/shadcn-sveltekit-landing-page
import os
import re
import time
from typing import List, Dict
from app.enums.waitlist import WaitlistStatus
from sqlalchemy.orm import Session
from app import models, crud, downloader
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas import MusicDBResponse, ITunesResponse
from app.database import Base, engine, SessionLocal, wait_for_db
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import io
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="MusicAPI",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None
)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(message)s",
    handlers=[logging.StreamHandler()]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pour tester, sinon utilise ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)


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
    logging.getLogger('apscheduler').setLevel(logging.WARNING)
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(recurring_task, 'interval', minutes=0.5)
    scheduler.start()


@app.on_event("startup")
async def startup_event():
    start_scheduler()


@app.get('/api/music/search', response_model=List[ITunesResponse], tags=["search"])
async def itunes_query(q: str, db: Session = Depends(get_db)):
    results = downloader.seek_itunes_music(query=q)
    if results:
        for result in results:
            result['statusCode'] = crud.get_status_code(db, result['trackId'])
        return results
    else:
        raise HTTPException(status_code=404, detail=f"Aucun résultat trouvé.")


@app.get('/api/music/search_track/{id}', response_model=ITunesResponse, tags=['search'])
async def itunes_query(id: int, db: Session = Depends(get_db)):
    result = downloader.get_track_info(db=db, track_id=id)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail=f"Aucun résultat trouvé.")


@app.get('/api/music/status/all', tags=["status"])
def get_all_status_code(db: Session = Depends(get_db)):
    return {music.trackId: WaitlistStatus(music.status).description() for music in db.query(models.Waitlist).all()}


@app.get("/api/music/status", tags=["status"])
def get_status(tracks_id: List[str], db: Session = Depends(get_db)) -> Dict[str, str]:
    results = {}

    for track_id in tracks_id:
        music = db.query(models.Waitlist).filter(models.Waitlist.trackId == track_id).first()
        if not music:
            # Si le morceau n'est pas dans la DB, on tente de le récupérer
            music_info = downloader.get_track_info(db=db, track_id=track_id)
            if music_info:
                crud.add_waitlist_entry(db, track_id=music_info.trackId, status=WaitlistStatus.INDEXED.value)
                results[track_id] = WaitlistStatus.INDEXED.value
            else:
                results[track_id] = "NOT_FOUND"
        else:
            results[track_id] = music.status

    return results


"""
@app.get('/api/music/status/reset/{track_id}', tags=["status"])
def get_status_code_of_a_track(track_id: int, db: Session = Depends(get_db)):
    return crud.modify_status(db, track_id=track_id, status=WaitlistStatus.INDEXED.value)
"""

@app.get('/api/music/download/{track_id}', tags=["download"])
def download_music(track_id: int, db: Session = Depends(get_db)):
    music = db.query(models.Waitlist).filter(models.Waitlist.trackId == track_id).first()
    if not music:
        music = crud.add_waitlist_entry(db, track_id=track_id, status=WaitlistStatus.WAITING.value)        
    else:
        if music.status != WaitlistStatus.INDEXED.value:
            status = WaitlistStatus(music.status)
            return {'status_code': status.value, 'description': status.description()}
        music = crud.modify_status(db, track_id=track_id, status=WaitlistStatus.WAITING.value)
    if music is None:
        raise HTTPException(status_code=404, detail=f"Error with {track_id} please check the database.")
    status = WaitlistStatus(music.status)

    return {'status_code': status.value, 'description': status.description()}


@app.get('/api/music/all', tags=['music'], response_model=List[MusicDBResponse])
def get_all_music_id_downloaded(db: Session = Depends(get_db)):
    return db.query(models.Music).all()


@app.get('/api/music/{music_id}', tags=['music'])
def get_musique_by_id(music_id: str, db: Session = Depends(get_db)):
    music = db.query(models.Music).filter(models.Music.trackId == music_id).first()
    if not music:
        raise HTTPException(status_code=404, detail=f"Music with id {music_id} not found")
    return StreamingResponse(io.BytesIO(music.musicBuffer), media_type="audio/mpeg")




"""
@app.get('/api/music/{music_id}', response_model=MusicDBResponse)
def get_musique_by_id(music_id: str, db: Session = Depends(get_db)):
    music = db.query(models.Music).filter(models.Music.MusicId == music_id).first()
    if not music:
        raise HTTPException(status_code=404, detail=f"Music with id {music_id} not found")
    return MusicDBResponse.from_orm(music)
"""

