import telebot
import asyncio
import re
import os
import time
import io # Image buffer ke liye zaruri hai
from telethon import TelegramClient
from telethon.sessions import StringSession
from telebot import types
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

# --- [ CLEANER & BUTTON MIRROR LOGIC ] ---
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

# --- [ CORE ENGINE - OSINT STYLE WITH IMAGE SUPPORT ] ---
async def fetch_dark_intel(query):
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()
    try:
        await client.send_message(TARGET_BOT, query)
        
        final_text = ""
        final_btns = None
        photo_buffer = None # Naya variable image ke liye
        
        for _ in range(20): # Max 40 seconds polling
            await asyncio.sleep(2)
            messages = await client.get_messages(TARGET_BOT, limit=1)
            if not messages: continue
            
            msg = messages[0]
            raw_text = msg.text or msg.caption or ""
            
            # Skip Thinking or own query
            if raw_text == query or "thinking" in str(raw_text).lower() or "⌛" in str(raw_text):
                continue
            
            # --- [ IMAGE DETECTION LOGIC ] ---
            if msg.photo:
                final_text = dark_cleaner(msg.caption)
                final_btns = markup_converter(msg.reply_markup)
                
                # Download photo to memory buffer (No local file saved)
                photo_buffer = io.BytesIO()
                await client.download_media(msg.photo, file=photo_buffer)
                photo_buffer.name = "dark_gpt.png"
                photo_buffer.seek(0)
                break
                
            # --- [ TEXT DETECTION LOGIC ] ---
            if raw_text:
                final_text = dark_cleaner(raw_text)
                final_btns = markup_converter(msg.reply_markup)
                break
        
        await client.disconnect()
        return final_text, final_btns, photo_buffer # Teeno return honge
            
    except Exception as e:
        if client.is_connected(): await client.disconnect()
        return f"❌ System Error: {str(e)}", None, None

# --- [ COMMANDS ] ---

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_chat_action(message.chat.id, 'typing')
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃        🔥 **DARK GPT v1.10** 🔥        ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Hii **{message.from_user.first_name}**, Main hoon **DARK GPT**💀\n\n"
        f"Logic, Art aur Unrestricted Power! 😉\n\n"
        f"┃ *Owner: @beast\\_harry* ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    status_msg = bot.reply_to(message, design, parse_mode="Markdown")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _, buttons, _ = loop.run_until_complete(fetch_dark_intel("/start"))
    loop.close()
    
    if buttons:
        bot.edit_message_reply_markup(message.chat.id, status_msg.message_id, reply_markup=buttons)

@bot.message_handler(func=lambda message: True)
def handle_input(message):
    bot.send_chat_action(message.chat.id, 'upload_photo')
    status_msg = bot.reply_to(message, "🛰 **DARK GPT is Decrypting...**", parse_mode="Markdown")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    final_output, buttons, photo = loop.run_until_complete(fetch_dark_intel(message.text))
    loop.close()
    
    # --- [ THE DISPLAY SWITCH ] ---
    if photo:
        # Photo mili toh thinking message delete karke image bhej do
        bot.delete_message(message.chat.id, status_msg.message_id)
        bot.send_photo(message.chat.id, photo, caption=final_output, reply_markup=buttons, parse_mode="Markdown")
    elif final_output:
        try:
            bot.edit_message_text(final_output, message.chat.id, status_msg.message_id, reply_markup=buttons, parse_mode="Markdown")
        except:
            bot.edit_message_text(final_output, message.chat.id, status_msg.message_id)
    else:
        bot.edit_message_text("❌ Timeout: No response received.", message.chat.id, status_msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("btn_"))
def handle_button_click(call):
    button_text = call.data.replace("btn_", "")
    bot.answer_callback_query(call.id, f"Trigging: {button_text}")
    call.message.text = button_text
    handle_input(call.message)

# --- [ RENDER SETUP ] ---
@app.route('/')
def home(): return "DARK_GPT_ACTIVE"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()
    bot.infinity_polling()
