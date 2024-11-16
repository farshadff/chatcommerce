from fastapi import FastAPI
from app.routes import chat
from app.db.database import metadata, engine

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

metadata.create_all(engine)

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
# Include chat routes
app.include_router(chat.router)