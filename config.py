import os
from dotenv import load_dotenv
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "telegram_chatbot")
BACKFILL_LIMIT = int(os.getenv("BACKFILL_LIMIT", "500"))

REPLY_CHATS = set()
for r in os.getenv("REPLY_CHATS", "me").split(","):
    r = r.strip()
    REPLY_CHATS.add("me" if r == "me" else int(r))
