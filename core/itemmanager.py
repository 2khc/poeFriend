import requests
import json

class ItemManager:
    def __init__(self):
        self.items = {}
        self.url = "http://pathofexile.gamepedia.com/api.php"

    def get_uniques(self):
        return self.api_request("Unique")

    def get_normals(self):
        return self.api_request("Normal")

    def api_request(self, item_type):
        payload = {
            'action': 'ask',
            'format': 'json',
            'query': '[[Has rarity::' + item_type +']]|limit=1000'
        }
        r = requests.get(self.url, params=payload)
        response = json.loads(r.content)
        print(json.loads(r.content))
        return response

    def add_item(self, item_name, item_price, currency):
        # self.items.append(item_name)
        self.items[item_name.lower()] = [item_price, currency]
        print("Adding %s", self.items)

    def get_items(self):
        return self.items