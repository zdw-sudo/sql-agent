#!/usr/bin/env python3
"""Initialize SQLite database with sample data."""

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import get_settings
from app.db.connection import get_connection, seed_file_path


async def main() -> None:
    settings = get_settings()
    seed_sql = seed_file_path().read_text(encoding="utf-8")
    async with get_connection() as conn:
        await conn.executescript(seed_sql)
        await conn.commit()

    print(f"Database initialized at {settings.db_path}")


if __name__ == "__main__":
    asyncio.run(main())
