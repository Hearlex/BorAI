from abc import ABC, abstractmethod
from typing import Any, List

from borai.memory.memory import Memory


class MemoryConverter(ABC):
    @abstractmethod
    def to_memories(self, data: Any) -> List[Memory]:
        pass

    @abstractmethod
    def from_memories(self, memories: List[Memory]) -> Any:
        pass