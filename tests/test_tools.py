import pytest

from app.tools.registry import GetSchemaTool, ListTablesTool, RunSqlTool


@pytest.mark.asyncio
async def test_list_tables(init_db) -> None:
    result = await ListTablesTool().run()
    assert "users" in result
    assert "products" in result
    assert "orders" in result


@pytest.mark.asyncio
async def test_get_schema(init_db) -> None:
    result = await GetSchemaTool().run(table="orders")
    assert "amount" in result


@pytest.mark.asyncio
async def test_run_sql(init_db) -> None:
    result = await RunSqlTool().run(sql="SELECT COUNT(*) AS cnt FROM users")
    assert '"cnt"' in result or "cnt" in result
