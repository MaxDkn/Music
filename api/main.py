#  https://github.com/Zxce3/shadcn-sveltekit-landing-page
import os
import re
import time
from typing import List
from sqlalchemy.orm import Session
from app import models, crud, downloader
from fastapi import FastAPI, Depends, HTTPException
from app.schemas import MusicDBResponse, ITunesResponse
from app.database import Base, engine, SessionLocal, wait_for_db
from apscheduler.schedulers.background import BackgroundScheduler
'''  DATABASE
WAITLIST :
    "trackId" INTEGER,
    "trackName" VARCHAR(100),
    "artisteId" INTEGER,
    "artisteName" VARCHAR(100),
    "coverImageUrl" VARCHAR(200),
    "MusicKey" VARCHAR(11),
    "status" INTEGER

MUSIC :
    "trackId" INTEGER,
    "trackName" VARCHAR(100),
    "artisteId" INTEGER,
    "artisteName" VARCHAR(100),
    "coverImageUrl" VARCHAR(200),
    "MusicKey" VARCHAR(11),
    "MusicBuffer" BYTEA
'''

app = FastAPI()


#  attend que la base de donnée se crée, le script dégueux est pour récuperer à partir de l'url de la bdd, le host name et port.
wait_for_db(*re.search(r'@([^/]+)', os.getenv('DATABASE_URL')).group(1).split(':'))
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""def recurring_task():
    print("Tâche récurrente exécutée à", time.strftime("%Y-%m-%d %H:%M:%S"))

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(recurring_task, 'interval', minutes=30)  # Exécute la tâche toutes les 30 minutes
    scheduler.start()

@app.on_event("startup")
async def startup_event():
    print("Démarrage de l'application FastAPI")
    start_scheduler()

@app.get("/")
def read_root():
    return {"message": "API FastAPI avec tâche récurrente toutes les 30 minutes"}
"""

"""
@app.get("/download/{query}")
def download(query: str, db: Session = Depends(get_db)):
    info = downloader.rechercher_musique_itunes(query)
    if not info:
        return {"error": "Not found on iTunes"}

    watch_key = downloader.get_watch_key(info["titre"], info["artiste"])
    if not watch_key:
        return {"error": "Not found on YouTube"}

    audio = downloader.download_music(watch_key)
    if not audio:
        return {"error": "Download failed"}

    item = crud.create_index(db, info["titre"], info["artiste"], info["buffer"].getvalue(), audio)
    return {"message": "Saved", "id": item.MusicId}
"""

@app.get('/api/music/search/{query}', response_model=List[ITunesResponse])
def itunes_query(query: str):
    results = downloader.seek_itunes_music(query=query)
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail=f"Aucun résultat trouvé.")


@app.get('/api/music/search_track/{id}', response_model=ITunesResponse)
def itunes_query(id: int):
    results = downloader.get_track_info(track_id=id)
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail=f"Aucun résultat trouvé.")

"""
@app.post('/api/music/download')
def add_music_on_download_waitlist():
    return True


@app.get('/api/music/all')
def get_all_music_id_downloaded(db: Session = Depends(get_db)):
    return db.query(models.Music).all()


@app.get('/api/music/{music_id}', response_model=MusicDBResponse)
def get_musique_by_id(music_id: str, db: Session = Depends(get_db)):
    music = db.query(models.Music).filter(models.Music.MusicId == music_id).first()
    if not music:
        raise HTTPException(status_code=404, detail=f"Music with id {music_id} not found")
    return MusicDBResponse.from_orm(music)
"""

