import customtkinter as ctk
from utils.threads import run_bg

from PIL import Image
from customtkinter import CTkImage
import io
from utils.paginatator import Paginatator


class ScimWindow(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.paginatator = Paginatator()
        self.paginatator.setMaxPage(1)
        self.paginatator.setWidth(20)  # nombre de bouton de la pagination

        self.transient(master)   # liée à la fenêtre principale
        self.lift()             # remonte au premier plan
        self.focus_force()      # prend le focus

        self.master = master
        self.paginatator.setCurrentPage(1)

        self.title(master.t("title_scim_windows"))
        self.center_window(1000, 600)
        self.configure(fg_color="#1b2838")

        # Header pagination
        self.header = ctk.CTkFrame(self)
        self.header.pack(fill="x", padx=10, pady=5)
        self.header.configure(fg_color="#2a475e", corner_radius=10)

        self.redrawHeader()

        # ================= SEARCH =================

        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=10)

        self.search_var = ctk.StringVar()

        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text=self.master.t("search_scim"),
            fg_color="#1b2838",
            text_color="#ffffff",
            placeholder_text_color="#9aa7b2",
            border_color="#3a5a75",
            corner_radius=8,
            height=32
        )
        self.search_entry.pack(fill="x", pady=(0, 8))
        # rendre le curseur visible et donner le focus au champ (améliore l'UX)
        try:
            # certaines versions exposent 'insertbackground' via configure
            self.search_entry.configure(insertbackground="#ffffff")
        except Exception:
            pass
        # Donner le focus pour que l'utilisateur voie le caret immédiatement
        try:
            self.search_entry.focus_set()
        except Exception:
            pass

        # Put a visible default text in the field (placeholder-like) and
        # clear/restore it on focus so the user always sees a hint.
        self._default_search_text = self.master.t("search_scim")
        # set initial value to the default text and make it look like a placeholder
        self.search_var.set(self._default_search_text)
        try:
            self.search_entry.configure(text_color="#9aa7b2")
        except Exception:
            pass

        def _clear_placeholder(e):
            if self.search_var.get() == self._default_search_text:
                self.search_var.set("")
                try:
                    self.search_entry.configure(text_color="#ffffff")
                except Exception:
                    pass

        def _restore_placeholder(e):
            if not self.search_var.get().strip():
                self.search_var.set(self._default_search_text)
                try:
                    self.search_entry.configure(text_color="#9aa7b2")
                except Exception:
                    pass

        self.search_entry.bind("<FocusIn>", _clear_placeholder)
        self.search_entry.bind("<FocusOut>", _restore_placeholder)

        def search_local():
            self.paginatator.setCurrentPage(1)
            self.load_page()

        self.search = search_local
        self.search_entry.bind("<Return>", lambda e: self.search())

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

    def go_to_page(self, page: int):
        self.paginatator.setCurrentPage(page)
        self.load_page()

    def headerBtn(self, targetPage: int, currentPage: int, text: str):
        btn = ctk.CTkButton(
            self.header,
            text=self.master.t(text),
            width=10,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=lambda: self.go_to_page(targetPage)
        )
        btn.pack(side="left", padx=1)
        if (targetPage == currentPage):
            btn.configure(state='disabled', fg_color="#3d6485")
        return btn

    def redrawHeader(self):
        for child in self.header.winfo_children():
            child.destroy()
        self.paginatator.generateFirst(lambda targetPage, currentPage: self.headerBtn(targetPage, currentPage, "<<"))
        self.paginatator.generatePrevious(lambda targetPage, currentPage: self.headerBtn(targetPage, currentPage, "<"))
        self.paginatator.generateRange(lambda targetPage, currentPage: self.headerBtn(targetPage, currentPage, str(targetPage)))
        self.paginatator.generateNext(lambda targetPage, currentPage: self.headerBtn(targetPage, currentPage, ">"))
        self.paginatator.generateLast(lambda targetPage, currentPage: self.headerBtn(targetPage, currentPage, ">>"))

    # ======================================================
    # Loading
    # ======================================================

    def load_page(self):

        for w in self.list.winfo_children():
            w.destroy()

        self.loading = ctk.CTkLabel(self.list, text=self.master.t("download_in_progress"))
        self.loading.pack(pady=30)

        # self.paginatator.currentPage_label.configure(text=f"Page {self.paginatator.currentPage}")

        self.list._parent_canvas.yview_moveto(0)  # Remonte en haut de la liste

        query = self.search_var.get().strip() if hasattr(self, "search_var") else ""
        if hasattr(self, "_default_search_text") and query == self._default_search_text:
            query = ""

        run_bg(
            lambda: self.master.scim.get_blueprints(self.paginatator.currentPage, query),
            self.render_items,
            self
        )

    # ======================================================
    # Render
    # ======================================================

    def render_items(self, results):

        for w in self.list.winfo_children():
            w.destroy()

        if (results.maxPage > 0):
            self.paginatator.setMaxPage(results.maxPage)
        self.redrawHeader()
        self._images = []

        if not results.items:
            ctk.CTkLabel(self.list, text=self.master.t("scim_no_description")).pack()
            return

        for bp in results.items:

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

            desc = bp.get("description") or self.master.t("scim_no_description")

            desc_label = ctk.CTkLabel(
                text_block,
                text=self.master.t("scim_click_description"),
                font=ctk.CTkFont(size=12),
                wraplength=420,
                justify="left",
                text_color="#60a5fa"
            )
            desc_label.pack(anchor="w", pady=(4, 0))

            def click(e, b=bp, lbl=desc_label):
                self.load_description(b, lbl)

            for widget in (card, row, text_block, desc_label):
                widget.bind("<Button-1>", click)

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

    def load_description(self, bp, label):
        if bp.get("description"):
            return
        label.configure(text="Chargement…")

        def work():
            return self.master.scim.get_description(bp["id"])

        def done(desc):
            bp["description"] = desc
            label.configure(text=desc)
        run_bg(work, done, self)
