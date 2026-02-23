import os
import customtkinter as ctk
from tkinter import messagebox, filedialog

from ui.sidebar import Sidebar
from ui.main_window import MainWindow
from ui.scim_window import ScimWindow

from core.config import ConfigService
from services.blueprint_service import BlueprintService
from services.scim_service import ScimService
from services.update_service import UpdateService
from services.ping_service import PingService

from utils.threads import run_bg

from core.version import BUILD_NUMBER
from core.paths import get_blueprints_base

from ui.menubar import build_menubar
from services.i18n_service import I18nService

# BUILD_NUMBER = "v2.0.0"


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        build_menubar(self)

        # ---------------- SERVICES ----------------

        self.config = ConfigService()
        self.blueprints = BlueprintService()
        self.scim = ScimService()
        self.updater = UpdateService()
        self.ping = PingService()

        self.i18n = I18nService(self.config.get_lang())
        self.t = self.i18n.t  # d'après la documentation i18n

        self.ping.send(self.config.get_id())

        # ---------------- UI ----------------

        self.title(f"Satisfactory Blueprint Manager - {BUILD_NUMBER}")
        self.geometry("1200x600")

        self.sidebar = Sidebar(self)
        self.sidebar.pack(side="top", fill="x")

        self.main = MainWindow(self)
        self.main.pack(fill="both", expand=True)

        # ---------------- Startup ----------------

        self.check_update()
        self.load_blueprints()

    # ======================================================
    # BLUEPRINTS
    # ======================================================

    def load_blueprints(self):
        folder = self.config.get_game_folder()

        if not folder or folder == "undefined":

            default = get_blueprints_base()

            folder = filedialog.askdirectory(initialdir=default)

            if not folder:
                return

            self.config.set_game_folder(folder)

        bps = self.blueprints.list_blueprints(folder)
        self.main.render_blueprints(bps)
        self.sidebar.dropdown.set(os.path.basename(folder))

    def delete_blueprint(self, name):
        folder = self.config.get_game_folder()

        if messagebox.askyesno("Supprimer", "Supprimer ce blueprint ?"):
            self.blueprints.delete_blueprint(folder, name)
            self.load_blueprints()

    def upload_blueprints(self):

        files = filedialog.askopenfilenames(filetypes=[("Blueprint", "*.sbp")])

        if not files:
            return

        folder = self.config.get_game_folder()

        if not self.blueprints.check_sbpcfg_exists(files):
            messagebox.showerror("Erreur", "Fichier .sbpcfg manquant")
            return

        if not self.blueprints.check_duplicates(files, folder):
            messagebox.showerror("Erreur", "Blueprint déjà existant")
            return

        self.blueprints.upload_blueprints(files, folder)
        self.load_blueprints()

    # ======================================================
    # SCIM
    # ======================================================

    def open_scim(self):
        ScimWindow(self)

    def download_scim(self, blueprint_id, title):

        folder = self.config.get_game_folder()

        try:
            name = self.scim.download_blueprint(blueprint_id, title, folder)
            messagebox.showinfo("OK", f"{name} téléchargé")
            self.load_blueprints()

        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # ======================================================
    # UPDATE
    # ======================================================

    def check_update(self):
        ok, remote, url, error = self.updater.check_for_update(BUILD_NUMBER)

        if error:
            return

        if not ok:
            messagebox.showinfo(
                "Mise à jour",
                f"Nouvelle version : {remote}\n{url}"
            )
