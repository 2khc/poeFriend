import winsound
import pyperclip
import requests
import json
import threading
import logging
from multiprocessing import Pool
import time
import wave
import sys
import logging
import logging.handlers


class StashManager:
    def __init__(self, condition, item_manager):
        self.url = None
        # self.condition = threading.Condition()
        self.condition = condition
        self.stash = None
        self.persist = True
        self.item_manager = item_manager

        # logging
        self.LOG_NAME = "stash_manager_log.out"
        self.logger = logging.getLogger("myLogger")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(
            self.LOG_NAME, maxBytes=80, backupCount=5
        )
        self.logger.addHandler(handler)

    def acquire_latest_id(self):
        stats = requests.get("http://poe.ninja/stats")
        print(stats.content)
        print("\n")
        return

    def acquire_stash_sync(self, stash_url, queue):
        response = requests.get(stash_url)
        response = json.loads(response.content)

        ninja_id = self.acquire_new_id()
        if "error" not in response:
            self.stash = response
            # print(int(last_section_id) - int(last_response_id))
            print("ninja id: ", ninja_id)
            self.stash["next_change_id"] = ninja_id
            self.url = "http://www.pathofexile.com/api/public-stash-tabs?id=" + ninja_id
            print(self.stash["next_change_id"])
            # self.previous_stash = self.stash
            return self.stash
        else:
            time.sleep(3)
            # while not queue.empty():
            #     queue.get()
            print("blocked")
            while not queue.empty():
                queue.get()

            self.url = self.get_new_latest_url()
            return False

    def set_url(self, url):
        self.url = url

    def sync(self, cond, stash_url, queue):
        logging.debug("Syncing from poe")
        self.url = stash_url
        while self.persist:
            # with cond:
            try:
                new_stash = self.acquire_stash_sync(self.url, queue)
                if new_stash:
                    print("adding to queue")
                    queue.put(new_stash)
                    print(queue.qsize())
                time.sleep(1)
            except Exception:
                self.logger.debug(sys.exc_info())
                # print("this")

    def single_refresh(self, stash_url):
        self.acquire_stash_sync(stash_url)
        return self.stash

    def get_stash(self, cond, queue):
        logging.debug("Starting get_stash thread.")
        # t = threading.currentThread()

        while self.persist:
            try:
                if queue.empty():
                    continue

                # print("something: " + queue.get()["next_change_id"])
                target_items = self.item_manager.get_items()

                stash_data = queue.get()["stashes"]
                for stash in stash_data:
                    if stash["items"]:
                        stash_buyout = stash["stash"].split(" ")

                        for item in stash["items"]:
                            is_individual = None
                            if "note" in item:
                                is_individual = True
                            else:
                                is_individual = False

                            if item["league"] == "Harbinger":
                                if len(item["name"].split("<<set:S>>")) == 2:
                                    item_name = item["name"].split("<<set:S>>")[1]
                                    lowercase_item_name = item_name.lower()

                                    if lowercase_item_name in target_items and (
                                                is_individual or stash_buyout[0] == "~b/o") \
                                            and self.str_to_bool(target_items[lowercase_item_name][3]) == item[
                                                "corrupted"] \
                                            and self.str_to_bool(
                                                target_items[lowercase_item_name][2]) == self.is_six_linked(
                                                item["sockets"], 6):
                                        # print("Found: ", item_name, ". Price: ", item["note"])
                                        self.build_buy_message(is_individual, item, item_name, stash,
                                                               target_items[lowercase_item_name][0],
                                                               target_items[lowercase_item_name][1])
                                elif item["typeLine"]:
                                    item_name = item["typeLine"]
                                    lowercase_item_name = item_name.lower()
                                    # print(item_name)
                                    if lowercase_item_name in target_items and (
                                                is_individual or stash_buyout[0] == "~b/o"):
                                        # print("foundfdounfdoufn note;", item["note"])
                                        self.build_buy_message(is_individual, item, item_name, stash,
                                                               target_items[lowercase_item_name][0],
                                                               target_items[lowercase_item_name][1])
            except Exception:
                self.logger.debug(sys.exc_info())

    def str_to_bool(self, text):
        if text == "True":
            return True
        return False

    def is_six_linked(self, sockets, links):
        if len(sockets) >= links:
            count = {}
            for socket in sockets:
                key = str(socket["group"])
                if key in count:
                    count[key] += 1
                else:
                    count[key] = 1

                if count[key] == links:
                    return True
        return False

    @staticmethod
    def build_buy_message(is_individual, item, item_name, stash, price, currency):
        # print("found Dapper for ", item["note"], " in league: ", item["league"])
        # print(item["note"])
        offer_price = None
        offer_price = None
        if is_individual:
            note = item["note"].split(" ")
            offer_price = note[1]
            offer_currency = note[2]
        else:
            stash_price = stash["stash"].split(" ")
            offer_price = stash_price[1]
            offer_currency = stash_price[2]

        if offer_price == 0:
            return

        if offer_currency == currency and int(offer_price) <= price:
            whisper_message = "@" + stash[
                "lastCharacterName"] + " Hi, I would like to buy your " \
                              + item_name + " for " + offer_price + " " + offer_currency + " in " \
                              + item["league"] + "(stash tab " + "\"" + stash["stash"] + "\";" \
                              + "position: left " + str(item["x"]) + ", top " + str(
                item["y"]) + ")"
            pyperclip.copy(whisper_message)
            winsound.Beep(400, 150)
            print(whisper_message)

    def acquire_new_id(self):
        return json.loads(requests.get("http://api.poe.ninja/api/Data/GetStats").content)["next_change_id"]

    def get_new_latest_url(self):
        return "http://www.pathofexile.com/api/public-stash-tabs?id=" + self.acquire_new_id()
