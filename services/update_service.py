import requests
import re


class UpdateService:

    VERSION_URL = "https://raw.githubusercontent.com/SatisfactoryFrance/satisfactory_blueprint_manager/refs/heads/v2/version.json"

    ''' 
    URLS = {
        "stable": "https://raw.githubusercontent.com/SatisfactoryFrance/satisfactory_blueprint_manager/refs/heads/v2/version.json",
        "beta":   "https://sbm.satisfactoryfr.com/version-beta.json",
        }

        ==> URLS[UPDATE_CHANNEL]
    '''


    def __init__(self):
        pass

    # ------------------------------
    # Utils
    # ------------------------------
    def _parse_version(self, v: str):
        """
        Transforme 'v2.1.1' -> (2, 1, 1)
        """
        if not v:
            return (0, 0, 0)

        v = v.strip().lower()
        if v.startswith("v"):
            v = v[1:]

        match = re.match(r"(\d+)\.(\d+)\.(\d+)", v)
        if not match:
            return (0, 0, 0)

        return tuple(int(x) for x in match.groups())

    # ------------------------------
    # Update check
    # ------------------------------
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
                return True, None, None, "Version distante introuvable"

            local_v = self._parse_version(current_version)
            remote_v = self._parse_version(remote_version)

            # DEBUG
            print(f"[UPDATE] local={local_v} remote={remote_v}")

            if remote_v > local_v:
                return False, remote_version, download_url, None

            return True, remote_version, None, None

        except requests.exceptions.RequestException as e:
            # On n'embête pas l'utilisateur si GitHub est HS
            return True, None, None, f"Erreur réseau : {e}"

        except ValueError:
            return True, None, None, "Erreur lecture JSON"
