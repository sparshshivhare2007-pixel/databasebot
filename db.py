from datetime import datetime
from pymongo import MongoClient, ASCENDING
from config import MONGO_URI, MONGO_DB

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
chats = db["chats"]
chat_meta = db["chat_meta"]

chats.create_index([("chat_id", ASCENDING), ("timestamp", ASCENDING)])
chat_meta.create_index([("chat_id", ASCENDING)], unique=True)

def save_message(chat_id, sender_id, role, message, chat_type=None, chat_title=None, sender_name=None):
    chats.insert_one({
        "chat_id": chat_id, "sender_id": sender_id, "role": role,
        "message": message, "chat_type": chat_type,
        "chat_title": chat_title, "sender_name": sender_name,
        "timestamp": datetime.utcnow(),
    })

def save_chat_meta(chat_id, chat_type, title):
    chat_meta.update_one({"chat_id": chat_id},
        {"$set": {"chat_type": chat_type, "title": title, "updated_at": datetime.utcnow()}},
        upsert=True)

def get_history(chat_id, limit=10):
    rows = list(chats.find({"chat_id": chat_id}, {"_id": 0, "role": 1, "message": 1})
                .sort("timestamp", -1).limit(limit))
    rows.reverse()
    return [(r["role"], r["message"]) for r in rows]

def get_context_string(chat_id, limit=10):
    return "\n".join([f"{r}: {m}" for r, m in get_history(chat_id, limit)])
