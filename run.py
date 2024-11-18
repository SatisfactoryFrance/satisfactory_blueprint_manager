from frontend import App, check_for_update
import tkinter as tk

if __name__ == "__main__":
    # Faut init tkinter pour avoir les messagebox
    root = tk.Tk()
    root.withdraw()  # On lance pas le logiciel

    check_for_update()

    # Lancer l'application principale
    app = App()
    app.mainloop()
