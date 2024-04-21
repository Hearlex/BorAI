from typing import Any, List
from borai.memory.converters.converter import MemoryConverter
from borai.memory.memory import Memory


class OpenAIConverter(MemoryConverter):
    def to_memories(self, data) -> List[Memory]:
        memories = []
        for message in data:
            memory = Memory()
            memory.role = message["role"]
            memory.content = message["content"]
            memories.append(memory)
        return memories

    def from_memories(self, memories: List[Memory]) -> Any:
        data = []
        for memory in memories:
            data.append({
                "role": memory.role,
                "content": memory.content
            })
        return data