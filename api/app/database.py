import os
import time
import socket
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


def wait_for_db(host: str, port: int | str, logger, timeout: int = 30):
    """
    Attend que la base de données soit disponible à l'adresse et au port spécifiés.

    Cette fonction tente de se connecter à la base de données en utilisant les informations
    d'hôte et de port fournies. Elle réessaie toutes les secondes jusqu'à ce que la connexion
    soit établie ou que le délai d'attente spécifié soit écoulé.

    Args:
        host (str): L'adresse de l'hôte de la base de données.
        port (int | str): Le port de la base de données. Peut être fourni en tant qu'entier ou chaîne de caractères.
        logger: Un objet logger pour enregistrer les messages d'information.
        timeout (int, optional): Le délai d'attente maximum en secondes avant de lever une exception.
                                 Par défaut, 30 secondes.

    Raises:
        ValueError: Si le port ne peut pas être converti en entier.
        Exception: Si la connexion à la base de données échoue après le délai d'attente spécifié.

    Example:
        >>> import logging
        >>> logger = logging.getLogger(__name__)
        >>> wait_for_db('localhost', 5432, logger)
        Connexion à la base de données réussie.
    """
    try:
        port = int(port)
    except:
        raise f"port {port} cannot convert into integer"
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=2):
                logger.info("Connexion à la base de données réussie.")
                break
        except OSError:
            time.sleep(1)
            logger.warning('Echec de connexions à la base de données, on attend 1 seconde avant de réessayer...') 
            if time.time() - start_time > timeout:
                raise Exception(f"Impossible de se connecter à la base de données sur {host}:{port}")


engine = create_engine(os.getenv('DATABASE_URL'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
