import customtkinter as ctk
from utils.threads import run_bg


class ScimWindow(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.page = 1

        self.list = ctk.CTkScrollableFrame(self)
        self.list.pack(fill="both", expand=True)

        run_bg(
            lambda: master.scim.get_blueprints(self.page),
            self.render,
            self
        )

    def render(self, items):

        for bp in items:

            ctk.CTkLabel(self.list, text=bp["title"]).pack(anchor="w")

            ctk.CTkButton(
                self.list,
                text="Télécharger",
                command=lambda b=bp: self.master.download_scim(b["id"], b["title"])
            ).pack(anchor="e")
