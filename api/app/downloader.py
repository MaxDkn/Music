import yt_dlp
import os
import requests
from io import BytesIO
from pathlib import Path

def rechercher_musique_itunes(recherche):
    url = "https://itunes.apple.com/search"
    params = {
        "term": recherche,
        "media": "music",
        "limit": 1,
        "lang": "fr_fr"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["resultCount"] > 0:
        musique = data["results"][0]
        titre = musique["trackName"]
        artiste = musique["artistName"]
        couverture_url = musique["artworkUrl100"].replace("100x100", "600x600")

        img_response = requests.get(couverture_url)
        cover_path = Path("cover.jpg")
        with open(cover_path, "wb") as f:
            f.write(img_response.content)

        buffer = BytesIO(img_response.content)

        return {
            "titre": titre,
            "artiste": artiste,
            "fichier": cover_path,
            "buffer": buffer
        }
    else:
        return None

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
