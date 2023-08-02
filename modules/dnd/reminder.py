
async def show_liked_posts(server, users):
    forum = server.get_channel(1134773233707647057)
    threads = forum.threads
    
    likes = {}
    
    for user in users.values():
        likes[user['User'].name] = 0
    
    for thread in threads:
        message = await thread.history(limit=1,oldest_first=True).flatten()
        reaction = message[0].reactions[0]
        
        async for user in reaction.users():
            name = user.name
            if name in likes.keys():
                likes[name] += 1
            else:
                likes[name] = 1
    
    return likes