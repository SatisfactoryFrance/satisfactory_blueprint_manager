import webbrowser
from tkinter import Menu, messagebox


def build_menubar(app):
    """
    app = instance de App (CTk)
    On ne met ici que de l'UI/menus + appels vers app / services.
    """
    menubar = Menu(app)
    app.config(menu=menubar)

    # ---------------- Fichier ----------------
    menu_file = Menu(menubar, tearoff=0)
    menu_file.add_command(label="Quitter", command=app.quit)
    menubar.add_cascade(label="Fichier", menu=menu_file)

    # ---------------- Langue ----------------
    menu_lang = Menu(menubar, tearoff=0)

    def set_fr():
        app.config.set_lang("fr")
        messagebox.showinfo("Langue", "Langue changée en FR. Redémarre l'app si besoin.")

    def set_en():
        app.config.set_lang("en")
        messagebox.showinfo("Langue", "Language set to EN. Restart app if needed.")

    # Simple et robuste (radio)
    menu_lang.add_radiobutton(label="Français", command=set_fr)
    menu_lang.add_radiobutton(label="English", command=set_en)
    menubar.add_cascade(label="Langue", menu=menu_lang)

    # ---------------- Liens utiles ----------------
    menu_links = Menu(menubar, tearoff=0)
    menu_links.add_command(label="Site Satisfactory FR", command=lambda: webbrowser.open("https://satisfactoryfr.com"))
    menu_links.add_command(label="Site Satisfactory EN", command=lambda: webbrowser.open("https://satisfactorygame.com"))
    menu_links.add_command(label="Discord FR", command=lambda: webbrowser.open("https://discord.gg/satisfactoryfr"))
    menu_links.add_command(label="Discord EN", command=lambda: webbrowser.open("https://discord.gg/satisfactory"))
    menu_links.add_command(label="Site S.B.M.", command=lambda: webbrowser.open("https://sbm.satisfactoryfr.com"))
    menu_links.add_command(label="Blueprints SCIM", command=lambda: webbrowser.open("https://satisfactory-calculator.com/fr/blueprints"))
    menubar.add_cascade(label="Liens utiles", menu=menu_links)

    # ---------------- Aide ----------------
    menu_help = Menu(menubar, tearoff=0)

    def about():
        messagebox.showinfo(
            "À propos",
            "Satisfactory Blueprint Manager\nProjet communautaire Satisfactory France"
        )

    def help_():
        messagebox.showinfo(
            "Aide",
            "• Choisis un dossier de save via la liste déroulante\n"
            "• Ajoute des .sbp (+ .sbpcfg)\n"
            "• Télécharge depuis SCIM\n"
        )

    def open_latest_release():
        webbrowser.open("https://github.com/SatisfactoryFrance/satisfactory_blueprint_manager/releases/latest/")

    menu_help.add_command(label="Comment ça marche", command=help_)
    menu_help.add_command(label="À propos", command=about)
    menu_help.add_separator()
    menu_help.add_command(label="Vérifier les mises à jour", command=app.check_update)
    menu_help.add_command(label="Dernière release (GitHub)", command=open_latest_release)
    menubar.add_cascade(label="Aide", menu=menu_help)

    return menubar