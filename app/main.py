import tkinter as tk

from app.ui import AppUI


def main():
    root = tk.Tk()
    AppUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
