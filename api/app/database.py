import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import time
import socket

def wait_for_db(host: str, port: int | str, timeout: int = 30):
    try:
        port = int(port)
    except:
        raise f"port {port} cannot convert into integer"
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=2):
                print("Connexion à la base de données réussie.")
                break
        except OSError:
            time.sleep(1)
            if time.time() - start_time > timeout:
                raise Exception(f"Impossible de se connecter à la base de données sur {host}:{port}")

engine = create_engine(os.getenv('DATABASE_URL'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
