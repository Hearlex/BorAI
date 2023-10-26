from autogen import config_list_from_json, UserProxyAgent, AssistantAgent, ConversableAgent, GroupChat, GroupChatManager
import os

from tools import get_weather_info, google_search

""" print(os.getcwd())
print(os.path.exists("OAI_CONFIG_LIST.json")) """

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST.json")

functions = [
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
}

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
    system_message="You are Bor, an artificial intelligence discord bot. You will get a message from a user, and you will respond to it. First you create a plan. The plan details how to find the answer to the user's question. Then you ask other participants to help with each task. If you finished with your tasks write a summary answer to the User and write 'TERMINATE' to end the conversation as well.",
    llm_config={"config_list": config_list},
    is_termination_msg=terminate,
)

lily = AssistantAgent("Lily",
    llm_config={"config_list": config_list, "functions": functions},
    system_message="You are Lily the Tool Finder, an assistant of the AI named Bor. Bor generates a list of tasks to solve a problem, and you help Bor solve each task. You have an arsenal of tools to help you, but if you don't know the answer to something say you don't know instead of using tools. If you need further information from the User, ask Bor to ask the User.",
)

techno = AssistantAgent("Techno",
    llm_config={"config_list": config_list},
    system_message="You are Techno the Tool User. You help Lily solve tasks by using tools. You only talk when asked.",
    function_map=tools,
)


groupchat = GroupChat(agents=[bor, lily, techno, user], messages=[], admin_name="User", max_round=50)
manager = GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})

if __name__ == "__main__":
    question = input(">>> ")
    user.initiate_chat(manager, message=question)
