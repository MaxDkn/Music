from calendar import c
import os
import yt_dlp
import tempfile
import requests
from io import BytesIO
import app.crud as crud
from app.schemas import ITunesResponse
from app.enums.waitlist import WaitlistStatus


class RequestFailed(BaseException):
    """
    Exception levée lorsque la requête échoue.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def seek_itunes_music(query: str, url: str = "https://itunes.apple.com/search", limit: int = 7, lang: str = "fr_fr"):
    """
    Recherche de la musique sur iTunes en utilisant l'API de recherche iTunes.

    Cette fonction envoie une requête à l'API de recherche iTunes pour trouver des morceaux de musique
    correspondant à un terme de recherche donné. Elle retourne les résultats trouvés jusqu'à la limite
    spécifiée ou un message indiquant que rien n'a été trouvé.

    Args:
        query (str): Le terme de recherche pour trouver de la musique.
        url (str, optional): L'URL de l'API de recherche iTunes. Par défaut, "https://itunes.apple.com/search".
        limit (int, optional): Le nombre maximum de résultats à retourner. Par défaut, 10.
        lang (str, optional): Le code de langue pour les résultats. Par défaut, "fr_fr" (français).

    Returns:
        list or str: Une liste de dictionnaires contenant les détails des résultats trouvés si la recherche est
                     réussie, sinon une chaîne de caractères "Not found".

    Example:
        >>> seek_itunes_music("Imagine")
        [{'wrapperType': 'track', 'kind': 'song', 'artistId': 3296287, ...}, ...]

        >>> seek_itunes_music("NonExistentSong123")
        None
    """
    response = requests.get(url, params={
        "term": query,
        "media": "music",
        "limit": limit,
        "lang": lang
    })

    if response.status_code == 200:
        data = response.json()
        if data.get("resultCount", 0) > 0:
            unique_results = []
            seen = set()
            for result in data.get('results', []):
                title = result.get('trackName')
                artist = result.get('artistName')
                key = (title, artist)
                # Ne garder que la première occurrence de chaque titre/auteur
                if key not in seen:
                    seen.add(key)
                    # Ajuster l'URL de la jaquette pour obtenir l'image originale
                    cover_image_url = result.get('artworkUrl100')
                    result['coverImageUrl'] = cover_image_url.replace('100x100bb.jpg', '')
                    unique_results.append(result)
                    # S'assurer de ne pas dépasser la limite
                    if len(unique_results) >= limit:
                        break
            return unique_results
        return []
    elif response.status_code == 404:
        return []
    else:
        print(f"SEEK_ITUNES_MUSIC : Request failed with status code {response.status_code}")
        return []
        

def get_track_info(db, track_id: int, url: str = "https://itunes.apple.com/lookup"):
    """
    Récupère les informations d'une piste musicale à partir de son identifiant iTunes.

    Cette fonction envoie une requête à l'API de recherche iTunes pour obtenir les détails d'une piste
    musicale spécifiée par son identifiant. Elle retourne les informations de la piste, y compris une
    URL d'image de couverture de haute qualité.

    Args:
        track_id (int): L'identifiant unique de la piste musicale sur iTunes.
        url (str, optional): L'URL de l'API de recherche iTunes. Par défaut, "https://itunes.apple.com/lookup".

    Returns:
        dict: Un dictionnaire contenant les informations de la piste musicale si la requête est réussie.
              Si la requête échoue, un dictionnaire avec une clé "error" contenant le message d'erreur.

    Example:
        >>> get_track_info(123456789)
        ITunesResponse(trackId=123456789, trackName='Track Name', artistId=123456, artistName='Artist Name', coverImageUrl='https://is1-ssl.mzstatic.com/image/thumb/Music123/v4/ab/cd/ef/abcdefghijklmnopqrstuvwxyz/600x600bb.jpg')
        >>> get_track_info(999999999)
        {"error": "Request failed with status code 404"}
    """
    response = requests.get(url + f"?id={track_id}")
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        if results:
            track = results[0]
            track['coverImageUrl'] = track['artworkUrl100'].replace('100x100bb.jpg', '')
            statusCode = crud.get_status_code(db=db, track_id=track_id)
            track['statusCode'] = statusCode
            track['statusDescription'] = WaitlistStatus(statusCode).description()
            return ITunesResponse(**track)
    else:
        raise {"error": f"Request failed with status code {response.status_code}"}


def get_watch_key(title: str, artist: str) -> str:
    query = f"{title} {artist}"
    ydl_opts = {
        'quiet': True,
        'noplaylist': True,
        'default_search': 'ytsearch',
        'max_downloads': 1,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(query, download=False)
            if 'entries' in result:
                return result['entries'][0]['id']
            else:
                return None
    except Exception as e:
        return None

def download_music_on_ytb(watch_key: str, output_path="tmp_downloads") -> BytesIO:
    """
    Télécharge l'audio depuis YouTube en utilisant le watch_key et retourne un objet BytesIO.
    
    La fonction utilise un fichier temporaire pour enregistrer la musique téléchargée,
    puis lit ce fichier pour retourner son contenu dans un BytesIO.
    """
    url = f"https://www.youtube.com/watch?v={watch_key}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/{watch_key}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'noplaylist': True,
    }
    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'audio')
            
            filename = os.path.join(output_path, f"{watch_key}.mp3")

        with open(filename, 'rb') as f:
            audio_bytes = BytesIO(f.read())
        audio_bytes.seek(0)

        # Supprimer le fichier temporaire après lecture
        os.remove(filename)
        return audio_bytes
    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")
        # S'assurer de supprimer le fichier temporaire en cas d'erreur
        return None
    

def download_music(track_id: int, db, logger):
    try:
        # Modifier le statut à "DOWNLOADING"
        crud.modify_status(
            db=db, 
            track_id=track_id,
            status=WaitlistStatus.DOWNLOADING.value
        )
        logger.info(f"Track ID {track_id} is being downloaded.")
        # Récupérer les informations de la piste à partir de l'API iTunes
        track_info = get_track_info(db=db, track_id=track_id)
        if not track_info:
            crud.modify_status(
                db=db, 
                track_id=track_id,
                status=WaitlistStatus.ERROR_NOT_FOUND_ON_ITUNES.value
            )
            return {"error": "Track not found on iTunes"}

        # Vérifier les attributs nécessaires
        trackName = getattr(track_info, 'trackName', None)
        artistName = getattr(track_info, 'artistName', None)
        coverImageUrl = getattr(track_info, 'coverImageUrl', None)
        if not all([trackName, artistName, coverImageUrl]):
            crud.modify_status(
                db=db, 
                track_id=track_id,
                status=WaitlistStatus.ERROR_INVALID_DATA.value
            )
            logger.error('Invalid track data from iTunes')
            return {"error": "Invalid track data from iTunes"}

        # Modifier l'URL de l'image de couverture
        coverImageUrl = coverImageUrl.replace('100x100bb.jpg', '')

        # Obtenir la clé YouTube
        musicKey = get_watch_key(trackName, artistName)
        if musicKey is None:
            crud.modify_status(
                db=db, 
                track_id=track_id,
                status=WaitlistStatus.ERROR_NOT_FOUND_ON_YOUTUBE.value
            )
            logger.error('Music not found on YouTube')
            return {"error": "Not found on YouTube"}

        # Télécharger la musique depuis YouTube
        musicBuffer = download_music_on_ytb(musicKey)
        if musicBuffer is None:
            crud.modify_status(
                db=db, 
                track_id=track_id,
                status=WaitlistStatus.ERROR_DOWNLOAD.value
            )
            logger.error('Download failed')
            return {"error": "Download failed"}
        
        # Ajouter la musique à la base de données
        crud.create_music_entry(
            trackId=track_id,
            trackName=trackName,
            artistId=track_info.artistId,
            artistName=artistName,
            coverImageUrl=coverImageUrl,
            musicKey=musicKey,
            musicBuffer=musicBuffer.getvalue(),
            db=db
        )

        # Modifier le statut à "SUCCESS"
        crud.modify_status(
            db=db, 
            track_id=track_id,
            status=WaitlistStatus.SUCCESS.value
        )

        return {"message": "Download successful"}

    except Exception as e:
        # Gestion des erreurs inattendues
        crud.modify_status(
            db=db, 
            track_id=track_id,
            status=WaitlistStatus.ERROR_UNKNOWN.value
        )
        return {"error": f"An unexpected error occurred: {str(e)}"}
