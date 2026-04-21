import telebot
import asyncio
import re
import os
import time
from telethon import TelegramClient, events
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

# --- [ REBRANDING & BUTTON CONVERTER ] ---
def dark_cleaner(text):
    if not text: return "❌ No Response."
    text = re.sub(r'Worm-GPT|WormGPT|Worm GPT', 'DARK GPT', text, flags=re.IGNORECASE)
    text = re.sub(r'@Realwormgpt_bot|@realwormgpt', '@x_dark_gpt_bot', text, flags=re.IGNORECASE)
    return text.strip()

def markup_converter(reply_markup):
    """Mirror all buttons from Target Bot to Telebot"""
    if not reply_markup: return None
    markup = types.InlineKeyboardMarkup()
    
    # Telethon buttons se Telebot buttons banane ka logic
    if hasattr(reply_markup, 'rows'):
        for row in reply_markup.rows:
            btns = []
            for btn in row.buttons:
                # Agar button mein text hai toh handle karo
                if hasattr(btn, 'text'):
                    # Yahan hum har button ka text hi callback_data bana rahe hain
                    # Taaki click hote hi wahi text Userbot bhej de
                    btns.append(types.InlineKeyboardButton(text=btn.text, callback_data=f"btn_{btn.text}"))
            markup.add(*btns)
    return markup

# --- [ CORE ENGINE - FETCH TEXT & BUTTONS ] ---
async def fetch_dark_intel(query):
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()
    try:
        async with client.conversation(TARGET_BOT, timeout=60) as conv:
            await conv.send_message(query)
            await conv.get_response() # Skip Thinking
            response = await conv.get_response()
            
            raw_text = response.text if response.text else response.caption
            clean_res = dark_cleaner(raw_text)
            
            # Buttons uthao
            target_markup = markup_converter(response.reply_markup)
            
            await client.disconnect()
            return clean_res, target_markup
            
    except Exception as e:
        if client.is_connected(): await client.disconnect()
        return f"❌ System Error: {str(e)}", None

# --- [ COMMANDS & HANDLERS ] ---

@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃        🔥 **DARK GPT v1.5** 🔥        ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Hii **{name}**, Main hoon **DARK GPT**💀\n\n"
        f"Saare features niche buttons mein display ho rahe hain. Try karo! 😉\n\n"
        f"┃ *Owner: @beast\\_harry* ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    # Start par bhi Target Bot ke buttons mangwa lete hain
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _, buttons = loop.run_until_complete(fetch_dark_intel("/start"))
    loop.close()
    
    bot.reply_to(message, design, parse_mode="Markdown", reply_markup=buttons)

@bot.message_handler(func=lambda message: True)
def handle_input(message):
    bot.send_chat_action(message.chat.id, 'typing')
    status_msg = bot.reply_to(message, "🛰 **DARK GPT is Decrypting...**", parse_mode="Markdown")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    final_output, buttons = loop.run_until_complete(fetch_dark_intel(message.text))
    loop.close()
    
    bot.edit_message_text(final_output, message.chat.id, status_msg.message_id, reply_markup=buttons)

# --- [ CALLBACK HANDLER FOR BUTTON CLICKS ] ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("btn_"))
def handle_button_click(call):
    button_text = call.data.replace("btn_", "")
    # Jab koi button click karega, hum use text message ki tarah treat karenge
    bot.answer_callback_query(call.id, f"Trigging: {button_text}")
    
    # Fake a message to the handler
    call.message.text = button_text
    handle_input(call.message)

# --- [ RENDER SETUP ] ---
@app.route('/')
def home(): return "DARK_GPT_BUTTONS_ACTIVE"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()
    bot.infinity_polling()
