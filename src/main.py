from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from ConnectionManager import ConnectionManager

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Burly Barghests</title>
    </head>
    <body>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <script>
            function uuidv4() {
              return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
                (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
              );
            };
            var client_id = uuidv4()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://`+ window.location.host + `/ws/${client_id}`);
            ws.addEventListener('message', function (event) {
                console.log('From server:', event.data);
            });
        </script>
    </body>
</html>
"""


manager = ConnectionManager()


@app.get("/")
async def get():
    """Called when root of site accessed"""
    return HTMLResponse(html)


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
