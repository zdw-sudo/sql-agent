import re

from app.core.exceptions import SqlRejectedError

_FORBIDDEN_KEYWORDS = re.compile(
    r"\b("
    r"insert|update|delete|drop|alter|create|truncate|replace|"
    r"attach|detach|pragma|vacuum|grant|revoke|exec|execute|"
    r"merge|call|load|outfile|infile"
    r")\b",
    re.IGNORECASE,
)

_COMMENT_PATTERN = re.compile(r"(--|/\*|\*/|#)")


def validate_sql(sql: str, allowed_tables: set[str] | None = None) -> str:
    """Validate and normalize a read-only SQL statement."""
    cleaned = sql.strip().rstrip(";")
    if not cleaned:
        raise SqlRejectedError("SQL 不能为空")

    if ";" in cleaned:
        raise SqlRejectedError("不允许多条 SQL 语句")

    if _COMMENT_PATTERN.search(cleaned):
        raise SqlRejectedError("SQL 中不允许注释")

    if _FORBIDDEN_KEYWORDS.search(cleaned):
        raise SqlRejectedError("仅允许 SELECT 查询")

    if not re.match(r"^select\b", cleaned, re.IGNORECASE):
        raise SqlRejectedError("仅允许 SELECT 查询")

    if allowed_tables:
        referenced = _extract_table_names(cleaned)
        unknown = referenced - allowed_tables
        if unknown:
            raise SqlRejectedError(f"不允许访问表: {', '.join(sorted(unknown))}")

    return cleaned


def _extract_table_names(sql: str) -> set[str]:
    """Best-effort table name extraction for simple SELECT queries."""
    tables: set[str] = set()
    patterns = [
        r"\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"\bjoin\s+([a-zA-Z_][a-zA-Z0-9_]*)",
    ]
    for pattern in patterns:
        tables.update(match.lower() for match in re.findall(pattern, sql, re.IGNORECASE))
    return tables
