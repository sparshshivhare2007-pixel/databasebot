from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from openai import OpenAI
from config import MONGO_URI, MONGO_DB, OPENAI_API_KEY

app = FastAPI()
llm = OpenAI(api_key=OPENAI_API_KEY)
db = AsyncIOMotorClient(MONGO_URI)[MONGO_DB]
chats = db["chats"]

class ChatReq(BaseModel):
    chat_id: int
    message: str

async def _save(chat_id, role, message):
    await chats.insert_one({
        "chat_id": chat_id, "sender_id": 0, "role": role, "message": message,
        "chat_type": "api", "chat_title": "API", "sender_name": None,
        "timestamp": datetime.utcnow(),
    })

async def _history(chat_id, limit=10):
    rows = await chats.find({"chat_id": chat_id}, {"_id": 0, "role": 1, "message": 1}) \
        .sort("timestamp", -1).limit(limit).to_list(length=limit)
    rows.reverse()
    return rows

@app.post("/chat")
async def chat(req: ChatReq):
    await _save(req.chat_id, "user", req.message)
    h = await _history(req.chat_id, 10)
    ctx = "\n".join([f"{r['role']}: {r['message']}" for r in h])
    r = llm.chat.completions.create(model="gpt-4o-mini",
        messages=[{"role": "user", "content": ctx}])
    reply = r.choices[0].message.content
    await _save(req.chat_id, "bot", reply)
    return {"reply": reply}

@app.get("/history/{chat_id}")
async def history(chat_id: int, limit: int = 20):
    return {"chat_id": chat_id, "messages": await _history(chat_id, limit)}

@app.delete("/history/{chat_id}")
async def clear(chat_id: int):
    r = await chats.delete_many({"chat_id": chat_id})
    return {"deleted": r.deleted_count}
