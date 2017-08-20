import requests
import json


class ItemManager:
    def __init__(self):
        self.items = {}
        self.items_file = "item_list.json"
        self.load_json()
        self.url = "http://pathofexile.gamepedia.com/api.php"

    def get_uniques(self):
        return self.api_request("Unique")

    def get_normals(self):
        return self.api_request("Normal")

    def api_request(self, item_type):
        payload = {
            'action': 'ask',
            'format': 'json',
            'query': '[[Has rarity::' + item_type + ']]|limit=1000'
        }
        r = requests.get(self.url, params=payload)
        response = json.loads(r.content)
        print(json.loads(r.content))
        return response

    def add_item(self, item_name, item_price, currency):
        # self.items.append(item_name)
        self.items[item_name.lower()] = [item_price, currency]
        self.save_json()
        print("Adding %s", self.items)

    def get_items(self):
        return self.items

    def remove_item(self, item_name):
        self.items.pop(item_name)

    def save_json(self):
        with open(self.items_file, "w") as outfile:
            json.dump(self.items, outfile)

    def load_json(self):
        try:
            with open(self.items_file, "r") as outfile:
                self.items = json.load(outfile)
        except Exception:
            print(Exception)
