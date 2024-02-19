from enum import Enum

import uvicorn
from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel




# Global data
users = []
countries = {
        "españa": {"performance": 0, "meme": 0, "vote_count": 0},
        "francia": {"performance": 0, "meme": 0, "vote_count": 0},
        "alemania": {"performance": 0, "meme": 0, "vote_count": 0},
}

app = FastAPI()

# avoid CORS error
origins = [
    "file:///home/crisber/Projects/eurotest/src/eurotest/html/index.html",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# REQUIREMENTS
# 1. Votar la actuacion (post, con confirmacion)
# 2. Ver ranking (get, posibilidad de refescar)
# 3. Cambiar pais actual: que se cambie TODO no sabemos los paises todavia, que sea facil agregar nuevos
# 4. Login: user, pass. En principio creamos nosotros los usuarios desde admin.


class Events(Enum):
    CONNECTION = "connect"
    UPDATE_USER_LIST = "update-user-list"


class Vote(BaseModel):
    username: str
    country: str
    performance: int
    meme: int


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@app.post("/vote/")
async def vote(vote: Vote): 
    # TODO use the database
    countries[vote.country]["performance"] += vote.performance
    countries[vote.country]["meme"] += vote.meme
    countries[vote.country]["vote_count"] += 1

    # change user vote state (already voted)
    for user in users:
        if user.name == vote.username:
            user.vote = True
            break

    # broadcast the connection to all users in the lobby
    # REFACTOR: duplicate function in websocket endpoint
    await manager.broadcast(
        {"type": Events.UPDATE_USER_LIST.value, "message": users}
    )

    return vote


@app.get("/ranking")
async def get_ranking(): ...


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # el client_id que sirva para recuperar los datos de la BD
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            datatype = data["type"]
            message = data["message"]
            match datatype:
                case Events.CONNECTION.value:
                    # TODO do this with the database
                    users.append(message)

                    # broadcast the connection to all users in the lobby
                    await manager.broadcast(
                        {"type": Events.UPDATE_USER_LIST.value, "message": users}
                    )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # lo que se hace cuando se desconecta el usuario


def run():
    uvicorn.run("eurotest.main:app", port=5000, reload=True, log_level="info")
