from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500, examples=["销量最高的3个产品是什么？"])
    max_steps: int | None = Field(default=None, ge=1, le=10)


class AgentStep(BaseModel):
    step: int
    type: str
    tool: str | None = None
    input: dict | None = None
    observation: str | None = None
    content: str | None = None


class QueryResponse(BaseModel):
    trace_id: str
    question: str
    answer: str
    sql: str
    rows: list[dict]
    steps: list[dict]
    latency_ms: int
