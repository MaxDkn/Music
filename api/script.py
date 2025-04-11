import yt_dlp
import os


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


def download_music(watch_key: str, output_origin_path: str = '/app/data') -> str:
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


if __name__ == '__main__':
    title = "Gangnam Style"
    artist = "Psy"

    watch_key = get_watch_key(title, artist)
    print(download_music(watch_key))
    
    #  if isinstance(result, bytes):
        #  print("La musique a été téléchargée et retournée sous forme de buffer.")
        #  with open('test.mp3', 'wb') as file:
        #      file.write(result)
        #  print(f'downloaded at test.mp3 - {watch_key}')
    #  else:
    #      print(result)
