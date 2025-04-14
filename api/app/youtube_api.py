import yt_dlp
import os
import requests
from pprint import pprint

import requests
from io import BytesIO
from pathlib import Path


"""
status file :



index file : 
 MusicId | Titre | Artiste  #   CoverImageBuffer | MusicBuffer




"""


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

        print("🎵 Titre :", titre)
        print("🎤 Artiste :", artiste)
        print("🖼️ Couverture URL :", couverture_url)

        # Télécharger la couverture dans un fichier
        img_response = requests.get(couverture_url)
        cover_path = Path("cover.jpg")
        with open(cover_path, "wb") as f:
            f.write(img_response.content)
        print(f"✅ Couverture enregistrée dans : {cover_path.resolve()}")

        # Charger la couverture dans un buffer (BytesIO)
        buffer = BytesIO(img_response.content)
        print(f"📦 Image également disponible dans le buffer (type: {type(buffer)})")

        return {
            "titre": titre,
            "artiste": artiste,
            "fichier": cover_path,
            "buffer": buffer
        }

    else:
        print("Aucun résultat trouvé.")
        return None


# Exemple d'utilisation
if __name__ == "__main__":
    recherche = input("Entrez le nom de la musique ou d’un artiste : ")
    resultat = rechercher_musique_itunes(recherche)

    if resultat:
        # Exemple : afficher la taille du buffer
        print(f"🧠 Taille du buffer image : {resultat['buffer'].getbuffer().nbytes} octets")


def get_watch_key(title: str, artist: str) -> str:
    """
    Recherche une vidéo YouTube en utilisant le titre de la musique et l'artiste, et retourne le `watch_key` 
    (ID de la vidéo).

    Cette fonction utilise `yt_dlp` pour effectuer une recherche YouTube avec les informations fournies 
    (titre et artiste). Elle renvoie l'ID de la première vidéo trouvée, qui peut être utilisé pour télécharger 
    la vidéo ou obtenir des informations supplémentaires.

    Args:
        title (str): Le titre de la musique à rechercher.
        artist (str): Le nom de l'artiste ou des artistes associés à la musique.

    Returns:
        str: L'ID de la vidéo YouTube (le `watch_key`) correspondant à la recherche.
             Si aucune vidéo n'est trouvée, un message d'erreur est retourné.
    """
    query = f"{title} {artist}"
    ydl_opts = {
        'quiet': True,  # Pour ne pas afficher les logs
        'noplaylist': True,  # Ne pas télécharger une playlist
        'default_search': 'ytsearch',  # Effectuer une recherche YouTube
        'max_downloads': 1,  # Limiter la recherche à une seule vidéo
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Effectuer la recherche
            result = ydl.extract_info(query, download=False)

            # Vérifier si un résultat a été trouvé
            if 'entries' in result:
                video = result['entries'][0]
                watch_key = video['id']  # Récupérer le watch_key (ID de la vidéo)
                return watch_key
            else:
                return "Aucune vidéo trouvée."
    except Exception as e:
        return f"Erreur lors de la recherche : {e}"


def download_music(watch_key: str, output_origin_path: str = '/app/data/audios') -> str:
    """
    Télécharge la musique depuis YouTube en utilisant le `watch_key` de la vidéo.

    Cette fonction prend l'ID d'une vidéo YouTube (le `watch_key`), télécharge la meilleure qualité audio
    disponible, puis l'enregistre au format MP3 dans le répertoire de destination spécifié.

    Args:
        watch_key (str): L'ID de la vidéo YouTube à télécharger (ex. : "KQ6zr6kCPj8").

    Returns:
        str: Un message indiquant si le téléchargement a réussi ou s'il y a eu une erreur.
    """
    url = f"https://www.youtube.com/watch?v={watch_key}"
    output_path = os.path.join(output_origin_path, watch_key + ".%(ext)s")
    
    for file in os.listdir(output_origin_path):
        if file.startswith(watch_key):
            return f"file already downloaded: {watch_key} - {os.path.join(output_origin_path, file)}"

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
        return "done"
    except Exception as e:
        return f"Erreur lors du téléchargement : {e}"

