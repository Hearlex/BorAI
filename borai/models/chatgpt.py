import os
from openai import OpenAI

from borai.memory.memory_base import MemoryBase
from borai.models.ai_interface import AIInterface

class ChatGPT(AIInterface):
    def __init__(self, system_prompt, model="gpt-3.5-turbo", temperature=0, memory: MemoryBase = None):
        super().__init__(system_prompt)
        
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
                        
        self.model = model
        self.temperature = temperature
        self.memory = memory

    def run(self, prompt):
        if not self.memory:
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
            messages = self.memory.recall()
            messages.append({
                "role": "user",
                "content": prompt
            })
        
        self.latest_response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=messages,
        )
        
        if self.memory:
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