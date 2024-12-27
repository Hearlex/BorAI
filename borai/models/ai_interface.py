from abc import ABC, abstractmethod

class AIInterface(ABC):
    def __init__(self, system_prompt, memory=None, tools=None):
        self.system_prompt = system_prompt
        self.latest_response = None
        self.memory = memory
        self.tools = tools
        
    @abstractmethod
    def run(self, prompt):
        pass
    
    @abstractmethod
    def run_with_image(self, prompt, images):
        pass