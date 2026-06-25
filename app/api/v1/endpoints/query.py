import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agent.react_loop import ReActAgent
from app.config import get_settings
from app.core.exceptions import AgentError
from app.schemas.request import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(payload: QueryRequest) -> QueryResponse:
    settings = get_settings()
    if payload.max_steps:
        settings = settings.model_copy(update={"max_agent_steps": payload.max_steps})

    agent = ReActAgent(settings)
    try:
        result = await agent.run(payload.question)
    except AgentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent 执行失败: {exc}") from exc

    return QueryResponse(**result)


@router.post("/query/stream")
async def query_stream(payload: QueryRequest) -> StreamingResponse:
    settings = get_settings()
    if payload.max_steps:
        settings = settings.model_copy(update={"max_agent_steps": payload.max_steps})

    agent = ReActAgent(settings)

    async def event_generator():
        try:
            async for event in agent.run_stream(payload.question):
                yield f"event: {event['event']}\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n"
        except AgentError as exc:
            payload_err = {"detail": str(exc)}
            yield f"event: error\ndata: {json.dumps(payload_err, ensure_ascii=False)}\n\n"
        except Exception as exc:
            payload_err = {"detail": f"Agent 执行失败: {exc}"}
            yield f"event: error\ndata: {json.dumps(payload_err, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
