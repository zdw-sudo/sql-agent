import asyncio
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import aiosqlite
import pytest

from app.config import Settings
from app.db.connection import seed_file_path


@pytest.fixture(scope="session")
def test_settings(tmp_path_factory) -> Settings:
    db_path = tmp_path_factory.mktemp("data") / "test.db"
    return Settings(database_path=str(db_path), deepseek_api_key="test-key")


@pytest.fixture(scope="session", autouse=True)
def init_db(test_settings: Settings):
    async def setup() -> None:
        test_settings.db_path.parent.mkdir(parents=True, exist_ok=True)
        seed_sql = seed_file_path().read_text(encoding="utf-8")
        conn = await aiosqlite.connect(test_settings.db_path)
        conn.row_factory = aiosqlite.Row
        await conn.executescript(seed_sql)
        await conn.commit()
        await conn.close()

    asyncio.run(setup())

    import app.config as config_module

    config_module.get_settings.cache_clear()

    @lru_cache
    def patched_get_settings() -> Settings:
        return test_settings

    original = config_module.get_settings
    config_module.get_settings = patched_get_settings
    yield
    config_module.get_settings = original
    config_module.get_settings.cache_clear()
