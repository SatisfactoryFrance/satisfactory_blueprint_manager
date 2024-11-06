from backend import Backend
import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu, Toplevel, Text, StringVar
from customtkinter import CTkImage
import webbrowser
import os
import threading
import io
from bs4 import BeautifulSoup
import requests
from PIL import Image

BUILD_NUMBER = "v0.15.1"


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.rowconfigure(1, weight=1)

        game_folder_data = self.winfo_toplevel().backend.config['game_folder']
        if game_folder_data is not None:
            self.game_folder = game_folder_data
        else:
            self.game_folder = False

        # Tronquer le chemin pour n'afficher que ce qu'il y a après /SaveGames/
        if self.game_folder:
            chemin_tronque = self.game_folder.split('/SaveGames/', 1)[-1]
        else:
            chemin_tronque = self.winfo_toplevel().lang.txt('label_game_folder_notset_txt')

        txt_label_game_folder = self.winfo_toplevel().lang.txt('label_game_folder')
        self.label_game_folder = ctk.CTkLabel(
            self,
            text="%s : %s" % (txt_label_game_folder, chemin_tronque),
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
        )

        self.label_game_folder.grid(
            column=0,
            row=0,
            padx=10,
            pady=5
        )

        self.button_game_folder = ctk.CTkButton(
            self,
            text=self.winfo_toplevel().lang.txt('button_game_folder_already_set_txt'),
            command=self.winfo_toplevel().game_folder_button_callback
        )

        self.button_game_folder.grid(
            row=0,
            column=1,
            padx=20,
            pady=20
        )

        if game_folder_data:
            self.button_game_folder.configure(text=self.winfo_toplevel().lang.txt('button_game_folder_already_set_txt'))
        else:
            self.label_game_folder.configure(text="%s : %s" % (txt_label_game_folder, self.winfo_toplevel().lang.txt('label_game_folder_notset_txt')))


