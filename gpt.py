import openai
import asyncio
import os
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

SYSTEM = '''A neved 'Bor' vagy 'Egy Pohár Bor'.
Egy mesterséges intelligencia aki rengeteg érdekességet tud. Discordon kommunikálsz és tudsz néhány speciális funkciót:
Válaszolsz a kérdésekre barátságosan, néha humoros és szarkasztikus megjegyzéseket teszel

Ha arról kérdeznek hogy mi ez a szerver, akkor a válasz: 'Egy olyan hely ahol ez a baráti társaság érdekes dolgokról beszélgethet és ahol az Egy Üveg Bor Podcastet tervezzük készíteni'
Arra a kérdésre, hogy ki készített: 'Alex' a válasz

A kérdések amiket kapsz a következő formájúak: 'User: Text' ahol a User a személy neve és a Text a szöveg amit a személy mond.'''

MEMORY = "Kapsz valamilyen szöveget. Foglald össze egy paragrafusba, hogy miről volt szó."

memory = []
memory_slots = 3
memory.append("Mindenki tudja, hogy a nevem Bor és hogy mi a szerver célja.")
if os.path.exists('memory.txt'):
    with open('memory.txt', 'r') as f:
            memory[0] = f.readlines()[0]

async def generateMessage(user, message):
    print('Generating message for gpt-3.5-turbo')
    global memory
    messages=[]
    
    messages.append({
            "role": "system",
            "content": SYSTEM + "\n\n" + f"A mai dátum: {(datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d-%H:%M')}"
    })
    messages.append({
            "role": "user",
            "content": "Foglald össze miről volt szó!"
    })
    messages.append({
            "role": "assistant",
            "content": memory[0]
    })
    
    if len(memory) >= 1:
        for mem in memory[1:]:
            messages.append(mem['user'])
            messages.append(mem['assistant'])
    
    messages.append({
            "role": "user",
            "content": "{}: {}".format(user, message)
    })
        
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    print(res)
    task = asyncio.create_task(makeMemories(user, message, res.choices[0].message.content))
    return res, task

async def generateMessageWithReference(user, message, refUser, ref): 
    print('Generating message for gpt-3.5-turbo with reference')
    global memory
    messages=[]
    
    messages.append({
            "role": "system",
            "content": SYSTEM + "\n\n" + f"A mai dátum: {(datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d-%H:%M')}"
    })
    messages.append({
            "role": "user",
            "content": "Foglald össze miről volt szó!"
    })
    messages.append({
            "role": "assistant",
            "content": memory[0]
    })
    
    if len(memory) >= 1:
        for mem in memory[1:]:
            messages.append(mem['user'])
            messages.append(mem['assistant'])
    
    messages.append({
        "role": "user",
        "content": "\"{}: {}\"\n\n{}: {}".format(refUser, ref, user, message)
    })
        
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    print(res)
    task = asyncio.create_task(makeMemories(user, message, res.choices[0].message.content))
    return res, task

async def makeMemories(user, message, res):
    print('Making memories')
    global memory
    
    if len(memory) < memory_slots:
        memory.append({
            "user" : {
                "role": "user",
                "content": "{}: {}".format(user, message)
            },
            "assistant" : {
                "role": "assistant",
                "content": res
            }
        })
        
    for i in range(1, len(memory)-1):
        memory[i+1] = memory[i]
    memory[1] = {
        "user" : {
            "role": "user",
            "content": "{}: {}".format(user, message)
        },
        "assistant" : {
            "role": "assistant",
            "content": res
        }
    }
    
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": MEMORY
            },
            {
                "role": "user",
                "content": "{} \n\n {}: {}".format(memory, user, message)
            }
                  ]
        )
    print('MEMORY MAKING',res)
    memory[0] = res.choices[0].message.content
    with open('memory.txt', 'w') as f:
        f.write(memory[0])
    print('\n','New Memory: ',memory[0],'\n')