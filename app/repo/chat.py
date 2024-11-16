from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.repo.message import save_message, get_user_by_chat_link
from app.db.database import database

router = APIRouter()

@router.on_event("startup")
async def startup():
    await database.connect()

@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@router.websocket("/{slug}")
async def chat_websocket(websocket: WebSocket, slug: str):
    await websocket.accept()
    print("=============")
    print("=============")
    print("=============")
    print("=============")
    user = await get_user_by_chat_link(slug)
    if not user:
        await websocket.send_text("Invalid chat link")
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_text()
            await save_message(user["id"], data)  # Save message to DB using repo layer
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        await websocket.close()
