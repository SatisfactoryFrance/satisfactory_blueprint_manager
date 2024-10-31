import backend as be
import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu, Toplevel, Text

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.rowconfigure(1, weight=1)

        game_folder_data = be.get_config_by_title('game_folder')
        if game_folder_data is not None:
            self.game_folder = game_folder_data[2]
        else:
            self.game_folder = False

        self.label_game_folder = ctk.CTkLabel(
            self,
            text="Le dossier de ma save : %s" % self.game_folder,
            font=self.winfo_toplevel().button_font,
        )

        self.label_game_folder.grid(
            column=0,
            row=0,
            padx=10,
            pady=5
        )

        self.button_game_folder = ctk.CTkButton(
            self, 
            text="Choisir", 
            command=self.winfo_toplevel().game_folder_button_callback
        )

        self.button_game_folder.grid(
            row=0, 
            column=1, 
            padx=20, 
            pady=20
        )

        if game_folder_data:
            self.button_game_folder.configure(text='Changer')
        else:
            self.label_game_folder.configure(text='Le dossier de ma save est : non défini')

class MainWindow(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weigh=10)

        self.button_add_bp = ctk.CTkButton(
            self, 
            text="Ajouter des blueprints", 
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

        self.bp_list = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.bp_list.grid(
            column=0,
            row=1,
            sticky="nsew"
        )

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Create local db and table if they don't exist
        be.create_config_table()


        # Menu
        menubar = Menu(self)
        self.config(menu=menubar)
        menufichier = Menu(menubar,tearoff=0)
        menufichier.add_command(label="Choisir/changer le répertoire du jeu", command=self.game_folder_button_callback)
        menufichier.add_separator()
        menufichier.add_command(label="Quitter", command=self.quit)
        menubar.add_cascade(label="Fichier", menu=menufichier)

        # Menu Liens Utiles
        links_menu = Menu(menubar, tearoff=0)
        links_menu.add_command(label="Site Satisfactory FR", command=lambda: self.open_link("https://satisfactoryfr.com"))
        links_menu.add_command(label="Discord", command=lambda: self.open_link("https://discord.gg/satisfactoryfr"))
        links_menu.add_command(label="Site SBM", command=lambda: self.open_link("https://sbm.satisfactoryfr.com"))
        menubar.add_cascade(label="Liens Utiles", menu=links_menu)

        # Menu Aide
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Comment ça fonctionne ?", command=self.show_help)
        help_menu.add_command(label="À propos", command=self.show_about)
        menubar.add_cascade(label="Aide", menu=help_menu)

        # Appearance
        ctk.set_appearance_mode('dark')
        self.title('Satisfactory Blueprint Manager')
        self.geometry('1000x600')
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

        game_folder_data = be.get_config_by_title('game_folder')
        if game_folder_data is not None:
            self.load_blueprints()

    def game_folder_button_callback(self):
        q = filedialog.askdirectory()
        
        if q:
            self.sidebar.label_game_folder.configure(text="Le dossier de mon jeu : %s" % q)
            self.sidebar.button_game_folder.configure(text='Changer')
            if self.sidebar.game_folder:
                    be.update_config(title='game_folder', new_value=q)
            else:
                be.create_config(title='game_folder', value=q)
            self.load_blueprints()

    def add_blueprint_button_callback(self):
        game_folder_data = be.get_config_by_title('game_folder')
        if game_folder_data is None:
            messagebox.showerror('Erreur', 'Veuillez tout d\'abord sélectionner le dossier de votre save')
        else:
            q = filedialog.askopenfilenames(
                title='Choisissez le ou les fichiers sbp',
                filetypes=[("Fichiers SBP", "*.sbp")],
            )
            
            if q:
                if not be.check_upload_blueprints(q):
                    messagebox.showerror('Erreur', 'Un blueprint se compose de 2 fichiers : un fichier sbp, et un fichier sbpcfg. Les 2 doivent etre dans le meme dossier.')
                else:
                    be.upload_blueprints(q)
                    self.load_blueprints()
                    messagebox.showinfo('Ajout réussi', 'Le ou les blueprints sélectionnés ont été ajoutés.')

    def load_blueprints(self):
        print('Trying to load bp')
        for child in self.main_window.bp_list.winfo_children():
            child.destroy()

        bps = be.list_bp_from_game_folder()

        for i, bp in enumerate(bps):
            bp_id = bp['id']
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
                text='Supprimer',
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
        answer = messagebox.askyesno(title='Confirmation', message='Etes-vous sur de supprimer ce blueprint ? Cette action est irrémédiable')
        if answer:
            be.delete_bp_from_game_folder(bp_file)
            self.load_blueprints()

    def show_about(self):
        """Affiche une boîte de dialogue À propos."""
        messagebox.showinfo("À propos", "Satisfactory Blueprint Manager v0.0.1\nCréé par Amorcage & Je0ffrey pour la communauté Satisfactory France")

    def show_help(self):
        """Affiche une nouvelle fenêtre avec du texte formaté pour expliquer le fonctionnement."""
        help_window = Toplevel(self)
        help_window.title("Comment ça fonctionne ?")
        help_window.geometry("500x400")

        # Zone de texte avec scrollbar
        text_widget = Text(help_window, wrap="word", font=("Arial", 10))
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)

        # Ajouter du contenu formaté
        text_widget.insert("1.0", "Ce logiciel permet de gérer et déplacer des blueprints (plans) entre un répertoire source et un répertoire cible.\n\n")
        
        # Instructions en gras
        text_widget.insert("end", "AVANT TOUT :\n", "bold")
        text_widget.insert("end", "Vous devez créer un premier blueprint dans le jeu et l'enregistrer afin de créer le repertoire de votre partie :\n", "bold")
        text_widget.insert("end", "1. Ajoutez un répertoire source depuis le menu ou via le bouton approprié.\n")
        text_widget.insert("end", "2. Ajoutez un ou plusieurs répertoires cibles. L'option est pré-configuré pour aller dans le repertoire racine des blueprint. A vous de choisir votre nom de partie\n")
        text_widget.insert("end", "3. Sélectionnez les fichiers dans le répertoire source, puis choisissez 'Copier' ou 'Déplacer'.\n")
        text_widget.insert("end", "4. Cliquez sur 'Exécuter l'action' pour copier ou déplacer les fichiers sélectionnés.\n")
        text_widget.insert("end", "5. Utilisez 'Déplacer vers Source' pour renvoyer des fichiers du répertoire cible vers la source.\n\n")

        # Section Options additionnelles en italique
        text_widget.insert("end", "Options additionnelles :\n", "bold")
        text_widget.insert("end", "- Cela ne marche qu'en local, pas sur serveurs dédiés\n")

        # Configurer les tags de style
        text_widget.tag_configure("bold", font=("Arial", 12, "bold"))
        text_widget.tag_configure("italic", font=("Arial", 10, "italic"))

        # Rendre le texte non modifiable
        text_widget.config(state="disabled")            