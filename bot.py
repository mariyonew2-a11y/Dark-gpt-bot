import telebot
import asyncio
import re
import os
import time
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
    if not text: return "❌ No Response."
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

# --- [ CORE ENGINE - OSINT STYLE WITH FORWARD ] ---
async def fetch_dark_intel(query, user_chat_id): # chat_id add kiya
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()
    try:
        await client.send_message(TARGET_BOT, query)
        
        final_text = ""
        final_btns = None
        
        for _ in range(25): # Image ke liye thoda extra wait
            await asyncio.sleep(2)
            messages = await client.get_messages(TARGET_BOT, limit=1)
            if not messages: continue
            
            msg = messages[0]
            
            # Agar Thinking wala message hai toh wait karo
            if msg.text == query or "thinking" in str(msg.text).lower():
                continue
            
            # --- [ IMAGE FORWARD LOGIC ] ---
            if msg.photo:
                await client.forward_messages(user_chat_id, msg)
                await client.disconnect()
                return "✅ **Image Forwarded to your chat!**", None

            # --- [ TEXT RESPONSE ] ---
            final_text = dark_cleaner(msg.text or msg.caption)
            final_btns = markup_converter(msg.reply_markup)
            
            if final_text:
                break
        
        await client.disconnect()
        return final_text, final_btns
            
    except Exception as e:
        if client.is_connected(): await client.disconnect()
        return f"❌ System Error: {str(e)}", None

# --- [ COMMANDS ] ---

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_chat_action(message.chat.id, 'typing')
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃        🔥 **DARK GPT v1.13** 🔥       ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Hii **{message.from_user.first_name}**, Main hoon **DARK GPT**💀\n"
        f"Forward Mode Active for Testing! 🚀\n\n"
        f"┃ *Owner: @beast\\_harry* ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    status_msg = bot.reply_to(message, design, parse_mode="Markdown")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _, buttons = loop.run_until_complete(fetch_dark_intel("/start", message.chat.id))
    loop.close()
    
    if buttons:
        bot.edit_message_reply_markup(message.chat.id, status_msg.message_id, reply_markup=buttons)

@bot.message_handler(func=lambda message: True)
def handle_input(message):
    bot.send_chat_action(message.chat.id, 'typing')
    status_msg = bot.reply_to(message, "🛰 **DARK GPT is Decrypting...**", parse_mode="Markdown")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Forwarding ke liye chat_id bheja
    final_output, buttons = loop.run_until_complete(fetch_dark_intel(message.text, message.chat.id))
    loop.close()
    
    try:
        bot.edit_message_text(final_output, message.chat.id, status_msg.message_id, reply_markup=buttons, parse_mode="Markdown")
    except:
        bot.edit_message_text(final_output, message.chat.id, status_msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("btn_"))
def handle_button_click(call):
    button_text = call.data.replace("btn_", "")
    bot.answer_callback_query(call.id, f"Trigging: {button_text}")
    call.message.text = button_text
    handle_input(call.message)

# --- [ RENDER SETUP ] ---
@app.route('/')
def home(): return "DARK_GPT_ONLINE"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()
    bot.infinity_polling()
