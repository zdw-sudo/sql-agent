import json
import time
import uuid
from typing import Any, AsyncIterator

from app.agent.llm_client import DeepSeekClient
from app.agent.prompts import SYSTEM_PROMPT
from app.config import Settings
from app.core.exceptions import AgentError, SqlExecutionError
from app.tools.registry import get_openai_tools, get_tool_registry


class ReActAgent:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.llm = DeepSeekClient(settings)
        self.tools = get_tool_registry()

    async def run(self, question: str) -> dict[str, Any]:
        if not self.settings.deepseek_api_key:
            raise AgentError("未配置 DEEPSEEK_API_KEY，请复制 .env.example 为 .env 并填入密钥")

        trace_id = str(uuid.uuid4())
        started = time.perf_counter()
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]
        steps: list[dict[str, Any]] = []
        final_answer = ""
        final_sql = ""
        final_rows: list[dict[str, Any]] = []

        for step_idx in range(1, self.settings.max_agent_steps + 1):
            response = await self.llm.chat(messages, tools=get_openai_tools())
            message = response.choices[0].message
            assistant_msg = self.llm.message_to_dict(message)
            messages.append(assistant_msg)

            if not message.tool_calls:
                final_answer = (message.content or "").strip()
                steps.append({"step": step_idx, "type": "final", "content": final_answer})
                break

            for call in message.tool_calls:
                tool_name = call.function.name
                tool_args = self.llm.parse_tool_args(call.function.arguments)
                tool = self.tools.get(tool_name)
                if not tool:
                    observation = json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)
                else:
                    try:
                        observation = await tool.run(**tool_args)
                    except SqlExecutionError as exc:
                        observation = json.dumps({"error": str(exc)}, ensure_ascii=False)

                steps.append(
                    {
                        "step": step_idx,
                        "type": "tool_call",
                        "tool": tool_name,
                        "input": tool_args,
                        "observation": observation,
                    }
                )

                if tool_name == "run_sql":
                    payload = json.loads(observation)
                    if "sql" in payload and "error" not in payload:
                        final_sql = payload["sql"]
                        final_rows = payload.get("rows", [])

                if tool_name == "format_result":
                    payload = json.loads(observation)
                    final_answer = payload.get("answer", "")
                    final_sql = payload.get("sql", final_sql)
                    steps.append({"step": step_idx, "type": "formatted", "content": final_answer})
                    return self._build_result(
                        trace_id=trace_id,
                        question=question,
                        answer=final_answer,
                        sql=final_sql,
                        rows=final_rows,
                        steps=steps,
                        started=started,
                    )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": observation,
                    }
                )
        else:
            raise AgentError(f"Agent 超过最大步数 {self.settings.max_agent_steps}")

        return self._build_result(
            trace_id=trace_id,
            question=question,
            answer=final_answer,
            sql=final_sql,
            rows=final_rows,
            steps=steps,
            started=started,
        )

    async def run_stream(self, question: str) -> AsyncIterator[dict[str, Any]]:
        result = await self.run(question)
        for step in result["steps"]:
            yield {"event": "step", "data": step}
        if result.get("sql"):
            yield {"event": "sql", "data": {"sql": result["sql"]}}
        yield {"event": "done", "data": result}

    @staticmethod
    def _build_result(
        *,
        trace_id: str,
        question: str,
        answer: str,
        sql: str,
        rows: list[dict[str, Any]],
        steps: list[dict[str, Any]],
        started: float,
    ) -> dict[str, Any]:
        latency_ms = int((time.perf_counter() - started) * 1000)
        return {
            "trace_id": trace_id,
            "question": question,
            "answer": answer,
            "sql": sql,
            "rows": rows,
            "steps": steps,
            "latency_ms": latency_ms,
        }
