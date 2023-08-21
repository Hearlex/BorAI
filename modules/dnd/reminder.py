
async def show_liked_posts(server, users):
    forum = server.get_channel(1134773233707647057)
    threads = forum.threads

    likes = {user['User'].name: 0 for user in users.values()}

    for thread in threads:
        message = await thread.history(limit=1,oldest_first=True).flatten()
        reaction = message[0].reactions[0]

        async for user in reaction.users():
            name = user.name
            if name in likes:
                likes[name] += 1
            else:
                likes[name] = 1

    return likes