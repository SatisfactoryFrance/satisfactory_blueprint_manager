from backend import Backend
import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu, Toplevel, Text, StringVar
from customtkinter import CTkImage
import webbrowser
import os
import threading
import io
import textwrap
from bs4 import BeautifulSoup
import requests
from PIL import Image
import i18n

BUILD_NUMBER = "v1.1.2"


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.rowconfigure(1, weight=1)
        self.backend = Backend()

        # Charger les dossiers blueprints disponibles
        self.blueprint_folders = self.backend.get_blueprint_folders()
        self.selected_blueprint_folder = StringVar(value=self.blueprint_folders[0] if self.blueprint_folders else "")

        # Ajouter un menu déroulant pour sélectionner un dossier de blueprints
        self.dropdown_game_folder = ctk.CTkOptionMenu(
            self,
            values=self.blueprint_folders,
            variable=self.selected_blueprint_folder,
            command=self.update_game_folder
        )
        self.dropdown_game_folder.grid(column=0, row=0, padx=10, pady=5)

    def update_game_folder(self, selected_folder):
        """Met à jour le dossier de blueprints sélectionné."""
        chemin_base = os.path.join(os.getenv("LOCALAPPDATA"), "FactoryGame", "Saved", "SaveGames", "blueprints")
        game_folder_path = os.path.join(chemin_base, selected_folder)
        self.winfo_toplevel().backend.set_config(title='game_folder', new_value=game_folder_path)

        # on refresh la liste :
        self.update_blueprints()

    def update_blueprints(self):
        """Met à jour la liste des blueprints dans la fenêtre principale."""
        self.winfo_toplevel().load_blueprints()

        # On remonte en haut de la liste au changement de dossier
        self.winfo_toplevel().main_window.bp_list._parent_canvas.yview_moveto(0)


