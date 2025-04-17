from enum import IntEnum

class WaitlistStatus(IntEnum):
    INDEXED = 100                 # Track indexé mais téléchargement non prévu
    WAITING = 101                 # En attente de téléchargement
    DOWNLOADING = 102             # Téléchargement en cours
    SUCCESS = 200                 # Téléchargement réussi
    ERROR_API_ITUNES = 401        # Erreur API iTunes
    ERROR_DOWNLOAD = 402          # Erreur téléchargement audio
    ERROR_PROCESSING = 403        # Erreur traitement/conversion
    ERROR_INCOMPLETE_DATA = 404   # Métadonnées manquantes
    ERROR_NOT_FOUND_ON_YOUTUBE = 405  # Pas trouvé sur YouTube
    ERROR_UNKNOWN = 500           # Erreur inconnue

    def description(self) -> str:
        return {
            self.INDEXED: "Indexed but not scheduled for download",
            self.WAITING: "Waiting to download",
            self.DOWNLOADING: "Downloading...",
            self.SUCCESS: "successful download",
            self.ERROR_API_ITUNES: "Error with iTunes API",
            self.ERROR_DOWNLOAD: "Error during audio download",
            self.ERROR_PROCESSING: "Error during processing/conversion",
            self.ERROR_INCOMPLETE_DATA: "Incomplete metadata",
            self.ERROR_NOT_FOUND_ON_YOUTUBE: "Not found on YouTube",
            self.ERROR_UNKNOWN: "Unknown error",
        }[self]
