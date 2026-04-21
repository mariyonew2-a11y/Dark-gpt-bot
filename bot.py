import telebot
import asyncio
import re
import os
import time
import io
from telethon import TelegramClient
from telethon.sessions import StringSession
from telebot import types
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

# --- [ CLEANER & BUTTON MIRROR ] ---
def dark_cleaner(text):
    if not text: return None
    text = re.sub(r'Worm-GPT|WormGPT|Worm GPT', 'DARK GPT', text, flags=re.IGNORECASE)
    text = re.sub(r'@Realwormgpt_bot|@realwormgpt', '@x_dark_gpt_bot', text, flags=re.IGNORECASE)
    return text.strip()

def markup_converter(reply_markup):
    if not reply_markup: return None
    markup = types.InlineKeyboardMarkup()
    rows = getattr(reply_markup, 'rows', [])
    for row in rows:
        btns = []
        for btn in row.buttons:
            btn_text = getattr(btn, 'text', None)
            if btn_text:
                btns.append(types.InlineKeyboardButton(text=btn_text, callback_data=f"btn_{btn_text}"))
        if btns: markup.add(*btns)
    return markup if rows else None

# --- [ CORE ENGINE - FIXED ID POLLING ] ---
async def fetch_dark_intel(query):
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()
    try:
        # 1. Message bhejo aur uski ID note karo
        sent_msg = await client.send_message(TARGET_BOT, query)
        query_id = sent_msg.id # Isse choti ID wala koi message nahi uthayenge
        
        final_text = ""
        final_btns = None
        photo_buffer = None
        
        # 2. Polling for NEW response (Max 45 seconds)
        for _ in range(22): 
            await asyncio.sleep(2)
            
            # Latest 2 messages check karo taaki gap na rahe
            messages = await client.get_messages(TARGET_BOT, limit=2)
            if not messages: continue
            
            # Check messages in order
            for msg in messages:
                # Rule: Sirf wo message jo hamari query ke BAAD aaya hai
                if msg.id > query_id:
                    raw_content = msg.text or msg.caption or ""
                    
                    # Skip Thinking/Wait messages
                    if "thinking" in str(raw_content).lower() or "⌛" in str(raw_content):
                        continue
                    
                    # PHOTO DETECTED
                    if msg.photo:
                        final_text = dark_cleaner(msg.caption)
                        final_btns = markup_converter(msg.reply_markup)
                        photo_buffer = io.BytesIO()
                        await client.download_media(msg.photo, file=photo_buffer)
                        photo_buffer.name = "dark_gpt.png"
                        photo_buffer.seek(0)
                        await client.disconnect()
                        return final_text, final_btns, photo_buffer
                        
                    # TEXT DETECTED
                    if raw_content:
                        final_text = dark_cleaner(raw_content)
                        final_btns = markup_converter(msg.reply_markup)
                        await client.disconnect()
                        return final_text, final_btns, None
        
        await client.disconnect()
        return None, None, None
            
    except Exception as e:
        if client.is_connected(): await client.disconnect()
        return f"❌ System Error: {str(e)}", None, None

# --- [ HANDLERS ] ---

@bot.message_handler(commands=['start'])
def welcome(message):
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃        🔥 **DARK GPT v1.11** 🔥       ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Hii **{message.from_user.first_name}**, Main hoon **DARK GPT**💀\n\n"
        f"Intelligence, Art aur No Limits! 😉\n\n"
        f"┃ *Owner: @beast\\_harry* ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    status_msg = bot.reply_to(message, design, parse_mode="Markdown")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _, buttons, _ = loop.run_until_complete(fetch_dark_intel("/start"))
    loop.close()
    if buttons: bot.edit_message_reply_markup(message.chat.id, status_msg.message_id, reply_markup=buttons)

@bot.message_handler(func=lambda message: True)
def handle_input(message):
    bot.send_chat_action(message.chat.id, 'upload_photo')
    status_msg = bot.reply_to(message, "🛰 **DARK GPT is Decrypting...**", parse_mode="Markdown")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    final_output, buttons, photo = loop.run_until_complete(fetch_dark_intel(message.text))
    loop.close()
    
    if photo:
        bot.delete_message(message.chat.id, status_msg.message_id)
        bot.send_photo(message.chat.id, photo, caption=final_output, reply_markup=buttons, parse_mode="Markdown")
    elif final_output:
        try:
            bot.edit_message_text(final_output, message.chat.id, status_msg.message_id, reply_markup=buttons, parse_mode="Markdown")
        except:
            bot.edit_message_text(final_output, message.chat.id, status_msg.message_id)
    else:
        bot.edit_message_text("❌ System Timeout: No Image/Text received.", message.chat.id, status_msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("btn_"))
def handle_button_click(call):
    button_text = call.data.replace("btn_", "")
    bot.answer_callback_query(call.id, f"Trigging: {button_text}")
    call.message.text = button_text
    handle_input(call.message)

# --- [ RENDER SETUP ] ---
@app.route('/')
def home(): return "DARK_GPT_LIVE"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()
    bot.infinity_polling()
