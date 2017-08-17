import winsound
import pyperclip
import requests
import json
import threading
import logging
from multiprocessing import Pool
import time
import wave


class StashManager:
    def __init__(self, condition, item_manager):
        self.url = None
        # self.condition = threading.Condition()
        self.condition = condition
        self.stash = None
        self.persist = True
        self.item_manager = item_manager

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
            self.url = "http://www.pathofexile.com/api/public-stash-tabs?id=" + self.stash["next_change_id"]
            print(self.stash["next_change_id"])
            return self.stash
        else:
            time.sleep(3)
            # while not queue.empty():
            #     queue.get()
            self.url = self.get_new_latest_url()
            return False
            # queue.

    def set_url(self, url):
        self.url = url

    def sync(self, cond, stash_url, queue):
        logging.debug("Syncing from poe")
        self.url = stash_url
        while self.persist:
            with cond:
                new_stash = self.acquire_stash_sync(self.url, queue)
                if new_stash:
                    queue.put(self.stash)
                # print("Searching for: ", self.item_manager.get_items())
                cond.notifyAll()
                time.sleep(0.5)

    def single_refresh(self, stash_url):
        self.acquire_stash_sync(stash_url)
        return self.stash

    def get_stash(self, cond, queue):
        logging.debug("Starting get_stash thread.")
        t = threading.currentThread()

        while self.persist:
            if queue.empty():
                continue

            print("something: " + queue.get()["next_change_id"])
            target_items = self.item_manager.get_items()

            stash_data = queue.get()["stashes"]
            for stash in stash_data:
                if stash["items"]:
                    for item in stash["items"]:
                        if item["league"] == "Harbinger":
                            if len(item["name"].split("<<set:S>>")) == 2:
                                item_name = item["name"].split("<<set:S>>")[1]
                                lowercase_item_name = item_name.lower()
                                if lowercase_item_name in target_items and "note" in item:
                                    # print("Found: ", item_name, ". Price: ", item["note"])
                                    self.build_buy_message(item, item_name, stash, target_items[lowercase_item_name][0],
                                                           target_items[lowercase_item_name][1])
                            elif item["typeLine"]:
                                item_name = item["typeLine"]
                                lowercase_item_name = item_name.lower()
                                # print(item_name)
                                if lowercase_item_name in target_items and "note" in item:
                                    print("foundfdounfdoufn note;", item["note"])
                                    self.build_buy_message(item, item_name, stash, target_items[lowercase_item_name][0],
                                                           target_items[lowercase_item_name][1])

    @staticmethod
    def build_buy_message(item, item_name, stash, price, currency):
        # print("found Dapper for ", item["note"], " in league: ", item["league"])
        # print(item["note"])
        note = item["note"].split(" ")
        if note[2] == currency and int(note[1]) <= price:
            whisper_message = "@" + stash[
                "lastCharacterName"] + " Hi, I would like to buy your " \
                              + item_name + " for " + note[1] + " " + note[2] + " in " \
                              + item["league"] + "(stash tab " + "\"" + stash["stash"] + "\";" \
                              + "position: left " + str(item["x"]) + ", top " + str(
                item["y"]) + ")"
            pyperclip.copy(whisper_message)
            winsound.Beep(400, 150)
            print(whisper_message)

    def acquire_new_id(self):
        return json.loads(requests.get("http://api.poe.ninja/api/Data/GetStats").content)["nextChangeId"]

    def get_new_latest_url(self):
        return "http://www.pathofexile.com/api/public-stash-tabs?id=" + self.acquire_new_id()