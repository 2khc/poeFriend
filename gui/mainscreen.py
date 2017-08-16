from tkinter import *
from tkinter import ttk
from .fliplayout import FlipLayout
import threading
# from . import FlipLayout
# from gui import FlipLayout

# from tkinter import *
from core import *

class MainScreen:
    def __init__(self):
        self.root = Tk()
        self.root.title("poeFriend")
        # window.geometry("500x500")
        self.menu = Menu(self.root)
        self.create_menu()
        mainframe = ttk.Frame(self.root, borderwidth=5, padding="3 12 3 12", width=500, height=300)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        item_manager = ItemManager()
        default_layout = FlipLayout(
            mainframe,
            item_manager=item_manager,
            stash_manager=StashManager(threading.Condition(), item_manager)
        )

        self.root.mainloop()

    def create_menu(self):
        self.root.config(menu=self.menu)
        file_menu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=file_menu)

        help_menu = Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self.about)
        return

    def about(self):
        print("Some about stuff")