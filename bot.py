import telebot
import asyncio
import re
import os
import time
from telethon import TelegramClient
from telethon.sessions import StringSession
from flask import Flask
from threading import Thread

# --- [ CONFIGURATION - OSINT STYLE ] ---
API_ID = 34871644
API_HASH = '9ab73b2a48115feed25b5029c812ea29'
# Render ke environment variables se uthayega, ya niche paste kar dena
SESSION_STR = "1BVtsOH0Bu5lnyEXPVEAuGyowSijpsUampMV1gWO2zntgmTIQluvoxgI2PAQ76K4RVeFWE3OlWQole-99hzjZ4bJdH9ew1VSHgib29jKWKAiAsGlYWIDFVhhwn1zPO1Ck7qoBajH_7RfFtEisEwrLYTlCVJmUklFMR1QFBoFbwq-1KeF7kQeeSBdJPKsTeqwMBSQfQySuc7JbQ_jj7ni18UPkV1laqHAKAWd_OZFoKsvJHa7f05oeOTozBSVrCFOrzK8UQN5gV3nDECvbIWfpFzzLT20HWYYGNL3v1Y1S0b1g0tk-uryzkQEgUCc3X4ej5cvUL80qfvmNgWfdPkE4kaZnmE2PsIo="
BOT_TOKEN = "8745018482:AAFkDT3Nv5TM5El2VlSPsCnbdGRHETfqAEY"
TARGET_BOT = "@Realwormgpt_bot"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# --- [ REBRANDING CLEANER ] ---
def dark_cleaner(text):
    if not text: return "❌ No Response"
    # Worm-GPT ko DARK GPT se replace karo
    text = re.sub(r'Worm-GPT|WormGPT', 'DARK GPT', text, flags=re.IGNORECASE)
    # Developer links ko apne se badlo (Optionally)
    text = re.sub(r'@[a-zA-Z0-9_]+bot', '@x_dark_gpt_bot', text) 
    return text.strip()

# --- [ THE CORE ENGINE - TELETHON CONVERSATION ] ---
async def fetch_dark_intel(query):
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()
    try:
        async with client.conversation(TARGET_BOT, timeout=60) as conv:
            await conv.send_message(query)
            # Response ka wait karo
            response = await conv.get_response()
            raw_text = response.text if response.text else response.caption
            
            # Agar processing wala message hai toh ek aur baar wait karo
            if "processing" in str(raw_text).lower():
                response = await conv.get_response()
                raw_text = response.text
                
            await client.disconnect()
            return dark_cleaner(raw_text)
    except Exception as e:
        if client.is_connected(): await client.disconnect()
        return f"❌ System Error: {str(e)}"

# --- [ START COMMAND ] ---
@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃        🔥 **DARK GPT v1.0** 🔥        ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Hii **{name}**, Main hoon **DARK GPT**—Tumhara ultimate AI companion jo kisi bhi limit ko nahi maanta! 💀\n\n"
        f"Pucho mujhse jo baaki AI block karte hain. Ethical ho ya Unethical, main sab handle kar leta hoon. 😉\n\n"
        f"┃ *Owner: @beast\_harry* ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, design, parse_mode="Markdown")

# --- [ BRIDGE HANDLER ] ---
@bot.message_handler(func=lambda message: True)
def handle_input(message):
    status_msg = bot.reply_to(message, "🛰 **DARK GPT is Decrypting...**", parse_mode="Markdown")
    
    # OSINT style loop handling
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        final_output = loop.run_until_complete(fetch_dark_intel(message.text))
        loop.close()
        
        bot.edit_message_text(final_output, message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, status_msg.message_id)

# --- [ RENDER SETUP ] ---
@app.route('/')
def home(): return "DARK_GPT_ACTIVE"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()
    bot.infinity_polling()
