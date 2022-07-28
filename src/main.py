from json import JSONDecodeError

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from .ConnectionManager import ConnectionManager
from .ActionManager import ActionManager

app = FastAPI()
connection_manager = ConnectionManager()


@app.get("/")
async def get():
    """Called when root of site accessed"""
    return FileResponse("src/index.html")


@app.get("/healthcheck")
async def healthcheck():
    """Sanity check for CD"""
    return "Service is healthy"


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Starts WebSocket when /ws/{some random UUID} accessed"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            getattr(ActionManager, data["action"])(data, connection_manager)
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except JSONDecodeError:
        connection_manager.send_to_client(
            "Wrong data sent. Please send a JSON string instead (Hint: JSON.stringify)."
        )
