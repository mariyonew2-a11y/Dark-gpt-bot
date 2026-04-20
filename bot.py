import asyncio
import re
import os
from flask import Flask
from threading import Thread
from pyrogram import Client
from telebot.async_telebot import AsyncTeleBot

# --- [ CONFIGURATION ] ---
API_ID = 34871644
API_HASH = "9ab73b2a48115feed25b5029c812ea29"
SESSION_STR = "1BVtsOH0Bu5lnyEXPVEAuGyowSijpsUampMV1gWO2zntgmTIQluvoxgI2PAQ76K4RVeFWE3OlWQole-99hzjZ4bJdH9ew1VSHgib29jKWKAiAsGlYWIDFVhhwn1zPO1Ck7qoBajH_7RfFtEisEwrLYTlCVJmUklFMR1QFBoFbwq-1KeF7kQeeSBdJPKsTeqwMBSQfQySuc7JbQ_jj7ni18UPkV1laqHAKAWd_OZFoKsvJHa7f05oeOTozBSVrCFOrzK8UQN5gV3nDECvbIWfpFzzLT20HWYYGNL3v1Y1S0b1g0tk-uryzkQEgUCc3X4ej5cvUL80qfvmNgWfdPkE4kaZnmE2PsIo="

BOT_TOKEN = "8745018482:AAFkDT3Nv5TM5El2VlSPsCnbdGRHETfqAEY"
TARGET_BOT = "Realwormgpt_bot"

# Clients Initialize (Async)
bot = AsyncTeleBot(BOT_TOKEN)
userbot = Client("DarkGPT_Userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STR)

app = Flask('')

# --- [ STEP 1: CUSTOM START MESSAGE ] ---
@bot.message_handler(commands=['start'])
async def welcome(message):
    name = message.from_user.first_name
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃        🔥 **DARK GPT v1.1** 🔥        ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Hii **{name}**, Main hoon **DARK GPT**—Tumhara ultimate AI companion jo kisi bhi limit ko nahi maanta! 💀\n\n"
        f"Mujhe engineered kiya hai **@beast\_harry** ne, taaki main tumhe wo access de sakoon jo baaki AI block karte hain.\n\n"
        f"🚀 **Main Kya Kar Sakta Hoon?**\n"
        f"• **Unrestricted Logic:** Ethical ho ya Unethical, hum har cheez pe khul ke discussion kar sakte hain. 🧠\n"
        f"• **Deep Coding:** Complex scripts aur system architecture ka asli gyaan.\n\n"
        f"⚠️ **Note:** Main yahan tumhare sawaalon ka jawab bina kisi 'Faltu Filters' ke deta hoon. 😉\n\n"
        f"┃ *Owner: @beast\_harry* ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    await bot.reply_to(message, design, parse_mode="Markdown")

# --- [ STEP 2: THE BRIDGE LOGIC (ASYNC) ] ---
@bot.message_handler(func=lambda m: True)
async def handle_chat(message):
    user_query = message.text
    chat_id = message.chat.id
    
    # Status Message
    status_msg = await bot.reply_to(message, "💀 **DARK GPT is Thinking...**", parse_mode="Markdown")

    try:
        if not userbot.is_connected:
            await userbot.start()

        # Target Bot ko query bhejo
        await userbot.send_message(TARGET_BOT, user_query)
        
        # Wait for reply (polling history)
        found = False
        for _ in range(15): # Max 30 seconds wait
            await asyncio.sleep(2)
            async for msg in userbot.get_chat_history(TARGET_BOT, limit=1):
                if msg.from_user and msg.from_user.username == TARGET_BOT:
                    raw_text = msg.text or msg.caption
                    if raw_text and user_query not in raw_text:
                        # REBRANDING: Worm-GPT ko DARK GPT se replace karo
                        final_res = re.sub(r'Worm-GPT|WormGPT', 'DARK GPT', raw_text, flags=re.IGNORECASE)
                        
                        await bot.edit_message_text(final_res, chat_id, status_msg.message_id)
                        found = True
                        break
            if found: break
        
        if not found:
            await bot.edit_message_text("❌ **Error:** Target bot response nahi de raha.", chat_id, status_msg.message_id)

    except Exception as e:
        await bot.edit_message_text(f"❌ **System Error:** {str(e)}", chat_id, status_msg.message_id)

# --- [ WEB SERVER FOR RENDER ] ---
@app.route('/')
def home(): return "DARK_GPT_ONLINE"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- [ MAIN RUNNER ] ---
async def main():
    print("✅ DARK GPT v1.1 is starting...")
    # Start Flask in a separate thread
    Thread(target=run_flask).start()
    # Start Bot Polling
    await bot.polling(non_stop=True)

if __name__ == "__main__":
    asyncio.run(main())
