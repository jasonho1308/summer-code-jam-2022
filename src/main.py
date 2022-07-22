from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <script>
            var client_id = crypto.randomUUID()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://`+ window.location.host + `/ws/${client_id}`);
            ws.addEventListener('message', function (event) {
                console.log('From server:', event.data);
            });
        </script>
    </body>
</html>
"""


class ConnectionManager:
    """
    Managing connection between client and server.

    Attributes
    ----------
    active_connections: List[WebSocket]
        Current alive connections that is connected to WebSocket

    Methods
    -------
    __init__()
        Initalize the manager
        Set `active_connections`
    connect(websocket: WebSocket)
        Called when client connects to WebSocket
        Assign connection to `active_connections`
    disconnect(websocket: WebSocket)
        Called when client disconnects
        Remove connection from `active_connections`
    send_to_client(message: str, websocket: WebSocket)
        Sends message to the specified client
    broadcast(message: str)
        Sends message to all active connection
    """
    def __init__(self):
        """__init__()
        Initalize the manager
        Set `active_connections`
        """
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """connect(websocket: WebSocket)
        Called when client connects to WebSocket
        Assign connection to `active_connections`
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """disconnect(websocket: WebSocket)
        Called when client disconnects
        Remove connection from `active_connections`
        """
        self.active_connections.remove(websocket)

    async def send_to_client(self, message: str, websocket: WebSocket):
        """send_to_client(message: str, websocket: WebSocket)
        Sends message to the specified client
        """
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """broadcast(message: str)
        Sends message to all active connection
        """
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get():
    """get()
    Called when root of site accessed
    """
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """websocket_endpoint(websocket: WebSocket, client_id: str)
    Starts WebSocket when /ws/{some random UUID} accessed
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_to_client(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
