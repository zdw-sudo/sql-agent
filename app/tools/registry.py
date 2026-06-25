import json
from typing import Any

from app import config
from app.core.exceptions import SqlExecutionError, SqlRejectedError
from app.core.sql_guard import validate_sql
from app.db import connection as db
from app.tools.base import Tool


class ListTablesTool(Tool):
    name = "list_tables"
    description = "列出数据库中所有可查询的业务表名。"

    def schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        }

    async def run(self, **_kwargs: Any) -> str:
        tables = await db.list_tables()
        return json.dumps({"tables": tables}, ensure_ascii=False)


class GetSchemaTool(Tool):
    name = "get_schema"
    description = "获取指定表的字段结构，包括字段名、类型和是否主键。"

    def schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table": {
                            "type": "string",
                            "description": "表名，例如 users / products / orders",
                        }
                    },
                    "required": ["table"],
                },
            },
        }

    async def run(self, table: str = "", **_kwargs: Any) -> str:
        if not table:
            return json.dumps({"error": "缺少 table 参数"}, ensure_ascii=False)

        allowed = set(await db.list_tables())
        if table not in allowed:
            return json.dumps(
                {"error": f"表 {table} 不存在", "available_tables": sorted(allowed)},
                ensure_ascii=False,
            )

        schema = await db.get_table_schema(table)
        return json.dumps({"table": table, "columns": schema}, ensure_ascii=False)


class RunSqlTool(Tool):
    name = "run_sql"
    description = "执行只读 SELECT 查询并返回结果。复杂问题请先调用 get_schema 了解表结构。"

    def schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "合法的 SELECT 语句",
                        }
                    },
                    "required": ["sql"],
                },
            },
        }

    async def run(self, sql: str = "", **_kwargs: Any) -> str:
        if not sql:
            return json.dumps({"error": "缺少 sql 参数"}, ensure_ascii=False)

        settings = config.get_settings()
        allowed_tables = set(await db.list_tables())

        try:
            safe_sql = validate_sql(sql, allowed_tables=allowed_tables)
            columns, rows = await db.execute_select(safe_sql, settings.sql_max_rows)
            return json.dumps(
                {"sql": safe_sql, "columns": columns, "rows": rows, "row_count": len(rows)},
                ensure_ascii=False,
            )
        except SqlRejectedError as exc:
            return json.dumps({"error": str(exc), "sql": sql}, ensure_ascii=False)
        except Exception as exc:
            raise SqlExecutionError(str(exc)) from exc


class FormatResultTool(Tool):
    name = "format_result"
    description = "将 SQL 查询结果整理成面向用户的自然语言回答。"

    def schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "answer": {
                            "type": "string",
                            "description": "最终中文回答，需引用关键数据",
                        },
                        "sql": {
                            "type": "string",
                            "description": "用于得出答案的 SQL",
                        },
                    },
                    "required": ["answer", "sql"],
                },
            },
        }

    async def run(self, answer: str = "", sql: str = "", **_kwargs: Any) -> str:
        return json.dumps({"answer": answer, "sql": sql}, ensure_ascii=False)


def get_tool_registry() -> dict[str, Tool]:
    tools: list[Tool] = [ListTablesTool(), GetSchemaTool(), RunSqlTool(), FormatResultTool()]
    return {tool.name: tool for tool in tools}


def get_openai_tools() -> list[dict]:
    return [tool.schema() for tool in get_tool_registry().values()]
