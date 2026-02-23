import os
import customtkinter as ctk
from tkinter import StringVar


class Sidebar(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.master = master

        folders = master.blueprints.get_blueprint_folders()

        self.selected = StringVar(value=folders[0] if folders else "")

        self.dropdown = ctk.CTkOptionMenu(
            self,
            values=folders,
            variable=self.selected,
            width=300,
            command=self.change_folder
        )
        self.dropdown.pack(side="left", padx=10)

        ctk.CTkButton(
            self,
            text=master.t("add_blueprints"),
            command=master.upload_blueprints
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            self,
            text=master.t("open_scim"),
            command=master.open_scim
        ).pack(side="left", padx=10)

    def change_folder(self, name):

        base = os.path.join(
            os.getenv("LOCALAPPDATA"),
            "FactoryGame",
            "Saved",
            "SaveGames",
            "blueprints"
        )

        path = os.path.join(base, name)

        self.master.config.set_game_folder(path)
        self.master.load_blueprints()
