import backend as be
import customtkinter as ctk
from tkinter import filedialog, messagebox

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