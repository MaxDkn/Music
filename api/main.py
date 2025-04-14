#  https://github.com/Zxce3/shadcn-sveltekit-landing-page
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app import models, crud, downloader
from app.schemas import MusicIdResponse, MusicResponse  
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
import time

app = FastAPI()


Base.metadata.create_all(bind=engine)


# Fonction qui sera appelée toutes les 30 minutes
def recurring_task():
    print("Tâche récurrente exécutée à", time.strftime("%Y-%m-%d %H:%M:%S"))

# Fonction pour démarrer le scheduler
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(recurring_task, 'interval', minutes=30)  # Exécute la tâche toutes les 30 minutes
    scheduler.start()

# Lancer le scheduler au démarrage de l'application
@app.on_event("startup")
async def startup_event():
    print("Démarrage de l'application FastAPI")
    start_scheduler()

@app.get("/")
def read_root():
    return {"message": "API FastAPI avec tâche récurrente toutes les 30 minutes"}



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


@app.get('/api/music_id/all')
def get_all_music_id_downloaded(db: Session = Depends(get_db)):
    return MusicIdResponse.from_orm(db.query(models.Music).all())


@app.get('/api/music/{music_id: str}', response_model=MusicResponse)
def get_musique_by_id(music_id: str, db: Session = Depends(get_db)):
    music = db.query(models.Music).filter(models.Music.MusicId == music_id).first()
    if not music:
        raise HTTPException(status_code=404, detail=f"Music with id {music_id} not found")
    return MusicResponse.from_orm(music)


