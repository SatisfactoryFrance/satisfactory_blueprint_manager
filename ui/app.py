import os
import customtkinter as ctk
from tkinter import messagebox, filedialog
import ctypes
import sys
from PIL import Image, ImageTk

from ui.sidebar import Sidebar
from ui.main_window import MainWindow
from ui.scim_window import ScimWindow

from core.config import ConfigService
from services.blueprint_service import BlueprintService
from services.scim_service import ScimService
from services.update_service import UpdateService
from services.ping_service import PingService
from services.save_service import SaveService
from services.auto_update_service import AutoUpdateService

from core.version import BUILD_NUMBER
from core.paths import get_blueprints_base
from core.version import CHANNEL


from ui.menubar import build_menubar
from services.i18n_service import I18nService

from utils.threads import run_bg


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        if getattr(sys, 'frozen', False):
            os.chdir(os.path.dirname(sys.executable))

       # ---------------- ICON ----------------

        #la, on va attacher l'icone à la fenêtre, et aussi à la barre des tâches sous Windows
        icon_path = os.path.join(os.getcwd(), "icone.ico")  # Chemin vers .ico
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        else:
            print("Icône introuvable")

        # Forcer l'icône dans la barre des tâches (uniquement sous Windows)
        if os.name == "nt":  # Vérifie que le système est Windows
            app_id = "Satisfactory blueprint Manager"  # Identifiant unique pour votre application
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            self.iconbitmap(icon_path)  # Appliquer l'icône

        # ---------------- SERVICES ----------------

        self.config_service = ConfigService()
        self.config = self.config_service  # alias pour le code existant
        self.blueprints = BlueprintService()
        self.scim = ScimService()
        self.updater = UpdateService()
        self.auto_updater = AutoUpdateService(self)
        self.ping = PingService()
        self.saves = SaveService(self.config_service)

        # ---------------- I18N ----------------

        self.i18n = I18nService(self.config_service.get_lang())
        self.t = self.i18n.t

        print("LANG START =", self.config_service.get_lang())
        print("DELETE =", self.t("delete"))

        # Menubar APRÈS i18n
        build_menubar(self)

        self.ping.send(self.config_service.get_id())

        # ---------------- UI ----------------

        self.title(f"Satisfactory Blueprint Manager - {BUILD_NUMBER} ({CHANNEL.upper()})")
        self.center_window(1200, 600)

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

        # ouverture dossier courant
        ctk.CTkButton(
            header,
            text="📂",
            width=40,
            command=self.open_current_folder
        ).pack(side="left", padx=6)

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

        # self.refresh_saves_dropdown(keep_selection=True)

        # ---------------- Startup ----------------

        self._focus_refresh_job = None
        self.bind("<FocusIn>", self._on_focus_in)

        # Main window
        self.main = MainWindow(self)
        self.main.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_saves_dropdown(keep_selection=True)

        self.load_blueprints()

        self.check_update()

    # ======================================================
    # BLUEPRINTS
    # ======================================================

    def load_blueprints(self):

        base_path = get_blueprints_base()

        # 🚨 Cas : aucun dossier blueprint global n'existe
        if not os.path.isdir(base_path):
            self.show_no_blueprint_folder_popup()
            return

        folder = self.config_service.get_game_folder()

        # ✅ Si le dossier mémorisé n'existe plus, on reset proprement
        if folder and folder != "undefined" and not os.path.isdir(folder):
            old = folder
            self.config_service.set_game_folder("undefined")

            # UI: on remet un texte neutre dans le dropdown (évite “valeur fantôme”)
            if hasattr(self, "save_selector"):
                self.save_selector.set(self.t("select_save"))

            # UI: état vide
            self.main.render_blueprints([])
            self.bp_count_label.configure(text="0 BP")

            self.show_missing_folder_popup(old)
            return

        if not folder or folder == "undefined":

            saves = self.saves.list_saves()

            if saves:
                # 🔥 Sélection automatique du premier dossier
                first_save = saves[0]

                self.saves.set_current(first_save)

                # Sync dropdown proprement
                self.refresh_saves_dropdown(keep_selection=False)
                self.save_selector.set(first_save)

                folder = self.config_service.get_game_folder()

            else:
                # Aucun dossier blueprint existant
                self.show_no_blueprint_folder_popup()
                return

        # Affiche immédiatement un état de chargement
        self.main.show_loading(self.t("loading_blueprints"))

        def work():
            return self.blueprints.list_blueprints(folder)

        def done(bps):
            self.main.hide_loading()
            self.main.render_blueprints(bps)
            self.bp_count_label.configure(text=f"{len(bps)} BP")

        run_bg(work, done, self)

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

        # 🔐 Sécurité : dossier disparu / non défini
        if not folder or folder == "undefined" or not os.path.isdir(folder):
            messagebox.showerror(self.t("error"), self.t("folder_not_set"))
            self.load_blueprints()
            return

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
    # ouverture fenetre SCIM
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

    def check_update(self, manual=False):
        ok, remote, url, error = self.updater.check_for_update(BUILD_NUMBER,CHANNEL)

        if error:
            if manual:
                messagebox.showerror(self.t("error"), error)
            return

        if not ok and remote and url:
            self.show_update_popup(remote, url)
        else:
            if manual:
                messagebox.showinfo(
                    self.t("update_available"),
                    self.t("no_update_available")
                )

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

            try:
                win.destroy()

                confirm = messagebox.askyesno(
                    self.t("update_available"),
                    self.t("update_confirm")
                )

                if not confirm:
                    return

                # lancement auto update
                self.auto_updater.download_and_apply(url)

            except Exception as e:
                messagebox.showerror(self.t("error"), str(e))

        ctk.CTkButton(
            btns,
            text=f"{self.t('download')} ({version})",
            width=140,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=download
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btns,
            text=self.t("later"),
            width=120,
            fg_color="#374151",
            hover_color="#4b5563",
            command=win.destroy
        ).pack(side="left", padx=10)

    # ======================================================
    # load bp
    # ======================================================

    def on_save_changed(self, name):

        # 🔄 resync avec le disque avant d'accepter la sélection
        existing = self.saves.list_saves()

        if name not in existing:
            # le dossier a été supprimé entre temps
            self.refresh_saves_dropdown(keep_selection=False)

            # état UI cohérent
            self.main.render_blueprints([])
            self.bp_count_label.configure(text="0 BP")

            self.show_missing_folder_popup(name)
            return

        if self.saves.set_current(name):
            # optionnel : resync pour retirer d’éventuels dossiers supprimés
            self.refresh_saves_dropdown(keep_selection=True)
            self.load_blueprints()

    # ======================================================
    # Ouverture du dossier courant
    # ======================================================

    def open_current_folder(self):

        folder = self.config_service.get_game_folder()

        if not folder or folder == "undefined":
            return

        try:
            os.startfile(folder)   # Windows
        except Exception as e:
            messagebox.showerror(self.t("error"), str(e))

    # ======================================================
    # CENTRAGE FENETRE
    # ======================================================

    def center_window(self, width=1200, height=600):
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    # ======================================================
    # FENETRE DE DOSSIER MANQUANT 
    # ======================================================

    def show_missing_folder_popup(self, missing_path):

        win = ctk.CTkToplevel(self)
        win.title(self.t("error"))
        win.geometry("480x220")
        win.transient(self)
        win.grab_set()
        win.lift()
        win.focus_force()

        # centrer
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - 240
        y = (win.winfo_screenheight() // 2) - 110
        win.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(win, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="📁",
            font=ctk.CTkFont(size=28)
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            frame,
            text=self.t("folder_missing_reset", folder=missing_path),
            wraplength=420,
            justify="center"
        ).pack(pady=(0, 15))

        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.pack()

        def choose_folder():
            default = get_blueprints_base()
            folder = filedialog.askdirectory(
                initialdir=default,
                title=self.t("filedialog_select_folder")
            )

            if folder:
                self.config_service.set_game_folder(folder)
                win.destroy()
                self.load_blueprints()

        ctk.CTkButton(
            btns,
            text=self.t("filedialog_select_folder"),
            width=180,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=choose_folder
        ).pack(side="left", padx=10)
        '''
        ctk.CTkButton(
            btns,
            text=self.t("quit"),
            width=120,
            fg_color="#374151",
            hover_color="#4b5563",
            command=win.destroy
        ).pack(side="left", padx=10)
        '''

    # ======================================================
    # Droplist des saves
    # ======================================================

    def refresh_saves_dropdown(self, keep_selection=True):
        folders = self.saves.list_saves()
        if not folders:
            folders = [self.t("select_save")]

        self.save_selector.configure(values=folders)

        # 👉 Au lieu d'utiliser la valeur actuelle du widget,
        # on utilise la save réellement active
        current = self.saves.get_current()

        if current and current in folders:
            self.save_selector.set(current)
        else:
            self.save_selector.set(self.t("select_save"))

    def _on_focus_in(self, event=None):
        if self._focus_refresh_job:
            self.after_cancel(self._focus_refresh_job)

        self._focus_refresh_job = self.after(300, self._do_focus_refresh)

    def _do_focus_refresh(self):
        self._focus_refresh_job = None

        previous = self.saves.get_current()
        existing = self.saves.list_saves()

        self.refresh_saves_dropdown(keep_selection=True)

        if previous and previous not in existing:
            self.config_service.set_game_folder("undefined")
            self.load_blueprints()

    def show_no_blueprint_folder_popup(self):

        win = ctk.CTkToplevel(self)
        win.title(self.t("no_bp_title"))
        win.geometry("520x260")
        win.transient(self)
        win.grab_set()
        win.lift()
        win.focus_force()
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - 260
        y = (win.winfo_screenheight() // 2) - 130
        win.geometry(f"+{x}+{y}")

        # empêcher fermeture via X
        win.protocol("WM_DELETE_WINDOW", lambda: None)

        frame = ctk.CTkFrame(win, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="⚠️ " + self.t("no_bp_header"),
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            frame,
            text=self.t("no_bp_message"),
            wraplength=460,
            justify="center"
        ).pack(pady=(0, 20))

        ctk.CTkButton(
            frame,
            text=self.t("quit"),
            width=200,
            fg_color="#b91c1c",
            hover_color="#991b1b",
            command=self.destroy
        ).pack()
