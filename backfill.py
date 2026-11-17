from telethon import TelegramClient
from telethon.sessions import StringSession
from config import API_ID, API_HASH, STRING_SESSION, BACKFILL_LIMIT
from db import save_message, save_chat_meta

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

async def backfill(limit):
    async for d in client.iter_dialogs():
        title = d.title or d.name or "Unknown"
        c_type = type(d.entity).__name__
        print(f"Backfill: {title}")
        try:
            async for m in client.iter_messages(d.entity, limit=limit):
                if not m.text: continue
                s_name = None
                if m.sender:
                    s_name = getattr(m.sender, "first_name", None) or getattr(m.sender, "title", None)
                save_message(d.id, m.sender_id or "me", "self" if m.out else "user",
                             m.text, c_type, title, s_name)
            save_chat_meta(d.id, c_type, title)
        except Exception as e:
            print(f"Skip {title}: {e}")

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(backfill(BACKFILL_LIMIT))
    print("Backfill done!")
