import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

from sqlalchemy.exc import SQLAlchemyError

from app.db import DB, shop, product
from app.db.chat_links import ChatLink
from app.db.message import Message

router = APIRouter()

chat_connections: Dict[str, List[WebSocket]] = {}
panel_connections: Dict[str, List[WebSocket]] = {}


async def broadcast_message(slug: str, message: str, from_panel: bool = False):
    if slug in chat_connections:
        for connection in chat_connections[slug]:
            await connection.send_text(f"{'Panel' if from_panel else 'User'} in {slug}: {message}")

    if slug in panel_connections:
        for connection in panel_connections[slug]:
            await connection.send_text(f"{'Panel' if from_panel else 'User'} in {slug}: {message}")


@router.websocket("/{slug}")
async def chat_websocket(websocket: WebSocket, slug: str):
    await websocket.accept()
    if slug not in chat_connections:
        chat_connections[slug] = []
    chat_connections[slug].append(websocket)
    query_params = websocket.scope.get("query_string", b"").decode()
    query_params = dict(q.split("=") for q in query_params.split("&") if "=" in q)
    mobile = query_params.get("mobile")
    print(f"Mobile from query params: {mobile}")
    print(f"Slug from URL: {slug}")
    print("Mobile from query params:", mobile)

    try:
        while True:
            data = await websocket.receive_text()
            print(mobile)
            chat_data = {
                "slug": slug,
                "message": data,
                "sender": mobile,
            }
            try:
                new_chat = Message(**chat_data)
                _id = DB.create(new_chat)
            except SQLAlchemyError as e:
                print(f"Database error occurred: {e}")
            shop_item = DB.query(ChatLink, filter_by={"slug": slug})
            # Check if results are not empty
            if shop_item:

                first_result = shop_item[0]  # Get the first item in the list
                products = DB.query(product, filter_by={"shop_id": first_result.shop_id})
                for item in products:
                    print(item.ID)
            else:
                print("No records found with slug:", slug)
            await broadcast_message(slug, data)
    except WebSocketDisconnect:
        chat_connections[slug].remove(websocket)
        if not chat_connections[slug]:
            del chat_connections[slug]


@router.websocket("/panel/{slug}")
async def panel_websocket(websocket: WebSocket, slug: str):
    await websocket.accept()
    if slug not in panel_connections:
        panel_connections[slug] = []
    panel_connections[slug].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await broadcast_message(slug, data, from_panel=True)
    except WebSocketDisconnect:
        panel_connections[slug].remove(websocket)
        if not panel_connections[slug]:
            del panel_connections[slug]
