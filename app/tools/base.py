from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    name: str
    description: str

    @abstractmethod
    def schema(self) -> dict[str, Any]:
        """OpenAI function-calling schema."""

    @abstractmethod
    async def run(self, **kwargs: Any) -> str:
        """Execute tool and return observation string."""
