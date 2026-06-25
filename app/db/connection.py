import aiosqlite
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from app import config


@asynccontextmanager
async def get_connection() -> AsyncIterator[aiosqlite.Connection]:
    settings = config.get_settings()
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(settings.db_path) as conn:
        conn.row_factory = aiosqlite.Row
        yield conn


async def list_tables() -> list[str]:
    async with get_connection() as conn:
        cursor = await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        rows = await cursor.fetchall()
        return [row["name"] for row in rows]


async def get_table_schema(table: str) -> list[dict[str, str]]:
    async with get_connection() as conn:
        cursor = await conn.execute(f"PRAGMA table_info({table})")
        rows = await cursor.fetchall()
        return [
            {
                "cid": row["cid"],
                "name": row["name"],
                "type": row["type"],
                "notnull": row["notnull"],
                "pk": row["pk"],
            }
            for row in rows
        ]


async def execute_select(sql: str, max_rows: int) -> tuple[list[str], list[dict]]:
    async with get_connection() as conn:
        cursor = await conn.execute(sql)
        rows = await cursor.fetchmany(max_rows + 1)
        if len(rows) > max_rows:
            raise ValueError(f"结果超过 {max_rows} 行，请添加 LIMIT 或缩小查询范围")

        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        data = [dict(row) for row in rows]
        return columns, data


def seed_file_path() -> Path:
    return Path(__file__).resolve().parent / "seed.sql"
