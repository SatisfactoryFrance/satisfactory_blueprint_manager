import webbrowser
from tkinter import Menu, messagebox
import customtkinter as ctk


def build_menubar(app):
    """
    app = instance de App (CTk)
    On utilise app.t(...) pour toutes les chaînes.
    """

    t = app.t  # raccourci

    menubar = Menu(app)
    ctk.CTk.config(app, menu=menubar)

    # =========================
    # FICHIER
    # =========================

    menu_file = Menu(menubar, tearoff=0)
    menu_file.add_command(label=t("quit"), command=app.quit)
    menubar.add_cascade(label=t("menu_file"), menu=menu_file)

    # =========================
    # LANGUE
    # =========================

    menu_lang = Menu(menubar, tearoff=0)

    def set_fr():
        app.config_service.set_lang("fr")
        app.i18n.set_locale("fr")

        # rebuild menubar live
        build_menubar(app)

        messagebox.showinfo("Info", t("switch_lang"))

    def set_en():
        app.config_service.set_lang("en")
        app.i18n.set_locale("en")

        # rebuild menubar live
        build_menubar(app)

        messagebox.showinfo("Info", t("switch_lang"))

    menu_lang.add_command(label=t("menu_fr"), command=set_fr)
    menu_lang.add_command(label=t("menu_en"), command=set_en)

    menubar.add_cascade(label=t("menu_lang"), menu=menu_lang)

    # =========================
    # LIENS UTILES
    # =========================

    menu_links = Menu(menubar, tearoff=0)

    menu_links.add_command(label="Site Satisfactory FR", command=lambda: webbrowser.open("https://satisfactoryfr.com"))
    menu_links.add_command(label="Site Satisfactory EN", command=lambda: webbrowser.open("https://satisfactorygame.com"))
    menu_links.add_command(label="Discord FR", command=lambda: webbrowser.open("https://discord.gg/satisfactoryfr"))
    menu_links.add_command(label="Discord EN", command=lambda: webbrowser.open("https://discord.gg/satisfactory"))
    menu_links.add_command(label="Site S.B.M.", command=lambda: webbrowser.open("https://sbm.satisfactoryfr.com"))
    menu_links.add_command(label="Blueprints SCIM", command=lambda: webbrowser.open("https://satisfactory-calculator.com/fr/blueprints"))

    menubar.add_cascade(label=t("useful_links"), menu=menu_links)

    # =========================
    # AIDE
    # =========================

    menu_help = Menu(menubar, tearoff=0)

    def show_about():
        messagebox.showinfo(
            t("menu_about"),
            t("software_aboutsbm")
        )

    def show_help():
        messagebox.showinfo(
            t("menu_howitisworking"),
            f"{t('software_specs')}\n\n"
            f"{t('software_before_anything')}\n"
            f"{t('software_create_first_blueprint')}\n\n"
            f"{t('software_step_1')}\n"
            f"{t('software_step_2')}\n"
            f"{t('software_step_3')}\n"
            f"{t('software_step_4')}\n"
            f"{t('software_step_5')}\n\n"
            f"{t('software_additional_options')}\n"
            f"{t('software_local_only')}"
        )

    menu_help.add_command(label=t("menu_howitisworking"), command=show_help)
    menu_help.add_command(label=t("menu_about"), command=show_about)
    menu_help.add_separator()
    menu_help.add_command(label=t("update_note"), command=lambda: webbrowser.open("https://github.com/SatisfactoryFrance/satisfactory_blueprint_manager/releases"))
    menu_help.add_command(label=t("send_comment"), command=lambda: webbrowser.open("https://github.com/SatisfactoryFrance/satisfactory_blueprint_manager/issues/new/choose"))
    menu_help.add_command(label=t("menu_update"),command=lambda: app.check_update(manual=True))

    menubar.add_cascade(label=t("menu_help"), menu=menu_help)

    return menubar
