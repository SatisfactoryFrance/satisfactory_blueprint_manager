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

from core.version import BUILD_NUMBER
from core.paths import get_blueprints_base

from ui.menubar import build_menubar
from services.i18n_service import I18nService


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        # ---------------- SERVICES ----------------

        self.config_service = ConfigService()
        self.config = self.config_service  # alias pour le code existant
        self.blueprints = BlueprintService()
        self.scim = ScimService()
        self.updater = UpdateService()
        self.ping = PingService()

        # ---------------- I18N ----------------

        self.i18n = I18nService(self.config_service.get_lang())
        self.t = self.i18n.t

        # Menubar APRÈS i18n
        build_menubar(self)

        self.ping.send(self.config_service.get_id())

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
        folder = self.config_service.get_game_folder()

        if not folder or folder == "undefined":

            default = get_blueprints_base()

            folder = filedialog.askdirectory(
                initialdir=default,
                title=self.t("filedialog_select_folder")
            )

            if not folder:
                return

            self.config_service.set_game_folder(folder)

        bps = self.blueprints.list_blueprints(folder)
        self.main.render_blueprints(bps)

        if hasattr(self.sidebar, "dropdown"):
            self.sidebar.dropdown.set(os.path.basename(folder))

    def delete_blueprint(self, name):
        folder = self.config_service.get_game_folder()

        if messagebox.askyesno(
            self.t("confirm_delete"),
            self.t("confirm_delete_long")
        ):
            self.blueprints.delete_blueprint(folder, name)
            self.load_blueprints()

    def upload_blueprints(self):

        files = filedialog.askopenfilenames(
            title=self.t("upload_blueprint"),
            filetypes=[(self.t("sbp_files"), "*.sbp")]
        )

        if not files:
            return

        folder = self.config_service.get_game_folder()

        if not self.blueprints.check_sbpcfg_exists(files):
            messagebox.showerror(self.t("error"), self.t("error_no_sbpcfg"))
            return

        if not self.blueprints.check_duplicates(files, folder):
            messagebox.showerror(self.t("error"), self.t("error_already_same_bp"))
            return

        self.blueprints.upload_blueprints(files, folder)
        self.load_blueprints()

        messagebox.showinfo(
            self.t("blueprint_added"),
            self.t("blueprint_added_long")
        )

    # ======================================================
    # SCIM
    # ======================================================

    def open_scim(self):
        ScimWindow(self)

    def download_scim(self, blueprint_id, title):

        folder = self.config_service.get_game_folder()

        try:
            name = self.scim.download_blueprint(blueprint_id, title, folder)

            messagebox.showinfo(
                self.t("download_successful"),
                self.t("download_successful_long", title=name)
            )

            self.load_blueprints()

        except Exception as e:
            messagebox.showerror(
                self.t("error"),
                self.t("download_failure_long", error=str(e))
            )

    # ======================================================
    # UPDATE
    # ======================================================

    def check_update(self):
        ok, remote, url, error = self.updater.check_for_update(BUILD_NUMBER)

        if error:
            return

        if not ok:
            messagebox.showinfo(
                self.t("update_available"),
                f"{self.t('new_version_available')} : {remote}\n{self.t('download_here')} : {url}"
            )
