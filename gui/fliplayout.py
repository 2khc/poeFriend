import json
import requests
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
        self.item_list = StringVar(value=list(self.item_manager.get_items().keys()))
        self.init_ui()

    def init_ui(self):
        queue_max_size = 10

        watched_items_label = Label(self.mainframe, text="Followed Items:")
        list_box = Listbox(self.mainframe, name="list_box", listvariable=self.item_list)

        # Label
        title_label = Label(self.mainframe, text="poeFriend")
        title_label.grid(column=3, row=0)
        watched_items_label.grid(column=0, row=1, columnspan=1)
        list_box.grid(column=1, row=1, columnspan=4, rowspan=6)
        # list_box.bind("<ListBoxSelect>", )


        condition = threading.Condition()
        queue = Queue(queue_max_size)
        # executor = ThreadPoolExecutor(max_workers=2)

        self.init_stash_url_input(condition, queue)
        self.init_items()
        self.init_item_entry(list_box)
        # self.init_get_stash_button(condition, queue)
        # entry.grid(column=0, row=1, columnspan=2)

    def init_item_entry(self, list_box):
        item_name = StringVar()
        item_price_threshold = DoubleVar()
        price_currency = StringVar()
        preset_currency = ('chaos', 'exa', 'alch', 'fuse')

        item_name_label = Label(self.mainframe, text="Item Name")
        item_price_threshold_label = Label(self.mainframe, text="Price Limit")
        item_name_entry = Entry(self.mainframe, textvariable=item_name)
        # Item entry
        threshold_price_entry = Entry(self.mainframe, textvariable=item_price_threshold)
        price_currency_selection = Combobox(self.mainframe, textvariable=price_currency)
        price_currency_selection['values'] = preset_currency
        price_currency_selection['state'] = 'readonly'
        add_button = Button(self.mainframe, text="Add Item",
                            command=lambda: self.add_to_list(item_name.get(), item_price_threshold.get(),
                                                             price_currency_selection.get()))

        # Add listener to the list box
        def on_list_box_select(*args):
            index = list_box.curselection()
            print(index)
            print("shit")

        list_box.bind('<<ListBoxSelect>>', on_list_box_select)
        list_box.bind("<Double-1>", on_list_box_select)

        item_name_label.grid(column=0, row=7)
        item_price_threshold_label.grid(column=3, row=7)

        # Remove item stuff
        # remove_button = Button(self.mainframe, text="Remove", command=lambda: self.remove_item(item_name))

        item_name_entry.grid(column=0, row=8, columnspan=3)
        threshold_price_entry.grid(column=3, row=8, columnspan=1)
        price_currency_selection.grid(column=4, row=8, columnspan=1)
        add_button.grid(column=5, row=8, columnspan=1)

    def init_items(self):
        sync_items_button = Button(self.mainframe, text="sync", command=self.item_manager.get_uniques)
        # self.item_manager.get_uniques()
        sync_items_button.grid(column=0, row=2)

    def init_stash_url_input(self, condition, queue):
        stash_url_input = Toplevel(self.mainframe)
        stash_url_input.attributes("-topmost", True)
        text = "Click on the button besides this to copy a link to your clipboard."
        text2 = "Follow that link, then click on the long number to get the latest stash update."
        text3 = "Copy the url and paste it below."
        latest_url = StringVar()
        Label(stash_url_input, text=text).pack()
        Label(stash_url_input, text=text2).pack()
        Label(stash_url_input, text=text3).pack()
        Entry(stash_url_input, textvariable=latest_url).pack()
        Button(stash_url_input,
               command=lambda: self.save_latest_url(stash_url_input, latest_url.get(), condition, queue)).pack()

        self.stash_manager.set_url(latest_url)
        latest_change_id = json.loads(requests.get("http://api.poe.ninja/api/Data/GetStats").content)["nextChangeId"]
        latest_url = "http://www.pathofexile.com/api/public-stash-tabs?id=" + latest_change_id
        t1 = threading.Thread(name="t1", target=self.stash_manager.sync, args=(condition, latest_url, queue))
        t1.start()
        t2 = threading.Thread(name="t2", target=self.stash_manager.get_stash, args=(condition, queue,))
        t2.start()
        # Button(self.mainframe, text="Start Scan Thread", command=t2.start).grid(column=0,row=3)
        stash_url_input.destroy()

    def add_to_list(self, item_name, price, currency):
        self.item_manager.add_item(item_name, price, currency)
        self.item_list.set(value=list(self.item_manager.get_items().keys()))

    def save_latest_url(self, window, latest_url, cond, queue):
        self.stash_manager.set_url(latest_url)
        latest_change_id = json.loads(requests.get("http://api.poe.ninja/api/Data/GetStats"))["nextChangeId"]

        # def select_listbox_item(self):

        # def init_get_stash_button(self, cond, queue):
        #     t2 = threading.Thread(name="t2", target=self.stash_manager.get_stash, args=(cond, queue,))
        #     Button(self.mainframe, text="Start Scan Thread", command=t2.start).grid(column=0,row=3)
        #     return