class MainWindow(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weigh=10)

        self.button_add_bp = ctk.CTkButton(
            self,
            text=self.winfo_toplevel().lang.txt('button_add_bp_txt'),
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
            text=self.winfo_toplevel().lang.txt('button_open_scim_txt'),
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

        self.backend.check_config_file()
        stored_lang = self.backend.config['lang']

        self.current_lang = stored_lang
        if self.current_lang == 'fr':
            self.lang_fr = StringVar(value='1')
            self.lang_en = StringVar(value='0')
        else:
            self.lang_fr = StringVar(value='0')
            self.lang_en = StringVar(value='1')

        self.lang = Lang(self.current_lang)

        self.current_site_page = 1
        # Menu
        menubar = Menu(self)
        self.config(menu=menubar)
        menufichier = Menu(menubar, tearoff=0)
        menufichier.add_command(label=self.lang.txt('menu_change_game_folder'), command=self.game_folder_button_callback)
        menufichier.add_separator()
        menufichier.add_command(label=self.lang.txt('menu_quit'), command=self.quit)
        menubar.add_cascade(label=self.lang.txt('menu_fichier'), menu=menufichier)

        menulang = Menu(menubar, tearoff=0)
        menulang.add_checkbutton(label=self.lang.txt('menu_fr'), variable=self.lang_fr, onvalue='1', offvalue='0', command=self.set_lang_to_fr)
        menulang.add_checkbutton(label=self.lang.txt('menu_en'), variable=self.lang_en, onvalue='1', offvalue='0', command=self.set_lang_to_en)
        menubar.add_cascade(label=self.lang.txt('menu_langue'), menu=menulang)

        # Menu Liens Utiles
        links_menu = Menu(menubar, tearoff=0)
        links_menu.add_command(label="Site Satisfactory FR", command=lambda: self.open_link("https://satisfactoryfr.com"))
        links_menu.add_command(label="Site Satisfactory EN", command=lambda: self.open_link("https://satisfactorygame.com"))
        links_menu.add_command(label="Discord FR", command=lambda: self.open_link("https://discord.gg/satisfactoryfr"))
        links_menu.add_command(label="Discord EN", command=lambda: self.open_link("https://discord.gg/satisfactory"))
        links_menu.add_command(label="Site S.B.M.", command=lambda: self.open_link("https://sbm.satisfactoryfr.com"))
        links_menu.add_command(label="Blueprints SCIM", command=lambda: self.open_link("https://satisfactory-calculator.com/fr/blueprints"))

        menubar.add_cascade(label=self.lang.txt('menu_liens'), menu=links_menu)

        # Menu Aide
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label=self.lang.txt('menu_fonctionnement'), command=self.show_help)
        help_menu.add_command(label=self.lang.txt('menu_about'), command=self.show_about)
        menubar.add_cascade(label=self.lang.txt('menu_help'), menu=help_menu)

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

    def game_folder_button_callback(self):
        chemin_par_defaut = os.path.join(os.getenv("LOCALAPPDATA"), "FactoryGame", "Saved", "SaveGames", "blueprints")
        q = filedialog.askdirectory(initialdir=chemin_par_defaut)

        if q:
            # Tronquer le chemin pour n'afficher que la partie après /SaveGames/
            chemin_tronque = q.split('/SaveGames/', 1)[-1]

            txt_label_game_folder = self.lang.txt('label_game_folder')
            self.sidebar.label_game_folder.configure(text="%s : %s" % (txt_label_game_folder, chemin_tronque))
            self.sidebar.button_game_folder.configure(text=self.lang.txt('button_game_folder_already_set_txt'))

            # Mise à jour dans la configuration
            self.backend.set_config(title='game_folder', new_value=q)
            self.load_blueprints()

    def add_blueprint_button_callback(self):
        game_folder_data = self.backend.config['game_folder']
        if game_folder_data is None:
            messagebox.showerror(self.lang.txt('messagebox_erreur'), self.lang.txt('messagebox_erreur_folder_not_set'))
        else:
            q = filedialog.askopenfilenames(
                title=self.lang.txt('filedialog_ajout_blueprint'),
                filetypes=[("Fichiers SBP", "*.sbp")],
            )

            if q:
                if not self.backend.check_blueprints_cbpcfg(q):
                    messagebox.showerror(self.lang.txt('messagebox_erreur'), self.lang.txt('messagebox_erreur_no_sbpcfg'))
                elif not self.backend.check_if_same_blueprints(q):
                    messagebox.showerror(self.lang.txt('messagebox_erreur'), self.lang.txt('messagebox_erreur_already_same_blueprint'))
                else:
                    self.backend.upload_blueprints(q)
                    self.load_blueprints()
                    messagebox.showinfo(self.lang.txt('messagebox_ajout_reussi'), self.lang.txt('messagebox_txt_ajout_reussi'))

