import gspread
import string
import math
import datetime
import discord

from modules.dnd.player import Player
from modules.dnd.mission import Mission
from modules.dnd.roll import DiceRoller

def convertNumberToLetter(number):
    letters_length = len(string.ascii_uppercase)
    
    number_of_letters = 1
    if number > 0:
        number_of_letters = math.floor(math.log(number, letters_length)) + 1
    
    letters = ""
    for _ in range(number_of_letters):
        letters = string.ascii_uppercase[number % letters_length] + letters
        number = math.floor(number / letters_length) - 1
        
    return letters

class DnD:
    users = {}
    server = None
    role = None
    stats_channel = None
    player_post = None
    adventure_board = None
    dice_roller = None
    
    classes = [
        "barbarian",
        "bard",
        "cleric",
        "druid",
        "fighter",
        "monk",
        "paladin",
        "ranger",
        "rogue",
        "sorcerer",
        "warlock",
        "wizard",
        "artificer"
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
        self.adventure_board = self.server.get_channel(1142473807492304937)
        self.dice_roller = DiceRoller()
        
        gc = gspread.service_account(filename='service_account.json')
        sh = gc.open_by_key('14J14qZFMWu9-xNEPBQCJMyZr_waUvCGvzb7yQsXKnwg')
        self.ws = sh.get_worksheet(0)
        
        psh = gc.open_by_key('1q0843eIrQ68MekWvj79BKddHagjVpPgkHwqop-tA58A')
        self.pws = psh.get_worksheet(0)
           
        headers = self.ws.row_values(1)
        if not headers:
            i = 0
            for attr in dir(Player):
                if not attr.startswith("__"):
                    print(convertNumberToLetter(i), attr)
                    self.ws.update(f'{convertNumberToLetter(i)}1', attr)
                    i += 1
        
        self.update_users()

    async def update_player_post(self):
        p_id = self.pws.get('B1').first()
        if p_id:
            p_id = int(p_id)

        names = "\n".join(
            f'{user["User"].display_name}\t-\t{user["Player"].character_name}'
            for user in self.users.values()
            if user["Player"]
        )
        print(names)

        embed = discord.Embed(
            title="Játékos adatok",
            description="Ebben a listában találhattok hasznos információkat a regisztrált játékosokról!",
            colour=2899536,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )

        embed.add_field(name="Játékosok és karaktereik", value=names, inline=True)

        if p_id:
            self.player_post = await self.stats_channel.fetch_message(p_id)
            await self.player_post.edit(embed=embed)
        else:
            msg = await self.stats_channel.send(embed=embed)
            self.pws.update_cell(1, 2, str(msg.id))
            

    def update_users(self):
        all_users = self.server.members
        for user in all_users:
            if self.role in user.roles:
                if namecell := self.ws.find(user.name):
                    row = namecell.row
                    col = namecell.col
                    player = Player()
                    values = self.ws.row_values(row)
                    for attr in dir(player):
                        if not attr.startswith("__"):
                            print(attr, values[col-1])
                            setattr(player, attr, values[col-1])
                            col += 1
                    self.users[user.id] = {"User": user, "Player": player}
                else:
                    self.users[user.id] = {"User": user, "Player": None}
    
    async def update_player(self, username, player):
        if namecell := self.ws.find(username):
            row = namecell.row
            col = namecell.col
            for attr in dir(player):
                if not attr.startswith("__"):
                    print(attr, self.ws.cell(row, col).value)
                    self.ws.update_cell(row, col, getattr(player, attr))
                    col += 1


        self.update_player_post()
                    
    async def create_player(self, user, **kwargs):
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
        await self.update_player_post()
            
    def find_mission(self, name):
        return next( #Returns next form iterator (aka first element) or None if there are no elements
            (thread for thread in self.adventure_board.threads if thread.name == name),
            None,
        )
            
    async def post_mission(self, name, description, mission_type, difficulty, reward, location = None, time = None, player_range = (4,6), blacklist = None, whitelist = None):
        blacklist = blacklist.split(', ') if blacklist else []
        whitelist = whitelist.split(', ') if whitelist else []
        mission = Mission(name=name, description=description, mission_type=mission_type, difficulty=difficulty, reward=reward, location=location, time=time, player_range=player_range, blacklist=blacklist, whitelist=whitelist)
        await self.adventure_board.create_thread(name=name, embed=mission.to_embed())
    
    async def update_mission(self, name, description = None, mission_type = None, difficulty = None, reward = None, location = None, time = None, player_range = None, players = None, spectators = None, blacklist = None, whitelist = None):
        thread = self.find_mission(name)

        if not thread:
            return
        
        message = (await thread.history(limit=1,oldest_first=True).flatten())[0]
        mission = Mission.from_embed(message.embeds[0])
        
        if description: mission.description = description
        if mission_type: mission.mission_type = mission_type
        if difficulty: mission.difficulty = difficulty
        if reward: mission.reward = reward
        if location: mission.location = location
        if time: mission.time = time
        if player_range: mission.player_range = player_range
        if players: mission.players = players
        if spectators: mission.spectators = spectators
        if blacklist: mission.blacklist = blacklist
        if whitelist: mission.whitelist = whitelist
            
        await message.edit(embed=mission.to_embed())
    
    def find_player(self, name):
        return next(
            (user["Player"] for user in self.users.values() if user["Player"] and user["Player"].Player_Name == name),
            None
        )
    
    async def join_mission(self, user, message):
        mission = Mission.from_embed(message.embeds[0])
        max_players = mission.get_player_range()[1]
        players = mission.get_players()
        time = datetime.datetime.strptime(mission.time, "%Y-%m-%d")
        if time < datetime.datetime.now():
            return False
        if len(players) >= max_players:
            lastPlayed = datetime.datetime.strptime(self.find_player(user.name).last_played, "%Y-%m-%d")
            lastPlayedPlayer = None
            for player in players:
                if player == user.name:
                    return False
                playerLastPlayed = datetime.datetime.strptime(self.find_player(player).last_played, "%Y-%m-%d")
                if playerLastPlayed > lastPlayed:
                    lastPlayed = playerLastPlayed
                    lastPlayedPlayer = player
            
            if lastPlayedPlayer:
                mission.remove_player(lastPlayedPlayer)
                mission.add_player(user.name)
                await message.edit(embed=mission.to_embed())
                return True
            return False
        else:
            mission.add_player(user.name)
        
        await message.edit(embed=mission.to_embed())
        return True
    
    async def end_mission(self, message):
        mission = Mission.from_embed(message.embeds[0])
        players = mission.get_players()
        for player in players:
            playerObject = self.find_player(player)
            playerObject.games_played = int(playerObject.games_played) + 1
            playerObject.last_played = mission.time
            self.update_player(playerObject.Player_Name, playerObject)
    
    async def leave_mission(self, user, message):
        mission = Mission.from_embed(message.embeds[0])
        mission.remove_player(user.name)
        await message.edit(embed=mission.to_embed())
        return True
    
    async def spectate_mission(self, user, message):
        mission = Mission.from_embed(message.embeds[0])
        mission.add_spectator(user.name)
        await message.edit(embed=mission.to_embed())
        return True
    
    async def unspectate_mission(self, user, message):
        mission = Mission.from_embed(message.embeds[0])
        mission.remove_spectator(user.name)
        await message.edit(embed=mission.to_embed())
        return True
    
    def get_users(self):
        return self.users