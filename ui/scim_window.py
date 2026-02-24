import customtkinter as ctk
from utils.threads import run_bg

from PIL import Image
from customtkinter import CTkImage
import io


class ScimWindow(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.transient(master)   # liée à la fenêtre principale
        self.lift()             # remonte au premier plan
        self.focus_force()      # prend le focus

        self.master = master
        self.page = 1

        self.title(master.t("title_scim_windows"))
        self.center_window(1000, 600)
        self.configure(fg_color="#1b2838")

        # Header pagination
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=10, pady=5)
        header.configure(fg_color="#2a475e", corner_radius=10)

        self.prev_btn = ctk.CTkButton(
            header,
            text=master.t("previous"),
            width=100,
            command=self.prev_page
        )
        self.prev_btn.pack(side="left")

        self.page_label = ctk.CTkLabel(header, text=f"Page {self.page}")
        self.page_label.pack(side="left", padx=20)
        self.page_label.configure(text_color="#e5e5e5")

        self.next_btn = ctk.CTkButton(
            header,
            text=master.t("next"),
            width=100,
            command=self.next_page
        )
        self.next_btn.pack(side="left")

        # Scrollable list
        self.list = ctk.CTkScrollableFrame(
            self,
            fg_color="#2a475e",
            corner_radius=12
        )
        self.list.pack(fill="both", expand=True, padx=10, pady=10)

        # Loading label
        self.loading = ctk.CTkLabel(self.list, text=master.t("download_in_progress"))
        self.loading.pack(pady=30)

        self.load_page()

    def center_window(self, width=1000, height=600):
        self.update_idletasks()

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")

    # ======================================================
    # Pagination
    # ======================================================

    def next_page(self):
        self.page += 1
        self.load_page()

    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.load_page()

    # ======================================================
    # Loading
    # ======================================================

    def load_page(self):

        for w in self.list.winfo_children():
            w.destroy()

        self.loading = ctk.CTkLabel(self.list, text=self.master.t("download_in_progress"))
        self.loading.pack(pady=30)

        self.page_label.configure(text=f"Page {self.page}")

        self.list._parent_canvas.yview_moveto(0) #Remonte en haut de la liste

        run_bg(
            lambda: self.master.scim.get_blueprints(self.page),
            self.render_items,
            self
        )

    # ======================================================
    # Render
    # ======================================================

    def render_items(self, items):

        for w in self.list.winfo_children():
            w.destroy()

        self._images = []

        if not items:
            ctk.CTkLabel(self.list, text=self.master.t("scim_no_description")).pack()
            return

        for bp in items:

            # ================= CARD =================

            card = ctk.CTkFrame(
                self.list,
                corner_radius=12,
                fg_color="#22384a",
                border_width=1,
                border_color="#3a5a75"
            )
            card.pack(fill="x", padx=10, pady=6)

            # container horizontal
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=10)

            # ================= IMAGE =================

            if bp.get("image"):
                try:
                    img = Image.open(io.BytesIO(bp["image"]))
                    ctk_img = CTkImage(img, size=(180, 76))
                    self._images.append(ctk_img)

                    img_frame = ctk.CTkFrame(row, fg_color="#1b2838", corner_radius=6)
                    img_frame.pack(side="left", padx=(0, 15))

                    ctk.CTkLabel(img_frame, image=ctk_img, text="").pack(padx=4, pady=4)
                except:
                    pass

            # ================= TEXT BLOCK =================

            text_block = ctk.CTkFrame(row, fg_color="transparent")
            text_block.pack(side="left", fill="both", expand=True, padx=(0, 20))

            ctk.CTkLabel(
                text_block,
                text=bp["title"],
                font=ctk.CTkFont(size=14, weight="bold"),
                wraplength=420,
                justify="left",
                text_color="#e5e5e5"
            ).pack(anchor="w")

            desc = bp["description"]

            # clamp manuel (~300 caractères ≈ 3 lignes)
            if len(desc) > 300:
                desc = desc[:300].rsplit(" ", 1)[0] + "..."

            ctk.CTkLabel(
                text_block,
                text=desc,
                font=ctk.CTkFont(size=12),
                wraplength=420,
                justify="left",
                text_color="#9aa7b2"
            ).pack(anchor="w", pady=(4, 0))

            # ================= DOWNLOAD BUTTON =================

            btn = ctk.CTkButton(
                row,
                text=self.master.t("download"),
                width=130,
                height=38,
                fg_color="#3b82f6",
                hover_color="#2563eb",
                corner_radius=6,
                font=ctk.CTkFont(weight="bold"),
                command=lambda b=bp: self.master.download_scim(b["id"], b["title"])
            )

            btn.pack(side="right", padx=10)
