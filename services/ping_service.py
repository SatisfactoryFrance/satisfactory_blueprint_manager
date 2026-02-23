import threading
import requests


class PingService:

    BASE_URL = "https://sbmping.satisfactoryfr.com:5001/hits"

    def send(self, client_id):

        def worker():
            try:
                requests.post(f"{self.BASE_URL}/{client_id}", timeout=5, verify=False)
            except:
                pass

        threading.Thread(target=worker, daemon=True).start()
