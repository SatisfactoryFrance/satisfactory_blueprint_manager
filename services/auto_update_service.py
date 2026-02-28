import os
import sys
import subprocess
import tempfile
import requests
import zipfile
from tkinter import messagebox


class AutoUpdateService:

    # ✅ on reçoit l'app tkinter
    def __init__(self, app):
        self.app = app

    # -------------------------------------------------
    # fermeture propre (CRITIQUE en PyInstaller onefile)
    # -------------------------------------------------
    def safe_quit(self):
        import os
        import sys

        self.app.update_idletasks()
        self.app.destroy()

        # tue le process immédiatement (aucun thread bloquant)
        os._exit(0)

    # -------------------------------------------------
    # téléchargement + remplacement EXE
    # -------------------------------------------------
    def download_and_apply(self, url):
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "sbm.zip")

        # ---------------- DOWNLOAD ----------------
        r = requests.get(url, stream=True)
        r.raise_for_status()

        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

        # ---------------- EXTRACT ----------------
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(temp_dir)

        new_exe = None
        for root, _, files in os.walk(temp_dir):
            for f in files:
                if f.lower().endswith(".exe"):
                    new_exe = os.path.join(root, f)
                    break

        if not new_exe:
            raise Exception("Nouvel EXE introuvable dans le zip")

        # ---------------- LAUNCH UPDATER ----------------
        current_exe = sys.executable
        base_dir = os.path.dirname(current_exe)

        updater_path = os.path.join(base_dir, "updater.exe")

        if not os.path.exists(updater_path):
            raise Exception("updater.exe introuvable")

        #messagebox.showinfo(
        #    self.app.t("update_available"),
        #    self.app.t("update_confirm")
        #)

        subprocess.Popen([
            updater_path,
            current_exe,
            new_exe
        ])


        # fermer IMMÉDIATEMENT SBM
        os._exit(0)
