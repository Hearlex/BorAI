from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type, Union
from autogen import ConversableAgent
from autogen.agentchat.agent import Agent
import asyncio
import discord
from termcolor import cprint
from collections import defaultdict
import warnings

from autogen.coding.factory import CodeExecutorFactory
from autogen.code_utils import content_str, decide_use_docker, check_can_use_docker_or_throw
from autogen.oai import OpenAIWrapper

from chat import ChatModule

TIME_TO_WAIT_FOR_REPLY = 60

class DiscordAgent(ConversableAgent):
    
    def __init__(self, name: str, is_termination_msg: Callable[[Dict], bool] | None = None, max_consecutive_auto_reply: int | None = None, human_input_mode: str | None = "ALWAYS", function_map: Dict[str, Callable[..., Any]] | None = None, code_execution_config: Dict | Literal[False] | None = None, default_auto_reply: str | Dict | None = "", llm_config: Dict | Literal[False] | None = False, system_message: str | List | None = "", description: str | None = None, chat: ChatModule | None = None):
        self.chat: ChatModule = chat
        self.current_channel: discord.TextChannel = None
        self.waiting_for_reply: bool = False
        self.replied_answer: str = ""
        
        self._name = name
        
        # a dictionary of conversations, default value is list
        self._oai_messages = defaultdict(list)
        self._oai_system_message = [{"content": system_message, "role": "system"}]
        self._description = description if description is not None else system_message
        self._is_termination_msg = (
            is_termination_msg
            if is_termination_msg is not None
            else (lambda x: content_str(x.get("content")) == "TERMINATE")
        )

        if llm_config is False:
            self.llm_config = False
            self.client = None
        else:
            self.llm_config = self.DEFAULT_CONFIG.copy()
            if isinstance(llm_config, dict):
                self.llm_config.update(llm_config)
            if "model" not in self.llm_config and (
                not self.llm_config.get("config_list")
                or any(not config.get("model") for config in self.llm_config["config_list"])
            ):
                raise ValueError(
                    "Please either set llm_config to False, or specify a non-empty 'model' either in 'llm_config' or in each config of 'config_list'."
                )
            self.client = OpenAIWrapper(**self.llm_config)

        # Initialize standalone client cache object.
        self.client_cache = None

        self.human_input_mode = human_input_mode
        self._max_consecutive_auto_reply = (
            max_consecutive_auto_reply if max_consecutive_auto_reply is not None else self.MAX_CONSECUTIVE_AUTO_REPLY
        )
        self._consecutive_auto_reply_counter = defaultdict(int)
        self._max_consecutive_auto_reply_dict = defaultdict(self.max_consecutive_auto_reply)
        self._function_map = (
            {}
            if function_map is None
            else {name: callable for name, callable in function_map.items() if self._assert_valid_name(name)}
        )
        self._default_auto_reply = default_auto_reply
        self._reply_func_list = []
        self._ignore_async_func_in_sync_chat_list = []
        self._human_input = []
        self.reply_at_receive = defaultdict(bool)
        self.register_reply([Agent, None], DiscordAgent.generate_oai_reply)
        self.register_reply([Agent, None], DiscordAgent.a_generate_oai_reply, ignore_async_in_sync_chat=True)

        # Setting up code execution.
        # Do not register code execution reply if code execution is disabled.
        if code_execution_config is not False:
            # If code_execution_config is None, set it to an empty dict.
            if code_execution_config is None:
                warnings.warn(
                    "Using None to signal a default code_execution_config is deprecated. "
                    "Use {} to use default or False to disable code execution.",
                    stacklevel=2,
                )
                code_execution_config = {}
            if not isinstance(code_execution_config, dict):
                raise ValueError("code_execution_config must be a dict or False.")

            # We have got a valid code_execution_config.
            self._code_execution_config = code_execution_config

            if self._code_execution_config.get("executor") is not None:
                # Use the new code executor.
                self._code_executor = CodeExecutorFactory.create(self._code_execution_config)
                self.register_reply([Agent, None], DiscordAgent._generate_code_execution_reply_using_executor)
            else:
                # Legacy code execution using code_utils.
                use_docker = self._code_execution_config.get("use_docker", None)
                use_docker = decide_use_docker(use_docker)
                check_can_use_docker_or_throw(use_docker)
                self._code_execution_config["use_docker"] = use_docker
                self.register_reply([Agent, None], DiscordAgent.generate_code_execution_reply)
        else:
            # Code execution is disabled.
            self._code_execution_config = False

        self.register_reply([Agent, None], DiscordAgent.generate_tool_calls_reply)
        self.register_reply([Agent, None], DiscordAgent.a_generate_tool_calls_reply, ignore_async_in_sync_chat=True)
        self.register_reply([Agent, None], DiscordAgent.generate_function_call_reply)
        self.register_reply(
            [Agent, None], DiscordAgent.a_generate_function_call_reply, ignore_async_in_sync_chat=True
        )
        self.register_reply([Agent, None], DiscordAgent.check_termination_and_human_reply)
        self.register_reply(
            [Agent, None], DiscordAgent.a_check_termination_and_human_reply, ignore_async_in_sync_chat=True
        )

        # Registered hooks are kept in lists, indexed by hookable method, to be called in their order of registration.
        # New hookable methods should be added to this list as required to support new agent capabilities.
        self.hook_lists = {
            "process_last_received_message": [],
            "process_all_messages_before_reply": [],
            "process_message_before_send": [],
        }

        
        
    async def a_receive(
        self,
        message: Union[Dict, str],
        sender: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        """(async) Receive a message from another agent.

        Once a message is received, this function sends a reply to the sender or stop.
        The reply can be generated automatically or entered manually by a human.

        Args:
            message (dict or str): message from the sender. If the type is dict, it may contain the following reserved fields (either content or function_call need to be provided).
                1. "content": content of the message, can be None.
                2. "function_call": a dictionary containing the function name and arguments. (deprecated in favor of "tool_calls")
                3. "tool_calls": a list of dictionaries containing the function name and arguments.
                4. "role": role of the message, can be "assistant", "user", "function".
                    This field is only needed to distinguish between "function" or "assistant"/"user".
                5. "name": In most cases, this field is not needed. When the role is "function", this field is needed to indicate the function name.
                6. "context" (dict): the context of the message, which will be passed to
                    [OpenAIWrapper.create](../oai/client#create).
            sender: sender of an Agent instance.
            request_reply (bool or None): whether a reply is requested from the sender.
                If None, the value is determined by `self.reply_at_receive[sender]`.
            silent (bool or None): (Experimental) whether to print the message received.

        Raises:
            ValueError: if the message can't be converted into a valid ChatCompletion message.
        """
        await self._process_received_message(message, sender, silent)
        if request_reply is False or request_reply is None and self.reply_at_receive[sender] is False:
            return
        reply = await self.a_generate_reply(sender=sender)
        if reply is not None:
            await self.a_send(reply, sender, silent=silent)
        
    async def _process_received_message(self, message: Union[Dict, str], sender: Agent, silent: bool):
        # When the agent receives a message, the role of the message is "user". (If 'role' exists and is 'function', it will remain unchanged.)
        valid = self._append_oai_message(message, "user", sender)
        if not valid:
            raise ValueError(
                "Received message can't be converted into a valid ChatCompletion message. Either content or function_call must be provided."
            )
        if not silent:
            self._print_received_message(message, sender)
            await self._send_recieved_message_to_discord(message, sender)
            
    async def _send_recieved_message_to_discord(self, message: Union[Dict, str], sender: Agent):
        # Send the received message to the discord channel
        await self.chat.sendChatToChannel(self.current_channel, message["content"])
        #asyncio.run(self.chat.sendChatToChannel(self.current_channel, message))
        print(f"Sent message to discord: {message['content']}")
        
    def set_current_channel(self, channel: discord.TextChannel):
        self.current_channel = channel
    
    def set_reply(self, reply: str):
        self.replied_answer = reply
        self.waiting_for_reply = False
        
    async def wait_for_reply(self):
        time_spent_waiting = 0
        cprint(f"Waiting for reply from user...", "yellow")
        while self.waiting_for_reply and time_spent_waiting < TIME_TO_WAIT_FOR_REPLY:
            await asyncio.sleep(1)
            time_spent_waiting += 1
        if time_spent_waiting >= TIME_TO_WAIT_FOR_REPLY:
            cprint(f"User did not reply within {TIME_TO_WAIT_FOR_REPLY} seconds.", "red")
            return None
        else:
            cprint(f"User replied: {self.replied_answer}", "green")
            return self.replied_answer
        
    async def a_check_termination_and_human_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[Any] = None,
    ) -> Tuple[bool, Union[str, None]]:
        """(async) Check if the conversation should be terminated, and if human reply is provided.

        This method checks for conditions that require the conversation to be terminated, such as reaching
        a maximum number of consecutive auto-replies or encountering a termination message. Additionally,
        it prompts for and processes human input based on the configured human input mode, which can be
        'ALWAYS', 'NEVER', or 'TERMINATE'. The method also manages the consecutive auto-reply counter
        for the conversation and prints relevant messages based on the human input received.

        Args:
            - messages (Optional[List[Dict]]): A list of message dictionaries, representing the conversation history.
            - sender (Optional[Agent]): The agent object representing the sender of the message.
            - config (Optional[Any]): Configuration object, defaults to the current instance if not provided.

        Returns:
            - Tuple[bool, Union[str, Dict, None]]: A tuple containing a boolean indicating if the conversation
            should be terminated, and a human reply which can be a string, a dictionary, or None.
        """
        if config is None:
            config = self
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]
        reply = ""
        no_human_input_msg = ""
        if self.human_input_mode == "ALWAYS":
            
            self.waiting_for_reply = True
            
            # Ide kell egy logika, ami várakoztatja a botot, amíg a felhasználó válaszol
            # Ha kap egy választ adott időn belül, akkor folytatja a működést
            # Ha nem kap választ adott időn belül, akkor befejezi a beszélgetést
            reply = await self.wait_for_reply()
            
            no_human_input_msg = "NO HUMAN INPUT RECEIVED." if not reply else ""
            # if the human input is empty, and the message is a termination message, then we will terminate the conversation
            reply = reply if reply or not self._is_termination_msg(message) else "exit"
            
            
            
        else:
            if self._consecutive_auto_reply_counter[sender] >= self._max_consecutive_auto_reply_dict[sender]:
                if self.human_input_mode == "NEVER":
                    reply = "exit"
                else:
                    # self.human_input_mode == "TERMINATE":
                    terminate = self._is_termination_msg(message)
                    reply = await self.a_get_human_input(
                        f"Please give feedback to {sender.name}. Press enter or type 'exit' to stop the conversation: "
                        if terminate
                        else f"Please give feedback to {sender.name}. Press enter to skip and use auto-reply, or type 'exit' to stop the conversation: "
                    )
                    no_human_input_msg = "NO HUMAN INPUT RECEIVED." if not reply else ""
                    # if the human input is empty, and the message is a termination message, then we will terminate the conversation
                    reply = reply if reply or not terminate else "exit"
            elif self._is_termination_msg(message):
                if self.human_input_mode == "NEVER":
                    reply = "exit"
                else:
                    # self.human_input_mode == "TERMINATE":
                    reply = await self.a_get_human_input(
                        f"Please give feedback to {sender.name}. Press enter or type 'exit' to stop the conversation: "
                    )
                    no_human_input_msg = "NO HUMAN INPUT RECEIVED." if not reply else ""
                    # if the human input is empty, and the message is a termination message, then we will terminate the conversation
                    reply = reply or "exit"

        # print the no_human_input_msg
        if no_human_input_msg:
            print(cprint(f"\n>>>>>>>> {no_human_input_msg}", "red"), flush=True)

        # stop the conversation
        if reply == "exit":
            # reset the consecutive_auto_reply_counter
            self._consecutive_auto_reply_counter[sender] = 0
            return True, None

        # send the human reply
        if reply or self._max_consecutive_auto_reply_dict[sender] == 0:
            # User provided a custom response, return function and tool results indicating user interruption
            # reset the consecutive_auto_reply_counter
            self._consecutive_auto_reply_counter[sender] = 0
            tool_returns = []
            if message.get("function_call", False):
                tool_returns.append(
                    {
                        "role": "function",
                        "name": message["function_call"].get("name", ""),
                        "content": "USER INTERRUPTED",
                    }
                )

            if message.get("tool_calls", False):
                tool_returns.extend(
                    [
                        {"role": "tool", "tool_call_id": tool_call.get("id", ""), "content": "USER INTERRUPTED"}
                        for tool_call in message["tool_calls"]
                    ]
                )

            response = {"role": "user", "content": reply}
            if tool_returns:
                response["tool_responses"] = tool_returns

            return True, response

        # increment the consecutive_auto_reply_counter
        self._consecutive_auto_reply_counter[sender] += 1
        if self.human_input_mode != "NEVER":
            print(cprint("\n>>>>>>>> USING AUTO REPLY...", "red"), flush=True)

        return False, None
    