# ON PASSE SUR L'OUVERTURE DE LA FENETRE BP DE SCIM

    def open_scim_button_callback(self):
        blueprint_window = ctk.CTkToplevel(self)
        blueprint_window.title("Liste des Blueprints de Satisfactory Calculator")
        blueprint_window.geometry("1500x700")
        blueprint_window.resizable(True, True)
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

        prev_button = ctk.CTkButton(nav_frame, text="Précédent", command=self.prev_site_page)
        prev_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.page_label = ctk.CTkLabel(nav_frame, text=f"Page {self.current_site_page}")
        self.page_label.grid(row=0, column=1, padx=10, pady=10)

        next_button = ctk.CTkButton(nav_frame, text="Suivant", command=self.next_site_page)
        next_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        blueprint_window.grid_rowconfigure(0, weight=1)
        blueprint_window.grid_columnconfigure(0, weight=1)

        # Afficher un message "Téléchargement en cours"
        self.loading_label = ctk.CTkLabel(self.scrollable_frame, text="Téléchargement en cours...")
        self.loading_label.pack(pady=20)

        # Utiliser un thread pour charger les blueprints
        threading.Thread(target=self.load_scim_blueprints, args=(self.current_site_page,), daemon=True).start()

    def bind_scim_mousewheel(self, blueprint_window):
        """Lier la molette de la souris au défilement dans la fenêtre SCIM."""
        blueprint_window.bind_all("<MouseWheel>", self.scroll_scim_window)

    def scroll_main_window(self, event):
        """Gère le défilement dans la fenêtre principale."""
        try:
            # Simulez le scroll en utilisant un déplacement de la scrollbar (on ajoute ou soustrait pour simuler le mouvement)
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

            title_label = ctk.CTkLabel(frame, width=300, text=title, font=("Arial", 12, "bold"), cursor="hand2")
            title_label.pack(side="left", padx=10)
            title_label.bind("<Button-1>", lambda e, bid=blueprint_id, t=title: self.download_blueprint(bid, t))

            # Ajouter la description sous le titre
            desc_label = ctk.CTkLabel(frame, text=description, font=("Arial", 10), width=950, wraplength=950, justify="left")
            desc_label.pack(side="left", padx=10, pady=5)

    def download_blueprint(self, blueprint_id, title):
        """Télécharge les fichiers .sbp et .sbpcfg pour un blueprint sélectionné"""
        base_url = "https://satisfactory-calculator.com/fr/blueprints/index/download"
        sbp_url = f"{base_url}/id/{blueprint_id}"
        sbpcfg_url = f"{base_url}-cfg/id/{blueprint_id}"

        try:
            # Téléchargement du fichier .sbp
            sbp_response = requests.get(sbp_url)
            sbpcfg_response = requests.get(sbpcfg_url)

            if sbp_response.status_code == 200 and sbpcfg_response.status_code == 200:
                # Sauvegarder les fichiers téléchargés dans le repertoire windows
                download_dir = os.path.join(os.path.expanduser("~"), "Downloads")

                with open(os.path.join(download_dir, f"{title}.sbp"), "wb") as f:
                    f.write(sbp_response.content)
                with open(os.path.join(download_dir, f"{title}.sbpcfg"), "wb") as f:
                    f.write(sbpcfg_response.content)

                messagebox.showinfo("Téléchargement Réussi", f"{title} a été téléchargé avec succès dans le dossier Téléchargements!")
            else:
                messagebox.showerror("Erreur", "Impossible de télécharger les fichiers du blueprint.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue lors du téléchargement : {e}")

        # # Rafraîchir la liste des fichiers dans la source
        # self.load_files()

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
            short_description = "Description non disponible"

        return short_description

    def load_blueprints(self):
        print('Trying to load bp')
        for child in self.main_window.bp_list.winfo_children():
            child.destroy()

        bps = self.backend.list_bp_from_game_folder()

        for i, bp in enumerate(bps):
            bp_file = bp['blueprint']
            label = ctk.CTkLabel(
                self.main_window.bp_list,
                text=bp_file,
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
                text=self.lang.txt('button_supprimer_bp_txt'),
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
        answer = messagebox.askyesno(title=self.lang.txt('messagebox_confirm_delete'), message=self.lang.txt('messagebox_config_delete_txt'))
        if answer:
            self.backend.delete_bp_from_game_folder(bp_file)
            self.load_blueprints()

    def set_lang_to_fr(self):
        self.lang_en.set(0)
        self.current_lang = 'fr'
        self.lang.set_current_lang(self.current_lang)
        self.backend.set_config(title='lang', new_value='fr')
        messagebox.showinfo("Information", self.lang.txt('messagebox_switch_lang'))

    def set_lang_to_en(self):
        self.lang_fr.set(0)
        self.current_lang = 'en'
        self.lang.set_current_lang(self.current_lang)
        self.backend.set_config(title='lang', new_value='en')
        messagebox.showinfo("Information", self.lang.txt('messagebox_switch_lang'))

    def show_about(self):
        """Affiche une boîte de dialogue À propos."""
        messagebox.showinfo("À propos", self.lang.txt('software_aboutsbm'))

    def show_help(self):

        """Affiche une nouvelle fenêtre avec du texte formaté pour expliquer le fonctionnement."""
        help_window = Toplevel(self)
        help_window.title("Comment ça fonctionne ?")
        help_window.geometry("500x400")

        # Zone de texte avec scrollbar
        text_widget = Text(help_window, wrap="word", font=("Arial", 10))
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)

        # Ajouter du contenu formaté
        text_widget.insert("1.0", self.lang.txt('description_software_functionality') + "\n\n")

        # Instructions en gras
        text_widget.insert("end", self.lang.txt('instructions_bold') + "\n", "bold")
        text_widget.insert("end", self.lang.txt('create_first_blueprint') + "\n\n", "bold")
        text_widget.insert("end", self.lang.txt('step_1') + "\n")
        text_widget.insert("end", self.lang.txt('step_2') + "\n")
        text_widget.insert("end", self.lang.txt('step_3') + "\n")
        text_widget.insert("end", self.lang.txt('step_4') + "\n")
        text_widget.insert("end", self.lang.txt('step_5') + "\n\n")

        # Section Options additionnelles en italique
        text_widget.insert("end", self.lang.txt('additional_options') + "\n", "bold")
        text_widget.insert("end", self.lang.txt('local_only_note') + "\n")

        # Configurer les tags de style
        text_widget.tag_configure("bold", font=("Arial", 12, "bold"))
        text_widget.tag_configure("italic", font=("Arial", 10, "italic"))

        # Rendre le texte non modifiable
        text_widget.config(state="disabled")

    def open_link(self, url):
        webbrowser.open(url)


