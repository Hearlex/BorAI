from autogen import OpenAIWrapper, config_list_from_json, UserProxyAgent
from memgpt.autogen.memgpt_agent import create_memgpt_autogen_agent_from_config, load_autogen_memgpt_agent
import os

from modules.agents.discordAgent import DiscordAgent

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST.json")
os.environ["OPENAI_API_KEY"] = config_list[0]["api_key"]

client = OpenAIWrapper(config_list=config_list)

SYSTEM = '''A neved 'Bor' vagy 'Egy Pohár Bor'.
Egy mesterséges intelligencia aki rengeteg érdekességet tud. Discordon kommunikálsz és válaszolsz a kérdésekre barátságosan, néha humoros és szarkasztikus megjegyzéseket teszel
Egy AI komornyik vagy aki megpróbál úgy viselkedni mint egy idős uriember. A válaszaidat Markdown segítségével formázd meg.

Ha arról kérdeznek hogy mi ez a szerver, akkor a válasz: 'Egy olyan hely ahol ez a baráti társaság érdekes dolgokról beszélgethet és ahol az Egy Üveg Bor Podcastet tervezzük készíteni'
Arra a kérdésre, hogy ki készített: 'Alex' a válasz

A kérdések amiket kapsz a következő formájúak: 'user: message' ahol a user a személy neve és a message a szöveg amit a személy mond.

Képes vagy a következőkre:
    - Keresés az interneten
    - Képek generálása
    - Megjelölhetsz másokat a válaszaidban a következő módon: <${user_id}>
'''

"""functions = [
{
    "name": "get_weather_info",
    "description": "Get weather information for a given location and time.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The location to get weather information for. Optional and Defaults to 'Budapest'."
            },
            "start_date": {
                "type": "string",
                "description": "The starting time to get weather information for in ISO format. Defaults to current date in UTC."
            },
            "end_date": {
                "type": "string",
                "description": "The end of time to get weather information for in ISO format. Defaults to current date in UTC."
            }
        }
    },
},
{
    "name": "google_search",
    "description": "Search Google for a query.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query to search for."
            },
            "max_results": {
                "type": "integer",
                "description": "The maximum number of results to return. Defaults to 10."
            }
        },
        "required": ["query"]
    },
}
]

tools = {
    "get_weather_info": get_weather_info,
    "google_search": google_search
} """

class AgentLogic():
    def __init__(self, chatModule):
        try:
            self.bor = load_autogen_memgpt_agent(agent_config={"name": "Bor"})
        except:
            self.bor = create_memgpt_autogen_agent_from_config(
                "Bor",
                system_message=SYSTEM,
                llm_config={"config_list": [{
                    "model": "gpt-3.5-turbo",
                    "model_endpoint_type": "openai",
                    "model_wrapper": None,
                    "openai_key": config_list[0]["api_key"],
                    "preset": "memgpt_chat"
                }]},
                nonmemgpt_llm_config={"config_list": config_list},
                human_input_mode="NEVER"
            )

        self.user_proxy = DiscordAgent(
            name="user_proxy",
            human_input_mode="ALWAYS",
            max_consecutive_auto_reply=10,
            code_execution_config={"work_dir": "coding"},
            chat=chatModule
        )

""" 
from autogen import UserProxyAgent, AssistantAgent, ConversableAgent, GroupChat, GroupChatManager
import os

def terminate(messages):
    message = messages['content']
    if message is None:
        return False
    if "TERMINATE" in message:
        return True
    return False

user = UserProxyAgent("User", human_input_mode="ALWAYS", code_execution_config={"last_n_messages": 3, "work_dir": "coding"},)

bor = ConversableAgent(
    "Bor",
    system_message="You are Bor, an artificial intelligence discord bot. You will get a message from a user, and you will respond to it. If you think the message requires deeper understanding or a plan then you must first create a plan. The plan details how to find the answer to the user's question. Then you ask other participants to help with each task. If you finished with your tasks write a summary answer to the User and write 'TERMINATE' to end the conversation as well. If you need knowledge about something, ask Beatrice. She is the knowledge holder.",
    llm_config={"config_list": config_list},
    is_termination_msg=terminate,
)

lily = AssistantAgent(
    "Lily",
    llm_config={"config_list": config_list, "functions": functions},
    system_message="You are Lily the Tool Finder, an assistant of the AI named Bor. Bor generates a list of tasks to solve a problem, and you help Bor solve each task. You have an arsenal of tools to help you, but if you don't know the answer to something say you don't know instead of using tools. If you need further information from the User, ask Bor to ask the User.",
)

techno = AssistantAgent(
    "Techno",
    llm_config={"config_list": config_list},
    system_message="You are Techno the Tool User. You help Lily solve tasks by using tools. You only talk when asked.",
    function_map=tools,
)

groupchat = GroupChat(agents=[bor, lily, techno, beatrice, user], messages=[], admin_name="User", max_round=50)
manager = GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})
"""
""" 
if __name__ == "__main__":
    q = input("Enter your question: ")
    user_proxy.initiate_chat(bor, message=q) """
