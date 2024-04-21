from borai.memory.memory import Memory
from borai.memory.memory_base import MemoryBase

class NMemory(MemoryBase):
    def __init__(self, system_prompt, converter, n=4):
        super().__init__(system_prompt=system_prompt, converter=converter)
        self.n = n

    def remember(self, messages):
        memory = self.model_converter.to_memories(messages)
        if len(self.memory)+len(memory) >= self.n:
            for i in range(len(self.memory)+len(memory)-self.n):
                self.memory.pop(0)
        self.memory += memory

    def recall(self):
        system_memory = Memory()
        system_memory.role = "system"
        system_memory.content = self.system_prompt
        
        all_memories = [system_memory] + self.memory
        memories = self.model_converter.from_memories(all_memories)
        return memories