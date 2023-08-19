import gspread
import string
import math
import datetime

from modules.dnd.reminder import show_liked_posts
from modules.dnd.player import Player

def convertNumberToLetter(number):
    letters_length = len(string.ascii_uppercase)
    
    number_of_letters = 1
    if number > 0:
        number_of_letters = math.floor(math.log(number, letters_length)) + 1
    
    letters = ""
    for i in range(number_of_letters):
        letters = string.ascii_uppercase[number % letters_length] + letters
        number = math.floor(number / letters_length) - 1
        
    return letters

class DnD:
    users = {}
    server = None
    role = None
    stats_channel = None
    player_post = None
    
    classes = [
        "Barbarian",
        "Bard",
        "Cleric",
        "Druid",
        "Fighter",
        "Monk",
        "Paladin",
        "Ranger",
        "Rogue",
        "Sorcerer",
        "Warlock",
        "Wizard",
        "Artificer"
    ]
    
    races = [
        "aarakocra",
        "aasimar",
        "bugbear",
        "centaur",
        "changeling",
        "deep gnome",
        "dragonborn",
        "duergar",
        "dwarf",
        "eladrin",
        "elf",
        "fairy",
        "firbolg",
        "genasi",
        "githyanki",
        "githzerai",
        "gnome",
        "goblin",
        "goliath",
        "half-elf",
        "half-orc",
        "halfling",
        "harengon",
        "hobgoblin",
        "human",
        "kenku",
        "kobold",
        "lizardfolk",
        "minotaur",
        "orc",
        "satyr",
        "sea elf",
        "shadar-kai",
        "shifter",
        "tabaxi",
        "tiefling",
        "tortle",
        "triton",
        "yuan-ti"
    ]

    def __init__(self, bot):
        self.server = bot.get_guild(1084891853758935141)
        self.role = self.server.get_role(1134772402820239370)
        self.stats_channel = self.server.get_channel(1142411553451290636)
        
        gc = gspread.service_account(filename='service_account.json')
        sh = gc.open_by_key('14J14qZFMWu9-xNEPBQCJMyZr_waUvCGvzb7yQsXKnwg')
        self.ws = sh.get_worksheet(0)
        
        i = 0
        for attr in dir(Player):
            if not attr.startswith("__"):
                print(convertNumberToLetter(i), attr)
                self.ws.update(f'{convertNumberToLetter(i)}1', attr)
                i += 1
        
        self.update_users()

    def update_users(self):
        all_users = self.server.members
        for user in all_users:
            if self.role in user.roles:
                namecell = self.ws.find(user.name)
                if (namecell):
                    row = namecell.row
                    col = namecell.col
                    player = Player()
                    for attr in dir(player):
                        if not attr.startswith("__"):
                            print(attr, self.ws.cell(row, col).value)
                            setattr(player, attr, self.ws.cell(row, col).value)
                            col += 1
                    self.users[user.id] = {"User": user, "Player": player}
                self.users[user.id] = {"User": user, "Player": None}
    
    def update_player(self, user, player):
        namecell = self.ws.find(user.name)
        if (namecell):
            row = namecell.row
            col = namecell.col
            for attr in dir(player):
                if not attr.startswith("__"):
                    print(attr, self.ws.cell(row, col).value)
                    self.ws.update_cell(row, col, getattr(player, attr))
                    col += 1
                    
    def create_player(self, user, **kwargs):
        player = Player()
        namecell = self.ws.find(user.name)
        available_row = len(self.ws.col_values(1)) + 1
        if (namecell):
            available_row = namecell.row
        col = 1
        
        player.Player_Name = user.name
        player.character_name = kwargs['character_name']
        player.character_race = kwargs["character_race"]
        player.character_class = kwargs["character_class"]
        player.last_played = datetime.datetime(2023,7,1).strftime("%Y-%m-%d")
        player.games_played = 0
        
        for attr in dir(player):
            if not attr.startswith("__"):
                self.ws.update_cell(available_row, col, getattr(player, attr))
                col += 1
        
        self.users[user.id] = {"User": user, "Player": player}
    
    def update_stats(self):
        if self.player_post:
            pass
            
    
    def get_users(self):
        return self.users
    
    async def show_likes(self):
        self.update_users()
        return await show_liked_posts(self.server, self.users)