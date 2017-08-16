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
    def __init__(self, condition):
        self.url = None
        # self.condition = threading.Condition()
        self.condition = condition
        self.stash = None
        self.persist = True
        # name = glob.glob("alert.wav")
        # self.song = AudioSegment.from_wav("assets/alert.wav")
        # play(self.song)
        # winsound.PlaySound("", winsound.SND_ALIAS)
        # asd = wave.open("assets/alert.wav")
        # winsound.Beep(400, 150)
        # self.mp_pool = Pool(process=2)

    def acquire_latest_id(self):
        stats = requests.get("http://poe.ninja/stats")
        print(stats.content)
        print("\n")
        return

    def acquire_stash_sync(self, stash_url):
        stash = requests.get(stash_url)
        self.stash = json.loads(stash.content)
        self.url = "http://www.pathofexile.com/api/public-stash-tabs?id=" + self.stash["next_change_id"]
        print(self.stash["next_change_id"])

    def set_url(self, url):
        self.url = url

    def sync(self, cond, stash_url, queue):
        logging.debug("Syncing from poe")
        self.url = stash_url
        while self.persist:
            with cond:
                self.acquire_stash_sync(self.url)
                queue.put(self.stash)
                cond.notifyAll()
                time.sleep(1)

    def single_refresh(self, stash_url):
        self.acquire_stash_sync(stash_url)
        return self.stash


    def get_stash(self, cond, queue):
        logging.debug("Starting get_stash thread.")
        t = threading.currentThread()
        # while self.persist:
        #     with cond:
        #         cond.wait()
        #         logging.debug("Resource available to requester")
        #         print("something: " + queue.get()["next_change_id"])
        while self.persist:
            print("something: " + queue.get()["next_change_id"])
            stash_data = queue.get()["stashes"]
            for stash in stash_data:
                if stash["items"]:
                    for item in stash["items"]:
                        if len(item["name"].split("<<set:S>>")) == 2:
                            item_name = item["name"].split("<<set:S>>")[1]
                            if item_name == "The Dapper Prodigy":
                                print("found a blackheart")
                        elif item["typeLine"]:
                            item_name = item["typeLine"]
                            if item_name == "The Dapper Prodigy" and "note" in item and item["league"] == "Harbinger":
                                # print("found Dapper for ", item["note"], " in league: ", item["league"])
                                print(item["note"])
                                note = item["note"].split(" ")
                                if note[2] == "chaos" and int(note[1]) <= 9:
                                    whisper_message = "@" + stash["lastCharacterName"] + " Hi, I would like to buy your " \
                                                      + item_name + " for " + note[1] + " " + note[2] + " in "\
                                                      + item["league"] + "(stash tab " + "\""+stash["stash"] + "\";"\
                                                      + "position: left " + str(item["x"]) + ", top " + str(item["y"]) + ")"
                                    pyperclip.copy(whisper_message)
                                    winsound.Beep(400, 150)
                                    print(whisper_message)
                                # @Perry_Berry Hi, I would like to buy your The Dapper Prodigy listed for 9 chaos in Harbinger (stash tab "~b/o 3 chaos"; position: left 10, top 12)
                # return self.stashBlackheart

    # def scan_divination(self):

    def getget(self):
        return self.stash