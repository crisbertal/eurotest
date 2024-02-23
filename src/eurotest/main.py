# REFACTOR
# - [ ] make different apps for API and Static
# - [ ] logging all request for server log

import os
from enum import Enum
import json

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
    NEXT_COUNTRY = "next-country"


class User(BaseModel):
    name: str
    vote: bool


class LoginResponse(BaseModel):
    user: User
    current_countr: str


class Vote(BaseModel):
    username: str
    performance: int
    meme: int


class Country(BaseModel):
    name: str
    performance: int
    meme: int
    vote_count: int


class CountryRanking(BaseModel):
    country: str
    mean_performance: float
    mean_meme: float


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
# - [x] Cambiar pais actual automatico: que se cambie TODO no sabemos los paises todavia, que sea facil agregar nuevos
# - [x] Cambiar pais actual por el admin
# - [ ] Login: user, pass. En principio creamos nosotros los usuarios desde admin.
# - [ ] Comportamiento en la desconexion de usuario
# - [ ] Mover el state a BD


class StateManager:
    users: list[User] = []
    countries: list[Country] = [
        Country(name="es", performance=0, meme=0, vote_count=0),
        Country(name="fr", performance=0, meme=0, vote_count=0),
        Country(name="de", performance=0, meme=0, vote_count=0),
        Country(name="be", performance=0, meme=0, vote_count=0),
        Country(name="po", performance=0, meme=0, vote_count=0),
        Country(name="en", performance=0, meme=0, vote_count=0),
        Country(name="ru", performance=0, meme=0, vote_count=0),
    ]
    # increment this value to get the next country
    _current_country: int = 0


    def get_current_country(self) -> Country:
        return self.countries[self._current_country]


    def set_next_country(self):
        self._current_country += 1


    def set_user_vote(self, name: str):
        for user in self.users:
            if user.name == name:
                user.vote = True
                break


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


state = StateManager()
manager = ConnectionManager()


@app.get("/")
def index():
    return RedirectResponse(url="/static/html/index.html")


@app.post("/login/")
async def login(user: User) -> dict:
    # TODO do the comprobation with DB of the login credentials
    # return user and current country
    return {"user": user, "country": state.get_current_country().name}


@app.post("/vote/")
async def vote(vote: Vote) -> Vote:
    # using global to avoid the "current_country is unbound"
    # global current_country
    current_country = state.get_current_country()

    # todo use the database
    current_country.performance += vote.performance
    current_country.meme += vote.meme
    current_country.vote_count += 1

    # change user vote state (already voted)
    state.set_user_vote(vote.username)

    # broadcast the connection to all users in the lobby
    # refactor: this message is duplicated in the ws endpoint
    users_json = json.dumps([user.model_dump() for user in state.users])
    await manager.broadcast(
        {
            "type": Events.UPDATE_USER_LIST.value,
            "message": users_json,
        }
    )

    # all users have voted, change performance to next country
    vote_count = 0
    for user in state.users:
        if user.vote:
            vote_count += 1

    if vote_count == len(state.users) and len(state.users) > 1:
        await send_next_country()
        pass

    return vote


async def send_next_country():
    # reset vote values for all users
    for user in state.users:
        user.vote = False

    # broadcast to update user list again
    users_json = json.dumps([user.model_dump() for user in state.users])
    await manager.broadcast(
        {
            "type": Events.UPDATE_USER_LIST.value,
            "message": users_json,
        }
    )

    # update current_country value
    state.set_next_country()
    # broadcast to change to next country
    await manager.broadcast(
        {
            "type": Events.NEXT_COUNTRY.value,
            "message": state.get_current_country().model_dump_json(),
        }
    )


@app.get("/ranking")
async def get_ranking() -> list[CountryRanking]:
    # TODO use the database
    # TODO only get those countries that have been played or playing
    result = []
    for country in state.countries:
        # if the country has no votes
        if country.vote_count == 0:
            break
        mean_performance = country.performance / country.vote_count
        mean_meme = country.meme / country.vote_count
        result.append(
            CountryRanking(
                country=country.name,
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
            # client messages
            data = await websocket.receive_json()
            datatype = data["type"]
            message = data["message"]
            match datatype:
                case Events.CONNECTION.value:
                    user = User(name=message["name"], vote=message["vote"])
                    # TODO do this with the database
                    state.users.append(user)

                    # broadcast the connection to all users in the lobby
                    users_json = json.dumps([user.model_dump() for user in state.users])
                    await manager.broadcast(
                        {"type": Events.UPDATE_USER_LIST.value, "message": users_json}
                    )
                case Events.NEXT_COUNTRY.value:
                    # global current_country
                    await send_next_country()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # lo que se hace cuando se desconecta el usuario


def run():
    uvicorn.run("eurotest.main:app", port=5000, reload=True, log_level="info")
