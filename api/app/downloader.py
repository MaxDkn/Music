import yt_dlp
import os
import requests
from io import BytesIO
from pathlib import Path
from app.schemas import ITunesResponse


def seek_itunes_music(query: str, url: str = "https://itunes.apple.com/search", limit: int = 10, lang: str = "fr_fr"):
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
        if data["resultCount"] > 0:
            return data['results']
    else:
        return {"error": f"Request failed with status code {response.status_code}"}


def get_track_info(track_id: int, url: str = "https://itunes.apple.com/lookup"):
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
        ITunesResponse(trackId=123456789, trackName='Track Name', artistId=123456, artistName='Artist Name', artworkUrl100='https://is1-ssl.mzstatic.com/image/thumb/Music123/v4/ab/cd/ef/abcdefghijklmnopqrstuvwxyz/600x600bb.jpg')
        >>> get_track_info(999999999)
        {"error": "Request failed with status code 404"}
    """
    response = requests.get(url + f"?id={track_id}")
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        if results:
            track = results[0]
            track['artworkUrl100'] = track['artworkUrl100'].replace('100x100bb.jpg', '600x600bb.jpg')
            return ITunesResponse(**track)
    else:
        return {"error": f"Request failed with status code {response.status_code}"}


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

def download_music(watch_key: str, output_origin_path: str = 'data/audios') -> bytes:
    url = f"https://www.youtube.com/watch?v={watch_key}"
    output_path = os.path.join(output_origin_path, watch_key + ".%(ext)s")

    if not os.path.exists(output_origin_path):
        os.makedirs(output_origin_path)

    for file in os.listdir(output_origin_path):
        if file.startswith(watch_key):
            with open(os.path.join(output_origin_path, file), "rb") as f:
                return f.read()

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir(output_origin_path):
            if file.startswith(watch_key):
                with open(os.path.join(output_origin_path, file), "rb") as f:
                    return f.read()
    except Exception:
        return None
