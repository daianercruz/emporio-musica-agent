
from threading import Lock
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.agent import TeoAgent


app = FastAPI(
    title="Téo - Empório da Música",
    version="1.0.0"
)

sessions = {}
sessions_lock = Lock()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    response: str


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="A mensagem não pode estar vazia."
        )

    if request.session_id is not None:
        try:
            session_id = str(UUID(request.session_id))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Identificador de sessão inválido."
            )
    else:
        session_id = str(uuid4())

    with sessions_lock:
        if session_id not in sessions:
            sessions[session_id] = {
                "agent": TeoAgent(),
                "lock": Lock()
            }

        session = sessions[session_id]

    with session["lock"]:
        answer = session["agent"].chat(message)

    return ChatResponse(
        session_id=session_id,
        response=answer
    )


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)
