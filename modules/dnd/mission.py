import discord
import datetime

class Mission:
    def from_embed(embed):
        name = embed.title
        description = embed.description
        location = embed.fields[0].value
        difficulty = embed.fields[1].value
        reward = embed.fields[2].value
        time = embed.fields[3].value
        mission_type = embed.fields[4].value
        
        player_range = embed.fields[5].value.split('-')
        player_range = tuple((int(player_range[0]), int(player_range[1])))
        
        players = embed.fields[6].value
        if players != '':
            players = players.split(', ')
        else:
            players = []
            
        spectators = embed.fields[7].value
        if spectators != '':
            spectators = spectators.split(', ')
        else:
            spectators = []
            
        blacklist = embed.fields[8].value
        if blacklist != '':
            blacklist = blacklist.split(', ')
        else:
            blacklist = []
            
        whitelist = embed.fields[9].value
        if whitelist != '':
            whitelist = whitelist.split(', ')
        else:
            whitelist = []
            
        return Mission(name, description, location, difficulty, reward, time, mission_type, player_range, players, spectators, blacklist, whitelist)
    
    def __init__(self, name, description, location, difficulty, reward, time, mission_type, player_range = (4,6), players = [], spectators = [], blacklist = [], whitelist = []):
        self.name = name
        self.description = description
        self.type = mission_type
        self.difficulty = difficulty
        self.reward = reward
        self.location = location
        self.time = time
        self.player_range = player_range
        
        self.players = players
        self.spectators = spectators
        self.blacklist = blacklist
        self.whitelist = whitelist

    def __str__(self):
        return f"**{self.name}**\n*{self.description}*\n\n**Location:** {self.location}\n**Difficulty:** {self.difficulty}\n**Reward:** {self.reward}\n**Time:** {self.time}\n**Type:** {self.type}\n**Player Range:** {self.player_range}\n**Players:** {self.players}\n**Spectators:** {self.spectators}\n**Blacklist:** {self.blacklist}\n**Whitelist:** {self.whitelist}"

    def __repr__(self):
        return self.name

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def get_location(self):
        return self.location

    def get_difficulty(self):
        return self.difficulty

    def get_reward(self):
        return self.reward

    def get_time(self):
        return self.time

    def get_type(self):
        return self.type
    
    def add_player(self, player):
        print(player, self.whitelist, self.whitelist == [], self.players, self.blacklist)
        if player in self.whitelist or self.whitelist == []:
            if player in self.players:
                return True
            elif player in self.blacklist:
                return False
            else:
                self.players.append(player)
                return True
        
        return False
    
    def add_spectator(self, spectator):
        self.spectators.append(spectator)
        
    def remove_player(self, player):
        self.players.remove(player)
        
    def remove_spectator(self, spectator):
        self.spectators.remove(spectator)
    
    def get_player_range(self):
        return self.player_range
    
    def get_players(self):
        return self.players
    
    def to_embed(self):
        embed = discord.Embed(title=self.name, description=self.description, colour=2899536, timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Location", value=self.location, inline=True)
        embed.add_field(name="Difficulty", value=self.difficulty, inline=True)
        embed.add_field(name="Reward", value=self.reward, inline=True)
        embed.add_field(name="Time", value=self.time, inline=True)
        embed.add_field(name="Type", value=self.type, inline=True)
        embed.add_field(name="Player Range", value=f"{self.player_range[0]}-{self.player_range[1]}", inline=True)
        embed.add_field(name="Players", value=", ".join([player for player in self.players]), inline=True)
        embed.add_field(name="Spectators", value=", ".join([spectator for spectator in self.spectators]), inline=True)
        embed.add_field(name="Blacklist", value=", ".join([blacklist for blacklist in self.blacklist]), inline=True)
        embed.add_field(name="Whitelist", value=", ".join([whitelist for whitelist in self.whitelist]), inline=True)
        return embed

Mission.from_embed = staticmethod(Mission.from_embed)