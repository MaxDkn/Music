from enum import IntEnum

class WaitlistStatus(IntEnum):
    WAITING = 101                 # En attente de téléchargement
    DOWNLOADING = 102             # Téléchargement en cours
    SUCCESS = 200                 # Téléchargement réussi
    ERROR_API_ITUNES = 401        # Erreur API iTunes
    ERROR_DOWNLOAD = 402          # Erreur téléchargement audio
    ERROR_PROCESSING = 403        # Erreur traitement/conversion
    ERROR_INCOMPLETE_DATA = 404   # Métadonnées manquantes
    ERROR_UNKNOWN = 500           # Erreur inconnue

    def description(self) -> str:
        return {
            self.WAITING: "En attente de téléchargement",
            self.DOWNLOADING: "Téléchargement en cours",
            self.SUCCESS: "Téléchargement réussi et ajouté à MUSIC",
            self.ERROR_API_ITUNES: "Erreur lors de l'appel à l'API iTunes",
            self.ERROR_DOWNLOAD: "Erreur lors du téléchargement de la musique",
            self.ERROR_PROCESSING: "Erreur de conversion ou traitement du fichier audio",
            self.ERROR_INCOMPLETE_DATA: "Métadonnées manquantes ou invalides",
            self.ERROR_UNKNOWN: "Erreur inconnue ou inattendue"
        }[self]
