import customtkinter as ctk


class MainWindow(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.list = ctk.CTkScrollableFrame(self)
        self.list.pack(fill="both", expand=True)

    def render_blueprints(self, items):

        for w in self.list.winfo_children():
            w.destroy()

        for i, bp in enumerate(items):

            name = bp["blueprint"]

            ctk.CTkLabel(self.list, text=name).grid(row=i, column=0, padx=10)

            ctk.CTkButton(
                self.list,
                text=self.master.t("delete"),
                fg_color="red",
                command=lambda n=name: self.master.delete_blueprint(n)
            ).grid(row=i, column=1)
