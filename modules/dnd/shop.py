import gspread
import discord
import time

from modules.helper import convertNumberToLetter

class Item:
    name : str = ""
    description : str = ""
    price : int = 0
    item_type : str = ""
    rarity : str = ""
    quantity : int = 0
    extra : str = ""
    
    def __init__(self, name, description, price, item_type, rarity, quantity, extra):
        self.name = name
        self.description = description
        self.price = int(price)
        self.item_type = item_type
        self.rarity = rarity
        self.quantity = int(quantity)
        self.extra = extra
    

class Shop:
    def __init__(self, stats_channel, gs_account):
        self.stats_channel = stats_channel
        self.gc : gspread.Client = gs_account
        self.items = []
        
        sh = self.gc.open_by_key('1XnDKGyJvLsr0eI-wHoKZg0vuNi5lutLGqmUGvsgStis')
        self.ws = sh.get_worksheet_by_id(0)
        
        headers = self.ws.row_values(1)
        if not headers:
            self.ws.update('A1:H1', [['Name','Description','Price','Type','Rarity','Quantity','Extra']])
    
    async def update_list(self):
        self.items = []
        last_row = len(self.ws.col_values(1))
        
        for i in range(2, last_row + 1):
            item = self.ws.row_values(i)
            print(item)
            
            self.items.append(Item(*item))
    
    def list_shop(self):
        return self.items