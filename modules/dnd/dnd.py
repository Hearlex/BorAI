from modules.dnd.reminder import show_liked_posts

class DnD:
    users = {}
    server = None
    role = None

    def __init__(self, bot):
        self.server = bot.get_guild(1084891853758935141)
        self.role = self.server.get_role(1134772402820239370)
        self.update_users()

    def update_users(self):
        all_users = self.server.members
        for user in all_users:
            if self.role in user.roles:
                self.users[user.id] = {"User": user}
        
    def get_users(self):
        return self.users
    
    async def show_likes(self):
        self.update_users()
        return await show_liked_posts(self.server, self.users)