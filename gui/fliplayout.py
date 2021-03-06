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

        show_info_frame = Frame(self.mainframe, borderwidth=5,relief=SUNKEN)
        show_info_frame.grid(column=1, row=1,columnspan=4,rowspan=6)

        scrollbar = Scrollbar(show_info_frame)
        scrollbar.grid(column=4, sticky=E )
        watched_items_label = Label(self.mainframe, text="Followed Items:")
        list_box = Listbox(show_info_frame, name="list_box", listvariable=self.item_list, yscrollcommand=scrollbar.set)

        scrollbar.config(command=list_box.yview)
        # Label
        title_label = Label(self.mainframe, text="poeFriend")
        title_label.grid(column=3, row=0)
        watched_items_label.grid(column=0, row=1, columnspan=1)
        # list_box.grid(column=1, row=1, columnspan=4, rowspan=6)
        list_box.grid(column=0, row=0, columnspan=3,sticky=(N,W))
# u        list_box.pack()
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
        self.price_currency = StringVar()
        self.is_corrupted = BooleanVar()
        self.is_six_linked = BooleanVar()

        preset_currency = ['chaos', 'exa', 'alch', 'fuse']
        preset_selections = (False, True)

        item_name_label = Label(self.mainframe, text="Item Name")
        item_price_threshold_label = Label(self.mainframe, text="Price Limit")
        is_corrupted_label = Label(self.mainframe, text="Corrupted?")
        is_six_link_label  = Label(self.mainframe, text="6-linked?")
        item_name_entry = Entry(self.mainframe, textvariable=item_name)


        # Item entry stuff here
        # ==============================================================================================
        # ==============================================================================================
        threshold_price_entry = Entry(self.mainframe, textvariable=item_price_threshold)
        price_currency_selection = Combobox(self.mainframe, textvariable=self.price_currency, values=preset_currency)
        price_currency_selection['state'] = 'readonly'
        price_currency_selection.current(0)

        corrupted_selection = Combobox(self.mainframe, textvariable=self.is_corrupted, values=preset_selections)
        corrupted_selection["state"] = "readonly"
        corrupted_selection.current(0)

        six_link_selection = Combobox(self.mainframe, textvariable=self.is_six_linked)
        six_link_selection['values'] = preset_selections
        six_link_selection["state"] = "readonly"
        six_link_selection.current(0)

        add_button = Button(self.mainframe, text="Add Item",
                            command=lambda: self.add_to_list(item_name.get(), item_price_threshold.get(),
                                                             price_currency_selection.get(), six_link_selection.get(), corrupted_selection.get()))
        delete_button = Button(self.mainframe, text="Delete Item",
                               command=lambda: self.remove_from_list(item_name.get()))

        # Add listener to the list box
        # ===================================================================
        def on_list_box_select(*args):
            index = list_box.curselection()
            item_string = list_box.get(index)
            item_data = self.item_manager.get_items()[item_string]
            item_name.set(value=item_string)
            item_price_threshold.set(value=item_data[0])
            six_link_selection.set(value=item_data[2])
            corrupted_selection.set(value=item_data[3])
            price_currency_selection.set(value=item_data[1])
            print(index)
            print("shit")

        list_box.bind("<<ListBoxSelect>>", on_list_box_select)
        list_box.bind("<Double-1>", on_list_box_select)

        item_name_label.grid(column=0, row=7)
        item_price_threshold_label.grid(column=3, row=7)
        is_six_link_label.grid(column=5, row=7)
        is_corrupted_label.grid(column=6, row=7)

        # Remove item stuff
        # remove_button = Button(self.mainframe, text="Remove", command=lambda: self.remove_item(item_name))

        # Set items to grid
        # ==============================================================================================
        # ==============================================================================================
        item_name_entry.grid(column=0, row=8, columnspan=3)
        threshold_price_entry.grid(column=3, row=8, columnspan=1)
        price_currency_selection.grid(column=4, row=8, columnspan=1)    
        six_link_selection.grid(column=5, row=8, columnspan=1)
        corrupted_selection.grid(column=6, row=8, columnspan=1)
        add_button.grid(column=7, row=8, columnspan=1)
        delete_button.grid(column=0, row=4)

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

        latest_change_id = json.loads(requests.get("http://api.poe.ninja/api/Data/GetStats").content)["next_change_id"]

        latest_url = "http://www.pathofexile.com/api/public-stash-tabs?id=" + latest_change_id
        t1 = threading.Thread(name="t1", target=self.stash_manager.sync, args=(condition, latest_url, queue))
        t1.start()
        t2 = threading.Thread(name="t2", target=self.stash_manager.get_stash, args=(condition, queue,))
        t2.start()
        # Button(self.mainframe, text="Start Scan Thread", command=t2.start).grid(column=0,row=3)
        stash_url_input.destroy()

    def add_to_list(self, item_name, price, currency, is_six_link, is_corrupted):
        self.item_manager.add_item(item_name, price, currency, is_six_link, is_corrupted)
        self.item_list.set(value=list(self.item_manager.get_items().keys()))

    def remove_from_list(self, item_name):
        self.item_manager.remove_item(item_name)
        self.item_list.set(value=list(self.item_manager.get_items().keys()))

    def save_latest_url(self, window, latest_url, cond, queue):
        self.stash_manager.set_url(latest_url)
        latest_change_id = json.loads(requests.get("http://api.poe.ninja/api/Data/GetStats"))["nextChangeId"]

        # def select_listbox_item(self):

        # def init_get_stash_button(self, cond, queue):
        #     t2 = threading.Thread(name="t2", target=self.stash_manager.get_stash, args=(cond, queue,))
        #     Button(self.mainframe, text="Start Scan Thread", command=t2.start).grid(column=0,row=3)
        #     return
