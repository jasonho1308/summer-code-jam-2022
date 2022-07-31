import traceback
import uuid
from json import JSONDecodeError

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from .ActionManager import ActionManager
from .ConnectionManager import ConnectionManager

app = FastAPI()
action_manager = ActionManager()
connection_manager = ConnectionManager(action_manager)


@app.get("/")
async def get():
    """Called when root of site accessed"""
    return FileResponse("src/index.html")


@app.get("/healthcheck")
async def healthcheck():
    """Sanity check for CD"""
    return "Service is healthy"


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Starts WebSocket when /ws/{some random UUID} accessed"""
    client_id = uuid.uuid4()
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
            except KeyError as e:
                await connection_manager.send_to_client(
                    f"Invalid data, did you mean '{e}'?", websocket
                )
                await connection_manager.send_to_client(
                    traceback.format_exc(), websocket
                )
            except Exception:
                await connection_manager.send_to_client(
                    traceback.format_exc(), websocket
                )
    except WebSocketDisconnect:
        if client_id in action_manager.certed.id_name.keys():
            action_manager.certed.delete(client_id)
        connection_manager.disconnect(websocket)
    except JSONDecodeError:
        await connection_manager.send_to_client(
            "Invalid JSON string",
            websocket,
        )
