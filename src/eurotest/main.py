from typing import Annotated
import uvicorn

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

# TODO
# - [x] Que varios usuarios se puedan conectar a un canal
# - [ ] Login de usuario (http)
# - [ ] Solo se puede acceder a la web si se esta logueado
# - [ ] Agregar votos a la base de datos
# - [ ] Reconocer quien es el usuario admin del resto
# - [ ] Admin tiene diferentes funcionales que el resto
# - [ ] Admin pueda cambiar la actuacion y se refleje en el lobby 
# - [ ] Los votos van a la actuacion correspondiente
# - [ ] Panel de ranking que se actualice por http


# REQUIREMENTS
# 1. Votar la actuacion (post, con confirmacion)
# 2. Ver ranking (get, posibilidad de refescar)
# 3. Cambiar pais actual: que se cambie TODO no sabemos los paises todavia, que sea facil agregar nuevos
# 4. Login: user, pass. En principio creamos nosotros los usuarios desde admin.


@app.get("/")
async def index() -> FileResponse: 
    return FileResponse("html/index.html")


# must be a form with input names equals as the parameters here
@app.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]): ...


@app.get("/next-country")
async def get_next_country(): ...


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

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    # el client_id que sirva para recuperar los datos de la BD
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            ...
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # lo que se hace cuando se desconecta el usuario


def run():
    uvicorn.run("eurotest.main:app", port=5000, reload=True, log_level="info")
