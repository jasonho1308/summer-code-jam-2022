from json import JSONDecodeError

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from .ConnectionManager import ConnectionManager
from .ActionManager import ActionManager

app = FastAPI()
connection_manager = ConnectionManager()
action_manager = ActionManager()


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
            getattr(action_manager, data["action"])(data, client_id)
    except WebSocketDisconnect:
        if client_id in action_manager.certificated:
            action_manager.certificated.remove(client_id)
        connection_manager.disconnect(websocket)
    except JSONDecodeError:
        connection_manager.send_to_client(
            "Wrong data sent. Please send a JSON string instead (Hint: JSON.stringify)."
        )
