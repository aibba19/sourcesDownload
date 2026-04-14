import tkinter as tk

from app.ui import AppUI


def _build_root() -> tk.Tk:
    try:
        from tkinterdnd2 import TkinterDnD

        return TkinterDnD.Tk()
    except Exception:
        return tk.Tk()


def main():
    root = _build_root()
    AppUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
