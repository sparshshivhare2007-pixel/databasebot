from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import User, Chat, Channel
from openai import OpenAI
from config import API_ID, API_HASH, STRING_SESSION, OPENAI_API_KEY, REPLY_CHATS
from db import save_message, save_chat_meta, get_context_string

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
llm = OpenAI(api_key=OPENAI_API_KEY)

def chat_type_of(e):
    if isinstance(e, User): return "user"
    if isinstance(e, Chat): return "group"
    if isinstance(e, Channel): return "channel"
    return "unknown"

async def info(event):
    try:
        c, s = await event.get_chat(), await event.get_sender()
        return (chat_type_of(c),
                getattr(c, "title", None) or getattr(c, "first_name", "Unknown"),
                getattr(s, "first_name", None) or getattr(s, "title", "Unknown"))
    except Exception:
        return None, None, None

def build_reply(chat_id, msg):
    ctx = get_context_string(chat_id, 10)
    prompt = f"Tum helpful assistant ho. Context se reply do.\n\nPichli baat:\n{ctx}\n\nUser: {msg}\nBot:"
    r = llm.chat.completions.create(model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}])
    return r.choices[0].message.content

@client.on(events.NewMessage())
async def handler(event):
    msg = event.raw_text
    if not msg: return
    c_type, c_title, s_name = await info(event)
    if c_title: save_chat_meta(event.chat_id, c_type, c_title)

    role = "self" if event.out else "user"
    sender_id = "me" if event.out else event.sender_id
    save_message(event.chat_id, sender_id, role, msg, c_type, c_title, s_name)

    if not event.out and (event.chat_id in REPLY_CHATS or "me" in REPLY_CHATS):
        try:
            reply = build_reply(event.chat_id, msg)
            save_message(event.chat_id, 0, "bot", reply, c_type, c_title, "Bot")
            await event.reply(reply)
        except Exception as e:
            print(f"Reply error: {e}")

if __name__ == "__main__":
    client.start()
    print(f"Bot chalu. Reply chats: {REPLY_CHATS}")
    client.run_until_disconnected()
