import json
import requests
from core.itemmanager import ItemManager
from mwclient import Site
import mwclient
import mwapi


class Core:
    def __init__(self):
        # Create database of stuff.
        self.name = "test"
        self.item_manager = ItemManager


