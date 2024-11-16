from app.db.database import database
from app.db.models import users, messages

async def create_user(username: str, mobile: str, chat_link: str):
    query = users.insert().values(username=username, mobile=mobile, chat_link=chat_link)
    user_id = await database.execute(query)
    return user_id

async def save_message(user_id: int, content: str):
    query = messages.insert().values(user_id=user_id, content=content)
    message_id = await database.execute(query)
    return message_id

async def get_user_by_chat_link(chat_link: str):
    query = users.select().where(users.c.chat_link == chat_link)
    return await database.fetch_one(query)
