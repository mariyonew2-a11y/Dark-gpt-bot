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

# --- [ REBRANDING CLEANER ] ---
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

# --- [ CORE ENGINE - ADVANCED POLLING ] ---
async def fetch_dark_intel(query):
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()
    try:
        # 1. Message bhejo aur apni ID save karo
        sent_msg = await client.send_message(TARGET_BOT, query)
        sent_id = sent_msg.id
        
        final_caption = None
        final_btns = None
        photo_buffer = None
        
        # 2. Polling for a NEW response
        for _ in range(25): # Increased wait time to 50s for images
            await asyncio.sleep(2)
            # Latest 3 messages check karo taaki gap cover ho jaye
            messages = await client.get_messages(TARGET_BOT, limit=3)
            
            for msg in messages:
                # Sirf wo message jo hamari query ke BAAD aaya ho aur Bot ne bheja ho
                if msg.id > sent_id and msg.from_id:
                    
                    raw_text = msg.text or msg.caption or ""
                    
                    # Agar "Thinking" wala message hai, toh ignore and continue polling
                    if "thinking" in raw_text.lower() or "⌛" in raw_text:
                        continue
                    
                    # Agar Media (Photo) hai
                    if msg.photo:
                        final_caption = dark_cleaner(msg.caption)
                        final_btns = markup_converter(msg.reply_markup)
                        
                        photo_buffer = io.BytesIO()
                        await client.download_media(msg.photo, file=photo_buffer)
                        photo_buffer.name = "dark_gpt.png"
                        photo_buffer.seek(0)
                        
                        await client.disconnect()
                        return final_caption, final_btns, photo_buffer

                    # Agar sirf Text hai
                    if raw_text:
                        final_caption = dark_cleaner(raw_text)
                        final_btns = markup_converter(msg.reply_markup)
                        await client.disconnect()
                        return final_caption, final_btns, None
        
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
        f"┃        🔥 **DARK GPT v1.8** 🔥        ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Hii **{message.from_user.first_name}**, Main hoon **DARK GPT**💀\n\n"
        f"Unrestricted Intelligence & Art! 😉\n\n"
        f"┃ *Owner: @beast\\_harry* ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    # Start menu buttons fetch
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _, buttons, _ = loop.run_until_complete(fetch_dark_intel("/start"))
    loop.close()
    bot.reply_to(message, design, parse_mode="Markdown", reply_markup=buttons)

@bot.message_handler(func=lambda message: True)
def handle_input(message):
    bot.send_chat_action(message.chat.id, 'upload_photo')
    status_msg = bot.reply_to(message, "🛰 **DARK GPT is Processing...**", parse_mode="Markdown")
    
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
        bot.edit_message_text("❌ System Timeout or No Response.", message.chat.id, status_msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("btn_"))
def handle_button_click(call):
    button_text = call.data.replace("btn_", "")
    bot.answer_callback_query(call.id, f"Trigging: {button_text}")
    call.message.text = button_text
    handle_input(call.message)

# --- [ RENDER SETUP ] ---
@app.route('/')
def home(): return "DARK_GPT_V1.8_ACTIVE"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()
    bot.infinity_polling()
