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
from services.save_service import SaveService

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
        self.saves = SaveService(self.config_service)

        # ---------------- I18N ----------------

        self.i18n = I18nService(self.config_service.get_lang())
        self.t = self.i18n.t

        # Menubar APRÈS i18n
        build_menubar(self)

        self.ping.send(self.config_service.get_id())

        # ---------------- UI ----------------

        self.title(f"Satisfactory Blueprint Manager - {BUILD_NUMBER}")
        self.geometry("1200x600")

# ================= HEADER =================

        header = ctk.CTkFrame(self, fg_color="#1b2838", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        self.save_selector = ctk.CTkOptionMenu(
            header,
            values=["Chargement..."],
            width=260,
            command=self.on_save_changed
        )
        self.save_selector.pack(side="left", padx=10)

        # On compte le nombre de BP et on l'affiche dans une petite étiquette
        self.bp_count_label = ctk.CTkLabel(
            header,
            text="0",
            fg_color="#1f2937",
            text_color="#60a5fa",
            corner_radius=12,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=36
            )
        self.bp_count_label.pack(side="left", padx=(5, 15))

        # Add blueprints
        ctk.CTkButton(
            header,
            text=self.t("add_blueprints"),
            width=170,
            command=self.upload_blueprints
        ).pack(side="left", padx=6)

        # Open SCIM
        ctk.CTkButton(
            header,
            text=self.t("open_scim"),
            width=240,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=self.open_scim
        ).pack(side="right", padx=6)

        # self.sidebar = Sidebar(self)
        # self.sidebar.pack(side="top", fill="x")

        # -------- Populate saves --------

        folders = self.saves.list_saves()

        if not folders:
            folders = [self.t("select_save")]

        self.save_selector.configure(values=folders)

        current = self.saves.get_current()
        if current:
            self.save_selector.set(current)

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
        self.bp_count_label.configure(text=f"{len(bps)} BP")

#        if hasattr(self.sidebar, "dropdown"):
#            self.sidebar.dropdown.set(os.path.basename(folder))

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
            self.show_update_popup(remote, url)

    def show_update_popup(self, version, url):
        import webbrowser

        win = ctk.CTkToplevel(self)
        win.title(self.t("update_available"))
        win.geometry("420x200")
        win.transient(self)
        win.grab_set()
        win.lift()
        win.focus_force()

        # centrer
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - 210
        y = (win.winfo_screenheight() // 2) - 100
        win.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(win, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text=self.t("new_version_available") + f" : {version}",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            frame,
            text=self.t("download_here"),
            text_color="#9aa7b2"
        ).pack(pady=(0, 15))

        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.pack()

        def download():
            webbrowser.open(url)
            win.destroy()

        ctk.CTkButton(
            btns,
            text=self.t("download"),
            width=140,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=download
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btns,
            text="Plus tard",
            width=120,
            fg_color="#374151",
            hover_color="#4b5563",
            command=win.destroy
        ).pack(side="left", padx=10)

    # ======================================================
    # load bp
    # ======================================================

    def on_save_changed(self, name):

        if self.saves.set_current(name):
            self.load_blueprints()
