from abc import ABC, abstractmethod
from borai.memory.converters.converter import MemoryConverter

class MemoryBase(ABC):
    def __init__(self, system_prompt, converter):
        self.system_prompt: str = system_prompt
        self.model_converter: MemoryConverter = converter
        self.memory = []
        
    @abstractmethod
    def remember(self, message):
        pass
    
    @abstractmethod
    def recall(self):
        pass