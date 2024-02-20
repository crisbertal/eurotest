# REFACTOR
# - [ ] make different apps for API and Static

import os
from enum import Enum

import uvicorn
from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# Global data
class Events(Enum):
    CONNECTION = "connect"
    UPDATE_USER_LIST = "update-user-list"


class Vote(BaseModel):
    username: str
    country: str
    performance: int
    meme: int


class Country(BaseModel):
    performance: int
    meme: int
    vote_count: int


class CountryRanking(BaseModel):
    country: str
    mean_performance: float
    mean_meme: float


users = []
countries = {
    "es": Country(performance=0, meme=0, vote_count=0),
    "fr": Country(performance=0, meme=0, vote_count=0),
    "de": Country(performance=0, meme=0, vote_count=0),
}

app = FastAPI()

origins = [
    "http://localhost",
    "http://127.0.0.1",
]

# TODO: dont leave the cors open to all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=origins,
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# resolve error by relative paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")


# REQUIREMENTS
# - [x] Votar la actuacion (post, con confirmacion)
# - [x] Ver ranking (get, posibilidad de refescar)
# - [ ] Cambiar pais actual: que se cambie TODO no sabemos los paises todavia, que sea facil agregar nuevos
# - [ ] Login: user, pass. En principio creamos nosotros los usuarios desde admin.


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


@app.get("/")
def index():
    return RedirectResponse(url="/static/html/index.html")


@app.post("/vote/")
async def vote(vote: Vote) -> Vote:
    # TODO use the database
    countries[vote.country].performance += vote.performance
    countries[vote.country].meme += vote.meme
    countries[vote.country].vote_count += 1

    # change user vote state (already voted)
    for user in users:
        if user["name"] == vote.username:
            user["vote"] = True
            break

    # broadcast the connection to all users in the lobby
    # REFACTOR: duplicate function in websocket endpoint
    await manager.broadcast(
        {"type": Events.UPDATE_USER_LIST.value, "message": users}
    )

    return vote


@app.get("/ranking")
async def get_ranking() -> list[CountryRanking]:
    # TODO use the database
    # TODO only get those countries that have been played or playing
    result = []
    for name, country in countries.items():
        # if the country has no votes
        if country.vote_count == 0:
            break
        mean_performance = country.performance / country.vote_count
        mean_meme = country.meme / country.vote_count
        result.append(
            CountryRanking(
                country=name,
                mean_performance=mean_performance,
                mean_meme=mean_meme,
            )
        )
    return result


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
                    user = message
                    # TODO do this with the database
                    users.append(user)

                    # broadcast the connection to all users in the lobby
                    await manager.broadcast(
                        {"type": Events.UPDATE_USER_LIST.value, "message": users}
                    )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # lo que se hace cuando se desconecta el usuario


def run():
    uvicorn.run("eurotest.main:app", port=5000, reload=True, log_level="info")
