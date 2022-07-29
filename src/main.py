from json import JSONDecodeError

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from .ActionManager import ActionManager
from .ConnectionManager import ConnectionManager

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
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            try:
                await getattr(action_manager, data["action"])(
                    data, client_id, connection_manager, websocket
                )
            except AttributeError:
                await connection_manager.send_to_client(
                    "Invalid action specified", websocket
                )
    except WebSocketDisconnect:
        if client_id in action_manager.certificated.keys():
            del action_manager.certificated[client_id]
        connection_manager.disconnect(websocket)
    except JSONDecodeError:
        await connection_manager.send_to_client(
            "Wrong data sent. Please send a JSON string instead (Hint: JSON.stringify).",
            websocket,
        )
