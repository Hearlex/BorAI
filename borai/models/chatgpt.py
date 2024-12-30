import inspect
import json
from openai import OpenAI
from termcolor import cprint

from borai.memory.memory_base import MemoryBase
from borai.models.ai_interface import AIInterface
from borai.misc.functions import getenv

class ChatGPT(AIInterface):
    def __init__(self, system_prompt, model="gpt-4o", temperature=0, memory: MemoryBase = None, tools=None):
        super().__init__(system_prompt)
        
        # Initialize OpenAI client with API key from environment variables
        self.client = OpenAI(
            api_key=getenv("OPENAI_API_KEY")
        )
        # Set the model, temperature, and memory configurations
        self.model = model
        self.temperature = temperature
        self.memory = memory
        self.tools = tools
        self.tool_calling_list = []
        
        # Lookup if tools are available and add them to the messages
        if self.tools:
            for tool in self.tools:
                sign = inspect.signature(tool.run)
                print(str(sign))
                
                name = tool.name
                description = tool.description
                params = [x for x in sign.parameters.values()]
                
                # Add the tool to the list of tools
                tool_desc = {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": description,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                param.name: {
                                    "type": "string",
                                    "description": str(param.annotation),
                                } for param in params
                            },
                            "required": [param.name for param in params], #TODO: Filter out optionals
                            "additionalProperties": False
                        }
                    }
                }
                self.tool_calling_list.append(tool_desc)
                cprint(f"Registering tool for {name}, {description}, {params}", "light_green")

    def handle_tool(self, response, messages):
        # Check if the response is a tool call
        if response.choices[0].finish_reason == "tool_calls":
            # Get the tool name and parameters
            tool_call = response.choices[0].message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_params = json.loads(tool_call.function.arguments)
            print(f"Tool call: {tool_name}, {tool_params}")
            # Find the tool object by name
            tool = next((t for t in self.tools if t.name == tool_name), None)
            if tool:
                # Call the tool's run method with the parameters
                tool_response = tool.run(**tool_params)
                # Create a new message with the tool's response
                function_call_result_message = {
                    "role": "tool",
                    "content": json.dumps(tool_response),
                    "tool_call_id": response.choices[0].message.tool_calls[0].id
                }
            
            messages.append(
                {
                    "role": "assistant",
                    "tool_calls": [
                        response.choices[0].message.tool_calls[0]
                    ]
                }
            )
            messages.append(function_call_result_message)
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=messages,
                tools=self.tool_calling_list
            )
            return self.handle_tool(response, messages)
        
        # If the response is not a tool call, return the response
        return response

    def run(self, prompt):
        if not self.memory:
            # Create initial messages with system prompt and user prompt
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        else:
            # Retrieve messages from memory and append the new user prompt
            messages = self.memory.recall()
            messages.append({
                "role": "user",
                "content": prompt
            })
                
        
        # Generate a response using OpenAI's chat completion API
        self.latest_response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=messages,
            tools=self.tool_calling_list
        )
        
        self.latest_response = self.handle_tool(self.latest_response, messages)
        
        if self.memory:
            # Store the user prompt and the AI's response in memory
            memories = [
                {
                    "role": "user",
                    "content": prompt
                },
                {
                    "role": self.latest_response.choices[0].message.role,
                    "content": self.latest_response.choices[0].message.content
                }
            ]
            self.memory.remember(memories)
        
        return self.latest_response.choices[0].message.content
    
    def run_with_image(self, prompt, images):
        
        # Prepare contents with text prompt
        contents = [
            {
                "type": "text",
                "text": prompt
            }
        ]
        
        for image in images:
            # Add image URLs with details to contents
            contents.append({
                "type": "image_url",
                "image_url": {
                    "url": str(image),
                    "detail": "low"
                }
            })
            
        
        if not self.memory:
            # Create messages with system prompt and user contents
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": contents
                }
            ]
        else:
            # Retrieve messages from memory and append new user contents
            messages = self.memory.recall()
            messages.append({
                "role": "user",
                "content": contents
            })
        
        # Generate a response with images using OpenAI's chat completion API
        self.latest_response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=messages,
            tools=self.tool_calling_list
        )
        
        self.latest_response = self.handle_tool(self.latest_response, messages)
        
        if self.memory:
            # Store the user prompt and the AI's response in memory
            memories = [
                {
                    "role": "user",
                    "content": prompt
                },
                {
                    "role": self.latest_response.choices[0].message.role,
                    "content": self.latest_response.choices[0].message.content
                }
            ]
            self.memory.remember(memories)
        
        return self.latest_response.choices[0].message.content