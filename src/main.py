from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Burly Barghests</title>
    </head>
    <body>
    </body>
</html>
"""


@app.get("/")
async def get():
    """get()

    Get request event on root of site.
    """
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """websockets_endpoint(websockets: WebSocket)

    start WebSocket
    """
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
