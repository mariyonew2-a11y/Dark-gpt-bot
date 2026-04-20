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
SESSION_STR = "1BVtsOH0Bu5lnyEXPVEAuGyowSijpsUampMV1gWO2zntgmTIQluvoxgI2PAQ76K4RVeFWE3OlWQole-99hzjZ4bJdH9ew1VSHgib29jKWKAiAsGlYWIDFVhhwn1zPO1Ck7qoBajH_7RfFtEisEwrLYTlCVJmUklFMR1QFBoFbwq-1KeF7kQeeSBdJPKsTeqwMBSQfQ_jj7ni18UPkV1laqHAKAWd_OZFoKsvJHa7f05oeOTozBSVrCFOrzK8UQN5gV3nDECvbIWfpFzzLT20HWYYGNL3v1Y1S0b1g0tk-uryzkQEgUCc3X4ej5cvUL80qfvmNgWfdPkE4kaZnmE2PsIo="
BOT_TOKEN = "8745018482:AAFkDT3Nv5TM5El2VlSPsCnbdGRHETfqAEY"
TARGET_BOT = "@Realwormgpt_bot"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# --- [ BEAST REBRANDING CLEANER ] ---
def dark_cleaner(text):
    if not text: return "❌ No Response from Abyss."
    # Rebranding: Worm-GPT ko DARK GPT se replace karo
    text = re.sub(r'Worm-GPT|WormGPT|Worm GPT', 'DARK GPT', text, flags=re.IGNORECASE)
    # Target bot ke usernames ko apne se badlo
    text = re.sub(r'@Realwormgpt_bot|@realwormgpt', '@x_dark_gpt_bot', text, flags=re.IGNORECASE)
    return text.strip()

# --- [ CORE ENGINE - TELETHON CONVERSATION ] ---
async def fetch_dark_intel(query):
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()
    try:
        async with client.conversation(TARGET_BOT, timeout=60) as conv:
            await conv.send_message(query)
            
            # Loop to catch the actual result (Skipping 'Processing' messages)
            for _ in range(5): # Max 5 messages check
                response = await conv.get_response()
                raw_text = response.text if response.text else response.caption
                
                if not raw_text: continue
                
                # Agar message mein "processing", "thinking" ya "wait" hai toh skip karo
                skip_keywords = ["processing", "thinking", "wait", "generating", "⌛"]
                if any(x in raw_text.lower() for x in skip_keywords) and len(raw_text) < 100:
                    continue
                else:
                    # Asli result mil gaya
                    clean_res = dark_cleaner(raw_text)
                    await client.disconnect()
                    return clean_res
            
            await client.disconnect()
            return "❌ Timeout: Bot ne koi solid jawab nahi diya."
            
    except Exception as e:
        if client.is_connected(): await client.disconnect()
        return f"❌ System Error: {str(e)}"

# --- [ START COMMAND ] ---
@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    # Fixed escape sequence warning by using \\_
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃        🔥 **DARK GPT v1.2** 🔥        ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Hii **{name}**, Main hoon **DARK GPT**—Tumhara ultimate AI companion jo kisi bhi limit ko nahi maanta! 💀\n\n"
        f"Pucho mujhse jo baaki AI block karte hain. Ethical ho ya Unethical, main sab handle kar leta hoon. 😉\n\n"
        f"┃ *Owner: @beast\\_harry* ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, design, parse_mode="Markdown")

# --- [ BRIDGE HANDLER ] ---
@bot.message_handler(func=lambda message: True)
def handle_input(message):
    # Typing status
    bot.send_chat_action(message.chat.id, 'typing')
    status_msg = bot.reply_to(message, "🛰 **DARK GPT is Decrypting...**", parse_mode="Markdown")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        final_output = loop.run_until_complete(fetch_dark_intel(message.text))
        loop.close()
        
        # Final output send
        bot.edit_message_text(final_output, message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, status_msg.message_id)

# --- [ RENDER SETUP ] ---
@app.route('/')
def home(): return "SYSTEM_ACTIVE"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()
    bot.infinity_polling()
