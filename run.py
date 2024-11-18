from frontend import App, display_update_status
import tkinter as tk

if __name__ == "__main__":
    # Faut init tkinter pour avoir les messagebox
    root = tk.Tk()
    root.withdraw()  # On lance pas le logiciel

    display_update_status()

    # Lancer l'application principale
    app = App()
    app.mainloop()
