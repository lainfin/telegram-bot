import requests
import time
import sqlite3
from datetime import datetime

TOKEN = "8672040417:AAEfAWNl0ip_YZtdqFlCI-Cro2rOSzYtEro"
YOUR_ID = 6320554901

conn = sqlite3.connect('messages.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS messages
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              chat_id INTEGER,
              message_id INTEGER,
              user_id INTEGER,
              username TEXT,
              first_name TEXT,
              text TEXT,
              date TEXT)''')
conn.commit()

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data)
    except:
        pass

def get_updates(offset=0):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"offset": offset, "timeout": 30}
    try:
        response = requests.get(url, params=params)
        return response.json()
    except:
        return {"ok": False, "result": []}

def save_message(chat_id, message_id, user_id, username, first_name, text):
    c.execute("INSERT INTO messages (chat_id, message_id, user_id, username, first_name, text, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (chat_id, message_id, user_id, username, first_name, text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

def get_message(chat_id, message_id):
    c.execute("SELECT text, first_name, username FROM messages WHERE chat_id = ? AND message_id = ?", 
              (chat_id, message_id))
    return c.fetchone()

print("🤖 BUSINESS БОТ ЗАПУЩЕН")
last_update_id = 0

while True:
    try:
        updates = get_updates(last_update_id + 1)
        
        if updates.get("ok"):
            for update in updates.get("result", []):
                last_update_id = update["update_id"]
                message = update.get("message")
                if not message:
                    continue
                
                chat_id = message["chat"]["id"]
                user_id = message["from"]["id"]
                text = message.get("text", "")
                first_name = message["from"].get("first_name", "Unknown")
                username = message["from"].get("username", "")
                message_id = message["message_id"]
                
                if text.startswith("/deleted:"):
                    try:
                        parts = text.replace("/deleted:", "").split("|")
                        deleted_chat_id = int(parts[0])
                        deleted_message_id = int(parts[1])
                        saved = get_message(deleted_chat_id, deleted_message_id)
                        
                        if saved:
                            msg_text, name, username = saved
                            alert = f"🔔 <b>УДАЛЕНО СООБЩЕНИЕ</b>\n\n👤 {name}\n📝 {msg_text}"
                            send_message(YOUR_ID, alert)
                    except:
                        pass
                else:
                    save_message(chat_id, message_id, user_id, username, first_name, text)
        
        time.sleep(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)
