from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from src.ConnectionManager import ConnectionManager

app = FastAPI()
manager = ConnectionManager()


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
            data = await websocket.receive_text()
            await manager.send_to_client(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
