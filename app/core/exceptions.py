class AgentError(Exception):
    """Base agent error."""


class SqlRejectedError(AgentError):
    """SQL failed security validation."""


class SqlExecutionError(AgentError):
    """SQL execution failed at the database layer."""
