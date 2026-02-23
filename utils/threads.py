import threading


def run_bg(fn, callback, tk_root):
    def wrapper():
        result = fn()
        tk_root.after(0, lambda: callback(result))

    threading.Thread(target=wrapper, daemon=True).start()
