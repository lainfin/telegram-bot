from pyrogram import Client, filters
import sqlite3
from datetime import datetime

API_ID = 20555396
API_HASH = "597331f9906626f548214ed469d3ebfc"
PHONE = "+79014843518"
LOG_CHAT = "me"

conn = sqlite3.connect('private_chats.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS messages
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              chat_id INTEGER, message_id INTEGER, user_id INTEGER,
              username TEXT, first_name TEXT, text TEXT, date INTEGER,
              has_media INTEGER, file_id TEXT)''')
conn.commit()

app = Client("my_account", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE)

@app.on_message(filters.private & ~filters.me)
async def save_all_messages(client, message):
    text = message.text or message.caption or ""
    has_media = 1 if message.photo else 0
    file_id = message.photo.file_id if message.photo else None
    c.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (None, message.chat.id, message.id, message.from_user.id,
               message.from_user.username, message.from_user.first_name,
               text, message.date, has_media, file_id))
    conn.commit()
    print(f"[+] Сохранено: {message.chat.first_name}")

@app.on_deleted_messages()
async def handle_deleted(client, messages):
    for message in messages:
        c.execute("SELECT text, first_name FROM messages WHERE chat_id=? AND message_id=?", 
                  (message.chat.id, message.id))
        result = c.fetchone()
        if result:
            text, name = result
            await client.send_message(LOG_CHAT, f"🔔 УДАЛЕНО от {name}:\n{text}")

print("🤖 UserBot запущен!")
app.run()
