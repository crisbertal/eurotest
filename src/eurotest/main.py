import uvicorn

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
)


from enum import Enum
import json

app = FastAPI()

# REQUIREMENTS
# 1. Votar la actuacion (post, con confirmacion)
# 2. Ver ranking (get, posibilidad de refescar)
# 3. Cambiar pais actual: que se cambie TODO no sabemos los paises todavia, que sea facil agregar nuevos
# 4. Login: user, pass. En principio creamos nosotros los usuarios desde admin.

class Events(Enum):
	CONNECTION = "connect"
	UPDATE_USER_LIST = "update-user-list"


@app.post("/{country}/vote/")
async def vote(country: str): ...


@app.get("/ranking")
async def get_ranking(): ...


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

# Global data
users = []


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
                    await manager.broadcast({"type": Events.UPDATE_USER_LIST.value, 
                                                 "message": users})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # lo que se hace cuando se desconecta el usuario


def run():
    uvicorn.run("eurotest.main:app", port=5000, reload=True, log_level="info")
