import requests
import re


class UpdateService:

    VERSION_URL_STABLE = "https://raw.githubusercontent.com/SatisfactoryFrance/satisfactory_blueprint_manager/main/version.json"
    VERSION_URL_BETA = "https://sbm.satisfactoryfr.com/version-beta.json"

    # ------------------------------
    # Utils
    # ------------------------------

    def _parse_version(self, v: str):
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

    def check_for_update(self, current_version: str, channel: str):

        try:

            # ✅ choix URL selon channel
            if channel.lower() == "beta":
                url = self.VERSION_URL_BETA
            else:
                url = self.VERSION_URL_STABLE

            print(f"[UPDATE] Checking {channel} channel → {url}")

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            remote_data = response.json()

            remote_version = remote_data.get("version")
            download_url = remote_data.get("download_url")

            if not remote_version:
                return True, None, None, "Version distante introuvable"

            local_v = self._parse_version(current_version)
            remote_v = self._parse_version(remote_version)

            print(f"[UPDATE] local={local_v} remote={remote_v}")

            if remote_v > local_v:
                return False, remote_version, download_url, None

            return True, remote_version, None, None

        except requests.exceptions.RequestException as e:
            return True, None, None, f"Erreur réseau : {e}"

        except ValueError:
            return True, None, None, "Erreur lecture JSON"