class MainWindow(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weigh=10)

        self.button_add_bp = ctk.CTkButton(
            self,
            text=self.winfo_toplevel().i18n.t('add_blueprints'),
            width=250,
            fg_color="#307C39",
            hover_color="#245E2B",
            command=self.winfo_toplevel().add_blueprint_button_callback
        )

        self.button_add_bp.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="n"
        )

        self.button_open_scim = ctk.CTkButton(
            self,
            text=self.winfo_toplevel().i18n.t('open_scim'),
            width=250,
            command=self.winfo_toplevel().open_scim_button_callback
        )

        self.button_open_scim.grid(
            row=0,
            column=1,
            padx=20,
            pady=20,
            sticky="n"
        )

        self.bp_list = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.bp_list.grid(
            columnspan=2,
            row=1,
            sticky="nsew"
        )


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.backend = Backend()

        # Chemin attendu pour le dossier blueprints
        chemin_blueprints = os.path.join(os.getenv("LOCALAPPDATA"), "FactoryGame", "Saved", "SaveGames", "blueprints")

        self.backend.check_config_file()
        stored_lang = self.backend.config['lang']

        self.current_lang = stored_lang
        if self.current_lang == 'fr':
            self.lang_fr = StringVar(value='1')
            self.lang_en = StringVar(value='0')
        else:
            self.lang_fr = StringVar(value='0')
            self.lang_en = StringVar(value='1')

        # Vérification de l'existence du dossier blueprints
        if not os.path.exists(chemin_blueprints):
            messagebox.showerror(self.i18n.t('error'), self.i18n.t('no_bp_folder'))
            self.destroy()
            return  # Arrête l'initialisation

        self.current_site_page = 1

        self.i18n = i18n

        self.i18n.load_path.append('locale')
        self.i18n.set('file_format', 'json')
        self.i18n.set('locale', str(self.current_lang))
        self.i18n.set('fallback', 'en')
        self.i18n.set('filename_format', '{locale}.{format}')
        self.i18n.set('skip_locale_root_data', True)

        # Menu
        menubar = Menu(self)
        self.config(menu=menubar)
        menufichier = Menu(menubar, tearoff=0)
        menufichier.add_command(label=self.i18n.t('quit'), command=self.quit)
        menubar.add_cascade(label=self.i18n.t('menu_file'), menu=menufichier)

        menulang = Menu(menubar, tearoff=0)
        menulang.add_checkbutton(label=self.i18n.t('menu_fr'), variable=self.lang_fr, onvalue='1', offvalue='0', command=self.set_lang_to_fr)
        menulang.add_checkbutton(label=self.i18n.t('menu_en'), variable=self.lang_en, onvalue='1', offvalue='0', command=self.set_lang_to_en)
        menubar.add_cascade(label=self.i18n.t('menu_lang'), menu=menulang)

        # Menu Liens Utiles
        links_menu = Menu(menubar, tearoff=0)
        links_menu.add_command(label="Site Satisfactory FR", command=lambda: self.open_link("https://satisfactoryfr.com"))
        links_menu.add_command(label="Site Satisfactory EN", command=lambda: self.open_link("https://satisfactorygame.com"))
        links_menu.add_command(label="Discord FR", command=lambda: self.open_link("https://discord.gg/satisfactoryfr"))
        links_menu.add_command(label="Discord EN", command=lambda: self.open_link("https://discord.gg/satisfactory"))
        links_menu.add_command(label="Site S.B.M.", command=lambda: self.open_link("https://sbm.satisfactoryfr.com"))
        links_menu.add_command(label="Blueprints SCIM", command=lambda: self.open_link("https://satisfactory-calculator.com/fr/blueprints"))

        menubar.add_cascade(label=self.i18n.t('useful_links'), menu=links_menu)

        # Menu Aide
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label=self.i18n.t('menu_howitisworking'), command=self.show_help)
        help_menu.add_command(label=self.i18n.t('menu_about'), command=self.show_about)
        menubar.add_cascade(label=self.i18n.t('menu_help'), menu=help_menu)

        # Appearance
        ctk.set_appearance_mode('dark')
        self.title(f'Satisfactory Blueprint Manager - {BUILD_NUMBER}')
        self.geometry('1200x600')
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)

        # Fonts
        self.title_font = ctk.CTkFont(
            family="Arial",
            size=40,
            weight='bold'
        )
        self.body_font = ctk.CTkFont(
            family="Helvetica",
            size=16
        )
        self.button_font = ctk.CTkFont(
            family="Helvetica",
            size=13
        )

        # Sidebar
        self.sidebar = Sidebar(self, fg_color="transparent")
        self.sidebar.grid(
            column=0,
            columnspan=2,
            row=0,
            padx=0,
            pady=0,
            sticky="nsew",
        )

        self.main_window = MainWindow(self, fg_color="transparent")
        self.main_window.grid(
            column=1,
            row=1,
            padx=0,
            pady=0,
            sticky="nsew",
        )

        game_folder_data = self.backend.config['game_folder']
        if game_folder_data != 'undefined':
            self.load_blueprints()

        self.main_window.bp_list.bind("<MouseWheel>", self.scroll_main_window)

    # Définir la méthode avant l'utilisation
    def scroll_scim_window(self, event):
        """Gère le défilement dans la fenêtre SCIM."""
        try:
            if event.delta < 0:
                self.canvas.yview_scroll(1, "units")  # Scroll down
            else:
                self.canvas.yview_scroll(-1, "units")  # Scroll up
        except Exception as e:
            print(f"Erreur lors du défilement dans la fenêtre SCIM : {e}")

    def add_blueprint_button_callback(self):
        game_folder_data = self.backend.config['game_folder']
        if game_folder_data is None:
            messagebox.showerror(self.i18n.t('error'), self.i18n.t('folder_not_set'))
        else:
            q = filedialog.askopenfilenames(
                title=self.i18n.t('upload_blueprint'),
                filetypes=[(self.i18n.t('sbp_files'), "*.sbp")],
            )

            if q:
                if not self.backend.check_blueprints_cbpcfg(q):
                    messagebox.showerror(self.i18n.t('error'), self.i18n.t('error_no_sbpcfg'))
                elif not self.backend.check_if_same_blueprints(q):
                    messagebox.showerror(self.i18n.t('error'), self.i18n.t('error_already_same_bp'))
                else:
                    self.backend.upload_blueprints(q)
                    self.load_blueprints()
                    messagebox.showinfo(self.i18n.t('blueprint_added'), self.i18n.t('blueprint_added_long'))

    # ON PASSE SUR L'OUVERTURE DE LA FENETRE BP DE SCIM

    def open_scim_button_callback(self):
        blueprint_window = ctk.CTkToplevel(self)
        blueprint_window.title(self.i18n.t('title_scim_windows'))
        blueprint_window.geometry("1600x700")
        blueprint_window.resizable(False, True)
        blueprint_window.transient(self)
        blueprint_window.lift()

        # blueprint_window.focus_force()

        # Cadre pour afficher la liste des blueprints
        self.canvas = ctk.CTkCanvas(blueprint_window, bg="#2f2f2f", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(blueprint_window, orientation="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set, background='#323232', highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Lier la molette de la souris au canvas dans la fenêtre SCIM
        blueprint_window.bind("<MouseWheel>", self.scroll_scim_window)

        # Cadre de navigation pour la pagination (inchangé)
        nav_frame = ctk.CTkFrame(blueprint_window)
        nav_frame.grid(row=1, column=0, sticky="ew")

        nav_frame.columnconfigure(0, weight=1)
        nav_frame.columnconfigure(1, weight=0)
        nav_frame.columnconfigure(2, weight=1)
        nav_frame.rowconfigure(0, weight=1)

        prev_button = ctk.CTkButton(nav_frame, text=self.i18n.t('previous'), command=self.prev_site_page)
        prev_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.page_label = ctk.CTkLabel(nav_frame, text=f"Page {self.current_site_page}")
        self.page_label.grid(row=0, column=1, padx=10, pady=10)

        next_button = ctk.CTkButton(nav_frame, text=self.i18n.t('next'), command=self.next_site_page)
        next_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        blueprint_window.grid_rowconfigure(0, weight=1)
        blueprint_window.grid_columnconfigure(0, weight=1)

        # Afficher un message "Téléchargement en cours"
        self.loading_label = ctk.CTkLabel(self.scrollable_frame, text=self.i18n.t('download_in_progress'))
        self.loading_label.pack(pady=20)

        # Utiliser un thread pour charger les blueprints
        threading.Thread(target=self.load_scim_blueprints, args=(self.current_site_page,), daemon=True).start()

    def bind_scim_mousewheel(self, blueprint_window):
        """Lier la molette de la souris au défilement dans la fenêtre SCIM."""
        blueprint_window.bind_all("<MouseWheel>", self.scroll_scim_window)

    def scroll_main_window(self, event):
        """Gère le défilement dans la fenêtre principale."""
        try:
            if event.delta < 0:
                self.main_window.bp_list._parent_canvas.yview_scroll(1, "units")  # Scroll down
            else:
                self.main_window.bp_list._parent_canvas.yview_scroll(-1, "units")  # Scroll up
        except Exception as e:
            print(f"Erreur lors du défilement de la fenêtre principale : {e}")

    # ON PASSE SUR LE LOAD BP DE SCIM

    def load_scim_blueprints(self, site_page):
        """Charge les blueprints depuis la page spécifiée du site"""
        # Efface les éléments précédents dans le cadre
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Mettre à jour le label de numéro de page
        self.page_label.configure(text=f"Page {site_page}")

        # On remonte en haut de la fenetre pour afficher les BP après un changement de page
        self.canvas.after(100, lambda: self.canvas.yview_moveto(0))

        # Construire l'URL pour la page actuelle
        url = f"https://satisfactory-calculator.com/fr/blueprints/index/index/p/{site_page}"

        # Récupération des données des blueprints
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        blueprint_items = soup.find_all("div", class_="card-body")

        # Afficher les blueprints pour la page actuelle du site
        for item in blueprint_items:
            # Récupération du lien, de l'image, du titre et de l'ID du blueprint
            link = item.find("a", href=True)
            if link is None:
                continue

            # Récupération du titre dans <h6><strong>
            h6_tag = item.find("h6")
            title_tag = h6_tag.find("strong") if h6_tag else None
            title = title_tag.get_text(strip=True) if title_tag else "Sans Titre"

            # Récupération de l'ID dans le href
            href = link.get("href", "")
            blueprint_id = href.split("/id/")[1].split("/")[0] if "/id/" in href else None
            if not blueprint_id:
                continue

            # Récupération de l'URL de l'image dans <img>
            image_tag = link.find("img")
            image_url = image_tag["src"] if image_tag and "src" in image_tag.attrs else None
            if not image_url:
                continue

            # Récupérer la description courte du blueprint
            description = self.get_blueprint_description(blueprint_id)

            # Téléchargement de l'image
            try:
                img_data = requests.get(image_url).content
                img = Image.open(io.BytesIO(img_data))
                ctk_img = CTkImage(img, size=(200, 83.3))
            except Exception as e:
                print(f"Erreur lors du téléchargement de l'image : {e}")
                continue

            # Affichage de l'image et du titre dans le cadre
            frame = ctk.CTkFrame(self.scrollable_frame)
            frame.pack(fill="x", pady=5)

            img_label = ctk.CTkLabel(frame, image=ctk_img, text=None)
            img_label.pack(side="left")

            title_label = ctk.CTkLabel(frame, width=300, text=title, font=("Arial", 12, "bold"), cursor="hand2", wraplength=280)
            title_label.pack(side="left", padx=10)

            # on chope l'url de la page du BP
            blueprint_url = f"https://satisfactory-calculator.com/fr/blueprints/index/details/id/{blueprint_id}"
            title_label.bind("<Button-1>", lambda e, url=blueprint_url: webbrowser.open(url))

            # Ajouter la description sous le titre
            desc_label = ctk.CTkLabel(frame, text=description, font=("Arial", 10), width=750, wraplength=870, justify="left")
            desc_label.pack(side="left", padx=10, pady=5)

            download_button = ctk.CTkButton(frame, text=self.i18n.t('download'), command=lambda bid=blueprint_id, t=title: self.download_blueprint(bid, t))
            download_button.pack(side="right", padx=20, pady=5)

    def download_blueprint(self, blueprint_id, title):
        """Télécharge les fichiers .sbp et .sbpcfg pour un blueprint sélectionné"""
        base_url = "https://satisfactory-calculator.com/fr/blueprints/index/download"
        sbp_url = f"{base_url}/id/{blueprint_id}"
        sbpcfg_url = f"{base_url}-cfg/id/{blueprint_id}"

        # On nettoie l'url SCIM si caractères bizarre
        sanitized_title = self.winfo_toplevel().backend.sanitize_filename(title)

        try:
            # Vérification de l'existence des fichiers
            game_folder_data = self.winfo_toplevel().backend.config['game_folder']
            sbp_file_path = os.path.join(game_folder_data, f"{title}.sbp")
            sbpcfg_file_path = os.path.join(game_folder_data, f"{title}.sbpcfg")

            if os.path.exists(sbp_file_path) and os.path.exists(sbpcfg_file_path):
                messagebox.showwarning(
                    self.i18n.t('error'),
                    self.i18n.t('download_failure_long').format(title=title)
                )
                return  # Ne pas procéder au téléchargement si le BP existe déjà

            # Téléchargement des fichiers si non existants
            sbp_response = requests.get(sbp_url)
            sbpcfg_response = requests.get(sbpcfg_url)

            if sbp_response.status_code == 200 and sbpcfg_response.status_code == 200:
                # Sauvegarder les fichiers téléchargés dans le repertoire windows
                download_dir = game_folder_data

                with open(os.path.join(download_dir, f"{sanitized_title}.sbp"), "wb") as f:
                    f.write(sbp_response.content)
                with open(os.path.join(download_dir, f"{sanitized_title}.sbpcfg"), "wb") as f:

                    with open(sbp_file_path, "wb") as f:
                        f.write(sbp_response.content)
                    with open(sbpcfg_file_path, "wb") as f:
                        f.write(sbpcfg_response.content)

                messagebox.showinfo(self.i18n.t('download_successful'), self.i18n.t('download_successful_long', title=sanitized_title))
            else:
                messagebox.showerror(self.i18n.t('error'), self.i18n.t('download_failure'))

        except Exception as e:
            messagebox.showerror(self.i18n.t('error'), self.i18n.t('download_failure_long', error=e))

        self.winfo_toplevel().load_blueprints()

    def next_site_page(self):
        """Affiche la page suivante de blueprints sur le site"""
        self.current_site_page += 1
        self.update_page()

    def prev_site_page(self):
        """Affiche la page précédente de blueprints sur le site"""
        if self.current_site_page > 1:
            self.current_site_page -= 1
            self.update_page()

    def update_page(self):
        """Met à jour la page des blueprints en utilisant un thread"""
        # Effacer le cadre et afficher un message "Téléchargement en cours"
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.loading_label = ctk.CTkLabel(self.scrollable_frame, text="Téléchargement en cours...")
        self.loading_label.pack(pady=20)

        # Utiliser un thread pour charger les blueprints
        threading.Thread(target=self.load_scim_blueprints, args=(self.current_site_page,), daemon=True).start()

    def get_blueprint_description(self, blueprint_id):
        """Récupère et retourne une courte description (150 mots) du blueprint"""
        url = f"https://satisfactory-calculator.com/fr/blueprints/index/details/id/{blueprint_id}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Essayer plusieurs approches pour trouver la description
        description_tag = None

        # 1. Rechercher dans des blockquotes indépendants
        blockquote_tags = soup.find_all("blockquote")
        for blockquote in blockquote_tags:
            if blockquote.get_text(strip=True):  # S'assurer qu'il y a du texte
                description_tag = blockquote
                break

        # 2. Rechercher dans une balise alternative si aucun blockquote ne contient la description
        if not description_tag:
            possible_tags = ["p", "div"]
            for tag in possible_tags:
                description_tag = soup.find(tag, {"class": "description"})  # Ajuster la classe si besoin
                if description_tag and description_tag.get_text(strip=True):
                    break

        # Extraire et limiter la description si trouvée
        if description_tag:
            description = description_tag.get_text(strip=True)
            short_description = " ".join(description.split()[:150]) + "..."
        else:
            # Si rien n'est trouvé, message pour aider à l'inspection
            print("Aucune description trouvée")  # Limite d'affichage à 1000 caractères
            short_description = self.i18n.t('scim_no_description')

        return short_description

    def load_blueprints(self):
        print('Trying to load bp')
        for child in self.main_window.bp_list.winfo_children():
            child.destroy()

        bps = self.backend.list_bp_from_game_folder()

        for i, bp in enumerate(bps):
            bp_file = bp['blueprint']
            bp_file_short = textwrap.shorten(bp_file, width=70, placeholder=" [...]")

            label = ctk.CTkLabel(
                self.main_window.bp_list,
                text=bp_file_short,
                width=250,
                fg_color="transparent",
                font=self.button_font,
            )
            label.grid(
                column=0,
                row=i,
                padx=10,
                pady=5,
                sticky="n",
            )
            button = ctk.CTkButton(
                self.main_window.bp_list,
                text=self.i18n.t('delete'),
                width=150,
                fg_color="red",
                font=self.button_font,
                command=lambda bp_file=bp_file: self.delete_bp(bp_file)
            )
            button.grid(
                column=1,
                row=i,
                padx=10,
                pady=5,
                sticky="n",
            )

    def delete_bp(self, bp_file):
        answer = messagebox.askyesno(title=self.i18n.t('confirm_delete'), message=self.i18n.t('confirm_delete_long'))
        if answer:
            self.backend.delete_bp_from_game_folder(bp_file)
            self.load_blueprints()

    def set_lang_to_fr(self):
        self.lang_en.set(0)
        self.current_lang = 'fr'
        self.i18n.set('locale', 'fr')
        self.backend.set_config(title='lang', new_value='fr')
        messagebox.showinfo("Information", self.i18n.t('switch_lang'))

    def set_lang_to_en(self):
        self.lang_fr.set(0)
        self.current_lang = 'en'
        self.i18n.set('locale', 'en')
        self.backend.set_config(title='lang', new_value='en')
        messagebox.showinfo("Information", self.i18n.t('switch_lang'))

    def show_about(self):
        """Affiche une boîte de dialogue À propos."""
        messagebox.showinfo(self.i18n.t('menu_about'), self.i18n.t('software_aboutsbm'))

    def show_help(self):

        """Affiche une nouvelle fenêtre avec du texte formaté pour expliquer le fonctionnement."""
        help_window = Toplevel(self)
        help_window.title(self.i18n.t('menu_howitisworking'))
        help_window.geometry("500x400")

        # Zone de texte avec scrollbar
        text_widget = Text(help_window, wrap="word", font=("Arial", 10))
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)

        # Ajouter du contenu formaté
        text_widget.insert("1.0", self.i18n.t('software_specs') + "\n\n")

        text_widget.insert("end", self.i18n.t('software_before_anything') + "\n", "bold")
        text_widget.insert("end",  self.i18n.t('software_create_first_blueprint') + "\n\n", "bold")
        text_widget.insert("end", self.i18n.t('software_step_1') + "\n")
        text_widget.insert("end", self.i18n.t('software_step_2') + "\n")
        text_widget.insert("end", self.i18n.t('software_step_3') + "\n")
        text_widget.insert("end", self.i18n.t('software_step_4') + "\n")
        text_widget.insert("end", self.i18n.t('software_step_5') + "\n\n")
        text_widget.insert("end", self.i18n.t('software_additional_options') + "\n", "bold")
        text_widget.insert("end", self.i18n.t('software_local_only') + "\n")
        text_widget.tag_configure("bold", font=("Arial", 12, "bold"))
        text_widget.tag_configure("italic", font=("Arial", 10, "italic"))

        # Rendre le texte non modifiable
        text_widget.config(state="disabled")

    def open_link(self, url):
        webbrowser.open(url)
