import telebot
import asyncio
import re
import os
import time
from telethon import TelegramClient
from telethon.sessions import StringSession
from flask import Flask
from threading import Thread

# --- [ CONFIGURATION ] ---
API_ID = 34871644
API_HASH = '9ab73b2a48115feed25b5029c812ea29'
SESSION_STR = "1BVtsOH0Bu5lnyEXPVEAuGyowSijpsUampMV1gWO2zntgmTIQluvoxgI2PAQ76K4RVeFWE3OlWQole-99hzjZ4bJdH9ew1VSHgib29jKWKAiAsGlYWIDFVhhwn1zPO1Ck7qoBajH_7RfFtEisEwrLYTlCVJmUklFMR1QFBoFbwq-1KeF7kQeeSBdJPKsTeqwMBSQfQySuc7JbQ_jj7ni18UPkV1laqHAKAWd_OZFoKsvJHa7f05oeOTozBSVrCFOrzK8UQN5gV3nDECvbIWfpFzzLT20HWYYGNL3v1Y1S0b1g0tk-uryzkQEgUCc3X4ej5cvUL80qfvmNgWfdPkE4kaZnmE2PsIo="
BOT_TOKEN = "8745018482:AAFkDT3Nv5TM5El2VlSPsCnbdGRHETfqAEY"
TARGET_BOT = "@Realwormgpt_bot"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# Persistent Client (Ek baar connect karega)
client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)

# --- [ REBRANDING CLEANER ] ---
def dark_cleaner(text):
    if not text: return None
    text = re.sub(r'Worm-GPT|WormGPT|Worm GPT', 'DARK GPT', text, flags=re.IGNORECASE)
    text = re.sub(r'@Realwormgpt_bot|@realwormgpt', '@x_dark_gpt_bot', text, flags=re.IGNORECASE)
    return text.strip()

# --- [ CORE ENGINE - HISTORY POLLING ] ---
async def fetch_dark_intel(query):
    if not client.is_connected():
        await client.connect()
    
    try:
        # 1. Message bhejo
        await client.send_message(TARGET_BOT, query)
        
        # 2. History scan karo (Wait for actual result)
        last_msg_id = 0
        for _ in range(20): # Max 40 seconds wait
            await asyncio.sleep(2)
            # Sirf aakhri message uthao
            messages = await client.get_messages(TARGET_BOT, limit=1)
            
            if not messages: continue
            msg = messages[0]
            
            # Agar message ID purani hai, toh wait karo
            if msg.id == last_msg_id: continue
            
            raw_text = msg.text or msg.caption
            if not raw_text: continue

            # "Thinking" ya "Wait" message check
            skip_keywords = ["thinking", "processing", "wait", "generating", "⌛"]
            if any(x in raw_text.lower() for x in skip_keywords) and len(raw_text) < 60:
                last_msg_id = msg.id # Is message ko ignore karke agle ka wait karo
                continue
            else:
                # Actual result mil gaya!
                return dark_cleaner(raw_text)
                
        return "❌ Timeout: DARK GPT ne jawab dene mein der kar di."
            
    except Exception as e:
        return f"❌ System Error: {str(e)}"

# --- [ START COMMAND ] ---
@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃        🔥 **DARK GPT v1.3** 🔥        ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Hii **{name}**, Main hoon **DARK GPT**💀\n\n"
        f"Pucho mujhse jo baaki AI block karte hain. Ethical ho ya Unethical, main sab handle kar leta hoon.\n\n"
        f"┃ *Owner: @beast\\_harry* ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, design, parse_mode="Markdown")

# --- [ BRIDGE HANDLER ] ---
@bot.message_handler(func=lambda message: True)
def handle_input(message):
    bot.send_chat_action(message.chat.id, 'typing')
    status_msg = bot.reply_to(message, "🛰 **DARK GPT is Decrypting...**", parse_mode="Markdown")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        final_output = loop.run_until_complete(fetch_dark_intel(message.text))
        loop.close()
        
        if final_output:
            bot.edit_message_text(final_output, message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("❌ No response found.", message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, status_msg.message_id)

# --- [ RENDER SETUP ] ---
@app.route('/')
def home(): return "SYSTEM_ACTIVE"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()
    bot.infinity_polling()
