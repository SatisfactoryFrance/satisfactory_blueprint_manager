from frontend import App
import tkinter as tk

if __name__ == "__main__":
    # Faut init tkinter pour avoir les messagebox
    root = tk.Tk()
    root.withdraw()  # On lance pas le logiciel

    # Lancer l'application principale
    app = App()
    app.mainloop()
