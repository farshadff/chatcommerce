from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

router = APIRouter()

# Dictionary to store active chat connections and panel connections by slug
chat_connections: Dict[str, List[WebSocket]] = {}
panel_connections: Dict[str, List[WebSocket]] = {}


async def broadcast_message(slug: str, message: str, from_panel: bool = False):
    # Broadcast message to all chat clients in the room
    if slug in chat_connections:
        for connection in chat_connections[slug]:
            await connection.send_text(f"{'Panel' if from_panel else 'User'} in {slug}: {message}")

    # Broadcast message to all panel clients in the room
    if slug in panel_connections:
        for connection in panel_connections[slug]:
            await connection.send_text(f"{'Panel' if from_panel else 'User'} in {slug}: {message}")


@router.websocket("/{slug}")
async def chat_websocket(websocket: WebSocket, slug: str):
    await websocket.accept()
    # Add the client to the chat connections for the given slug
    if slug not in chat_connections:
        chat_connections[slug] = []
    chat_connections[slug].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast message to both chat and panel clients
            await broadcast_message(slug, data)
    except WebSocketDisconnect:
        # Remove the client from chat connections on disconnect
        chat_connections[slug].remove(websocket)
        if not chat_connections[slug]:  # Clean up if no more connections in the room
            del chat_connections[slug]


@router.websocket("/panel/{slug}")
async def panel_websocket(websocket: WebSocket, slug: str):
    await websocket.accept()
    # Add the client to the panel connections for the given slug
    if slug not in panel_connections:
        panel_connections[slug] = []
    panel_connections[slug].append(websocket)

    try:
        while True:
            # Here, the panel can also send messages to the chat room
            data = await websocket.receive_text()
            # Broadcast message to both chat and panel clients, marking it as from the panel
            await broadcast_message(slug, data, from_panel=True)
    except WebSocketDisconnect:
        # Remove the client from panel connections on disconnect
        panel_connections[slug].remove(websocket)
        if not panel_connections[slug]:  # Clean up if no more connections in the room
            del panel_connections[slug]