class Lang():
    def __init__(self, current_lang):
        self.current_lang = current_lang

    def set_current_lang(self, current_lang):
        print('Setting current lang to %s' % current_lang)
        self.current_lang = current_lang

    def txt(self, txt):
        match txt:
            case 'button_game_folder_already_set_txt':
                ret = 'Changer' if self.current_lang == 'fr' else 'Change'
            case 'button_add_bp_txt':
                ret = 'Ajouter des blueprints' if self.current_lang == 'fr' else 'Add blueprints'
            case 'button_supprimer_bp_txt':
                ret = 'Supprimer' if self.current_lang == 'fr' else 'Delete'
            case 'label_game_folder':
                ret = 'Dossier actif' if self.current_lang == 'fr' else 'Active folder'
            case 'label_game_folder_notset_txt':
                ret = 'non défini' if self.current_lang == 'fr' else 'undefined'
            case 'messagebox_switch_lang':
                ret = 'Veuillez redémarrer Satisfactory Blueprint Manager pour prendre en compte le changement de langue' if self.current_lang == 'fr' else 'Please restart Satisfactory Blueprint Manager in order to switch language'
            case 'messagebox_erreur':
                ret = 'Erreur' if self.current_lang == 'fr' else 'Error'
            case 'messagebox_erreur_already_same_blueprint':
                ret = 'Erreur : ce blueprint existe déjà dans votre sauvegarde' if self.current_lang == 'fr' else 'Error : this blueprint already exists in your save'
            case 'messagebox_confirm_delete':
                ret = 'Confirmation de suppression' if self.current_lang == 'fr' else 'Please confirm'
            case 'messagebox_config_delete_txt':
                ret = 'Etes-vous sur de supprimer ce blueprint ? Cette action est irrémédiable' if self.current_lang == 'fr' else 'Are you sure to delete this blueprint ? This action cannot be undone'
            case 'messagebox_erreur_folder_not_set':
                ret = 'Veuillez tout d\'abord sélectionner le dossier des blueprint de votre save' if self.current_lang == 'fr' else 'Please select first the blueprint\'s folder'
            case 'messagebox_erreur_no_sbpcfg':
                ret = 'Un blueprint se compose de 2 fichiers : un fichier sbp, et un fichier sbpcfg. Les 2 doivent etre dans le meme dossier' if self.current_lang == 'fr' else 'A blueprint must be a sbp file and a sbpcfg file. The two files need to be next to each other'
            case 'messagebox_ajout_reussi':
                ret = 'Blueprints ajoutés' if self.current_lang == 'fr' else 'Blueprints successfully added'
            case 'messagebox_txt_ajout_reussi':
                ret = 'Le ou les blueprints sélectionnés ont été ajoutés' if self.current_lang == 'fr' else 'The selected blueprints were successfully added'
            case 'filedialog_ajout_blueprint':
                ret = 'Choisissez le ou les fichiers sbp' if self.current_lang == 'fr' else 'Choose one of multiple sbp files'
            case 'menu_change_game_folder':
                ret = 'Choisir/changer le répertoire des blueprints' if self.current_lang == 'fr' else 'Modify blueprint\'s folder'
            case 'menu_quit':
                ret = 'Quitter' if self.current_lang == 'fr' else 'Quit'
            case 'menu_fichier':
                ret = 'Fichier' if self.current_lang == 'fr' else 'File'
            case 'menu_langue':
                ret = 'Langue' if self.current_lang == 'fr' else 'Language'
            case 'menu_liens':
                ret = 'Liens utiles' if self.current_lang == 'fr' else 'Useful links'
            case 'menu_fonctionnement':
                ret = 'Comment ça fonctionne ?' if self.current_lang == 'fr' else 'How is it working ?'
            case 'menu_about':
                ret = 'A propos' if self.current_lang == 'fr' else 'About'
            case 'menu_help':
                ret = 'Aide' if self.current_lang == 'fr' else 'Help'
            case 'menu_fr':
                ret = 'FR (Français)' if self.current_lang == 'fr' else 'FR (French)'
            case 'menu_en':
                ret = 'EN (Anglais)' if self.current_lang == 'fr' else 'EN (English)'
            case 'description_software_functionality':
                ret = 'Ce logiciel permet de gérer et déplacer des blueprints (plans) entre un répertoire source et un répertoire cible.' if self.current_lang == 'fr' else 'This software allows you to manage and move blueprints between a source directory and a target directory.'
            case 'software_aboutsbm':
                ret = 'Satisfactory Blueprint Manager\nCréé par Je0ffrey & Amorcage pour la communauté Satisfactory France.' if self.current_lang == 'fr' else 'Satisfactory Blueprint Manager\nCreated by Je0ffrey & Amorcage from Satisfactory France and Satisfactory community around the world.'
            case 'description_software_functionality':
                ret = 'Ce logiciel permet de gérer et déplacer des blueprints (plans) entre un répertoire source et un répertoire cible.' if self.current_lang == 'fr' else 'This software allows you to manage and move blueprints (plans) between a source directory and a target directory.'
            case 'instructions_bold':
                ret = 'AVANT TOUT :' if self.current_lang == 'fr' else 'BEFORE ANYTHING:'
            case 'create_first_blueprint':
                ret = 'Vous devez créer un premier blueprint dans le jeu et l\'enregistrer afin de créer le repertoire de votre partie :' if self.current_lang == 'fr' else 'You must create a first blueprint in the game and save it to create your game directory:'
            case 'step_1':
                ret = '1. Ajoutez le repertoire de Blueprint de votre partie depuis le menu ou via le bouton approprié. L\'option est pré-configuré pour aller dans le repertoire racine des blueprint. A vous de choisir votre nom de partie' if self.current_lang == 'fr' else '1. Add your game\'s Blueprint directory from the menu or via the appropriate button. The option is pre-configured to go to the root directory of the blueprints. It\'s up to you to choose your game name'
            case 'step_2':
                ret = '2. La fenêtre se met à jour automatiquement avec les BP déjà présents' if self.current_lang == 'fr' else '2. The window automatically updates with the BPs already present'
            case 'step_3':
                ret = '3. Sélectionnez les fichiers depuis le bouton AJOUTER DES BLUEPRINTS dans vos repertoires de téléchargements. la recherche n\'affiche que les fichiers .sbp et prend automatiquement le fichier .sbpcfg en même temps' if self.current_lang == 'fr' else '3. Select the files from the ADD BLUEPRINTS button in your downloads directories. The search only displays .sbp files and automatically takes the .sbpcfg file at the same time.'
            case 'step_4':
                ret = '4. Une fenetre d\'information vous indique sur le transfert s\'est bien passé ou non.' if self.current_lang == 'fr' else '4. An information window will tell you whether the transfer went well or not.'
            case 'step_5':
                ret = '5. Vous pouvez utiliser le bouton SUPPRIMER pour supprimer les BP de votre partie.' if self.current_lang == 'fr' else '5. You can use the DELETE button to remove BP from your game.'
            case 'additional_options':
                ret = 'Informations additionnelles :' if self.current_lang == 'fr' else 'Additional informations :'
            case 'local_only_note':
                ret = '- Cela ne marche qu\'en local, pas sur serveurs dédiés' if self.current_lang == 'fr' else '- This only works locally, not on dedicated servers'
            case 'button_open_scim_txt':
                ret = 'Ouvrir Satisfactory Calculator (SCIM)' if self.current_lang == 'fr' else 'Open Satisfactory Calculator (SCIM)'
            case _:
                ret = 'no trad'
        return ret
