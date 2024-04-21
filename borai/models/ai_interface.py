from abc import ABC, abstractmethod

class AIInterface(ABC):
    def __init__(self, system_prompt, memory=None):
        self.system_prompt = system_prompt
        self.latest_response = None
        self.memory = memory
        
    @abstractmethod
    def run(self, prompt):
        pass