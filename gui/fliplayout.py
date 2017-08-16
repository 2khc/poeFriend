from tkinter import *
from tkinter.ttk import *
import threading
from core import *
from concurrent.futures import *
from multiprocessing import Queue, Process

class FlipLayout:
    def __init__(self, mainframe, item_manager, stash_manager):
        self.mainframe = mainframe
        self.item_manager = item_manager
        self.stash_manager = stash_manager
        self.item_list = StringVar(value=self.item_manager.get_items())
        self.init_ui()

    def init_ui(self):
        watched_items_label = Label(self.mainframe, text="Followed Items:")
        list_box = Listbox(self.mainframe, listvariable=self.item_list)
        # Label
        title_label = Label(self.mainframe, text="poeFriend")
        # ttk.Label(window, text="Test").grid()
        # # label.pack()
        #
        # # Entry
        # # entry.pack()
        #
        #
        title_label.grid(column=3, row=0)
        watched_items_label.grid(column=0, row=1, columnspan=1)
        list_box.grid(column=1, row=1, columnspan=4, rowspan=6)

        condition = threading.Condition()
        queue = Queue()
        executor = ThreadPoolExecutor(max_workers=2)

        self.init_stash_url_input(condition, queue)
        self.init_items()
        self.init_item_entry()
        self.init_get_stash_button(condition, queue)
        # entry.grid(column=0, row=1, columnspan=2)

    def init_item_entry(self):
        item_name = StringVar()
        item_price_threshold = DoubleVar()
        item_name_label = Label(self.mainframe, text="Item Name")
        item_price_threshold_label = Label(self.mainframe, text="Price Limit")
        item_name_entry = Entry(self.mainframe, textvariable=item_name)
        # Item entry
        threshold_price_entry = Entry(self.mainframe, textvariable=item_price_threshold)
        add_button = Button(self.mainframe, text="Add Item", command=lambda: self.add_to_list(item_name))

        item_name_label.grid(column=0, row=7)
        item_price_threshold_label.grid(column=3, row=7)

        item_name_entry.grid(column=0, row=8, columnspan=3)
        threshold_price_entry.grid(column=3, row=8, columnspan=1)
        add_button.grid(column=5, row=8, columnspan=1)

    def init_items(self):
        sync_items_button = Button(self.mainframe, text="sync", command=self.item_manager.get_uniques)
        # self.item_manager.get_uniques()
        sync_items_button.grid(column=0, row=2)

    def init_stash_url_input(self, condition, queue):
        stash_url_input = Toplevel(self.mainframe)
        text = "Click on the button besides this to copy a link to your clipboard."
        text2 = "Follow that link, then click on the long number to get the latest stash update."
        text3 = "Copy the url and paste it below."
        latest_url = StringVar()
        Label(stash_url_input, text=text).pack()
        Label(stash_url_input, text=text2).pack()
        Label(stash_url_input, text=text3).pack()
        Entry(stash_url_input, textvariable=latest_url).pack()
        Button(stash_url_input, command=lambda: self.save_latest_url(stash_url_input, latest_url.get(), condition, queue)).pack()

    def add_to_list(self, item_name):
        self.item_manager.add_item(item_name.get())
        self.item_list.set(value=self.item_manager.get_items())

    def save_latest_url(self, window, latest_url, cond, queue):
        self.stash_manager.set_url(latest_url)
        # condition = threading.Condition()
        t1 = threading.Thread(name="t1", target=self.stash_manager.sync, args=(cond, latest_url, queue))
        t1.start()
        # while True:
        #     self.stash_manager.single_refresh(latest_url)
        window.destroy()

    def init_get_stash_button(self, cond, queue):
        t2 = threading.Thread(name="t2", target=self.stash_manager.get_stash, args=(cond, queue,))
        Button(self.mainframe, text="Start Scan Thread", command=t2.start).grid(column=0,row=3)
        return

    # def start_scan(self):