import customtkinter as ctk


class MainWindow(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color="#1b2838")

        self.master = master

        self.list = ctk.CTkScrollableFrame(
            self,
            fg_color="#2a475e",
            corner_radius=12
        )
        self.list.pack(fill="both", expand=True, padx=10, pady=10)

    def render_blueprints(self, items):

        # On remonte la liste tout en haut avant load
        self.list._parent_canvas.yview_moveto(0)

        for w in self.list.winfo_children():
            w.destroy()

    # ================= EMPTY STATE =================
        if not items:

            empty_frame = ctk.CTkFrame(
                self.list,
                fg_color="transparent"
            )
            empty_frame.pack(expand=True, pady=80)

            ctk.CTkLabel(
                empty_frame,
                text="🧩 " + self.master.t("empty_local_title"),
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#9aa7b2"
            ).pack(pady=(0, 20))

            ctk.CTkLabel(
                empty_frame,
                text=self.master.t("empty_local_hint"),
                font=ctk.CTkFont(size=13),
                text_color="#7f8c8d"
            ).pack(pady=(0, 25))

            btns = ctk.CTkFrame(empty_frame, fg_color="transparent")
            btns.pack()

            ctk.CTkButton(
                btns,
                text=self.master.t("add_blueprints"),
                width=200,
                command=self.master.upload_blueprints
            ).pack(side="left", padx=10)

            ctk.CTkButton(
                btns,
                text=self.master.t("open_scim"),
                width=200,
                fg_color="#3b82f6",
                hover_color="#2563eb",
                command=self.master.open_scim
            ).pack(side="left", padx=10)

            return

        # RETOUR A LA LISTE NORMALE
        for bp in items:

            name = bp["blueprint"]

            card = ctk.CTkFrame(
                self.list,
                corner_radius=12,
                fg_color="#22384a",
                border_width=1,
                border_color="#3a5a75"
            )
            card.pack(fill="x", padx=10, pady=6)

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=10)

            ctk.CTkLabel(
                row,
                text=name,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#e5e5e5",
                wraplength=500,
                justify="left"
            ).pack(side="left", expand=True, anchor="w")

            ctk.CTkButton(
                row,
                text="Supprimer",
                width=110,
                fg_color="#b91c1c",
                hover_color="#991b1b",
                corner_radius=6,
                command=lambda n=name: self.master.delete_blueprint(n)
            ).pack(side="right")

