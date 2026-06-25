import pytest

from app.core.exceptions import SqlRejectedError
from app.core.sql_guard import validate_sql


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM users",
        "select u.name from users u join orders o on u.id = o.user_id",
    ],
)
def test_validate_sql_accepts_select(sql: str) -> None:
    assert validate_sql(sql, allowed_tables={"users", "orders"}).lower().startswith("select")


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM users",
        "SELECT * FROM users; DROP TABLE users",
        "INSERT INTO users VALUES (1, 'a', 'b', 'c')",
        "SELECT * FROM users -- comment",
    ],
)
def test_validate_sql_rejects_dangerous(sql: str) -> None:
    with pytest.raises(SqlRejectedError):
        validate_sql(sql, allowed_tables={"users"})


def test_validate_sql_rejects_unknown_table() -> None:
    with pytest.raises(SqlRejectedError):
        validate_sql("SELECT * FROM secrets", allowed_tables={"users"})
