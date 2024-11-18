import json
from difflib import SequenceMatcher  # To calculate similarity
import os

from groq import Groq
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

from sqlalchemy.exc import SQLAlchemyError

from app.db import DB, shop, product
from app.db.chat_links import ChatLink
from app.db.message import Message
from app.db.product import Products

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

    try:
        await websocket.send_text("Welcome! Please type your message.")

        # Track the state to know if we are waiting for a product name
        waiting_for_product_name = False
        selected_shop_id = None

        while True:
            data = await websocket.receive_text()
            print(f"Received from {mobile}: {data}")

            if not waiting_for_product_name:
                # Process the initial message
                shop_item = DB.query(ChatLink, filter_by={"slug": slug})
                if shop_item:
                    first_result = shop_item[0]
                    selected_shop_id = first_result.shop_id
                    selected_shop_slug = first_result.slug
                    await websocket.send_text("لطفا اسم محصولی که میخوای رو وارد کن")
                    waiting_for_product_name = True
                else:
                    await websocket.send_text(f"No shop found for slug: {slug}")
            else:
                # Perform similarity check with product names
                if selected_shop_id:
                    products = DB.query(Products, filter_by={"shop_id": selected_shop_id})
                    most_similar_product = None
                    highest_similarity = 0

                    for product in products:
                        similarity = SequenceMatcher(None, data.lower(), product.name.lower()).ratio()
                        if similarity > highest_similarity:
                            highest_similarity = similarity
                            most_similar_product = product

                    if most_similar_product and highest_similarity >= 0.8:
                        print("")
                        client = Groq(
                            api_key='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',
                        )
                        prompt = f"please provide me a brief information about this product . think that i want to sell it write it in persian and max 100 words write just the response and no english text in it . the text should be related to the product desctiption i give you here :{most_similar_product.description}"
                        print(prompt)
                        chat_completion = client.chat.completions.create(

                            messages=[
                                {
                                    "role": "user",
                                    "content":prompt,
                                }
                            ],
                            model="llama3-8b-8192",
                        )

                        print(chat_completion.choices[0].message.content)
                        product_link = "http://podro.shop/" + selected_shop_slug + "/" + most_similar_product.slug
                        await websocket.send_text(product_link +  "  این لینک محصولی هسست که درخواست دادی لطفا روش کلیک کن و خریدت رو نهایی کن  " +chat_completion.choices[0].message.content)
                        print(f"Product found: {most_similar_product.name}")
                    else:
                        await websocket.send_text("No similar product found with sufficient similarity.")

                waiting_for_product_name = False  # Reset state
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
