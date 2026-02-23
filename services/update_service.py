import requests


class UpdateService:

    VERSION_URL = "https://sbm.satisfactoryfr.com/version.json"

    def __init__(self):
        pass

    def check_for_update(self, current_version: str):
        """
        Retourne :
        (is_up_to_date, remote_version, download_url, error_message)
        """

        try:
            response = requests.get(self.VERSION_URL, timeout=10)
            response.raise_for_status()

            remote_data = response.json()

            remote_version = remote_data.get("version")
            download_url = remote_data.get("download_url")

            if not remote_version:
                return False, None, None, "Version distante introuvable"

            if remote_version > current_version:
                return False, remote_version, download_url, None

            return True, remote_version, None, None

        except requests.exceptions.RequestException as e:
            return False, None, None, f"Erreur réseau : {e}"

        except ValueError:
            return False, None, None, "Erreur lecture JSON"
