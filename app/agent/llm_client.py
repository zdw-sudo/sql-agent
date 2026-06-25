import json
from typing import Any

from openai import AsyncOpenAI

from app.config import Settings


class DeepSeekClient:
    """Thin wrapper around DeepSeek's OpenAI-compatible chat API."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict] | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {
            "model": self.settings.deepseek_model,
            "messages": messages,
            "temperature": 0.1,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        return await self.client.chat.completions.create(**kwargs)

    @staticmethod
    def message_to_dict(message: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "role": message.role,
            "content": message.content or "",
        }
        if message.tool_calls:
            payload["tool_calls"] = [
                {
                    "id": call.id,
                    "type": call.type,
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in message.tool_calls
            ]
        return payload

    @staticmethod
    def parse_tool_args(raw: str) -> dict[str, Any]:
        try:
            return json.loads(raw or "{}")
        except json.JSONDecodeError:
            return {"_raw": raw}
