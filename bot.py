import telebot
import re
import asyncio
import time
from pyrogram import Client
from threading import Thread

# --- [ CONFIGURATION ] ---
API_ID = 34871644
API_HASH = "9ab73b2a48115feed25b5029c812ea29"
SESSION_STR = "1BVtsOH0Bu5lnyEXPVEAuGyowSijpsUampMV1gWO2zntgmTIQluvoxgI2PAQ76K4RVeFWE3OlWQole-99hzjZ4bJdH9ew1VSHgib29jKWKAiAsGlYWIDFVhhwn1zPO1Ck7qoBajH_7RfFtEisEwrLYTlCVJmUklFMR1QFBoFbwq-1KeF7kQeeSBdJPKsTeqwMBSQfQySuc7JbQ_jj7ni18UPkV1laqHAKAWd_OZFoKsvJHa7f05oeOTozBSVrCFOrzK8UQN5gV3nDECvbIWfpFzzLT20HWYYGNL3v1Y1S0b1g0tk-uryzkQEgUCc3X4ej5cvUL80qfvmNgWfdPkE4kaZnmE2PsIo="

BOT_TOKEN = "8745018482:AAFkDT3Nv5TM5El2VlSPsCnbdGRHETfqAEY"
TARGET_BOT = "Realwormgpt_bot"

# Clients Initialize
bot = telebot.TeleBot(BOT_TOKEN)
userbot = Client("DarkGPT_Userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STR)

# --- [ STARTUP ] ---
def start_userbot():
    with userbot:
        print("✅ Userbot Session Connected!")
        # Keep userbot alive in the background
        while True:
            time.sleep(10)

# --- [ STEP 1: CUSTOM START MESSAGE ] ---
@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃        🔥 **DARK GPT v1.0** 🔥        ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Hii **{name}**, Main hoon **DARK GPT**—Tumhara ultimate AI companion jo kisi bhi limit ko nahi maanta! 💀\n\n"
        f"Mujhe engineered kiya hai **@beast\_harry** ne, taaki main tumhe wo access de sakoon jo baaki AI block karte hain.\n\n"
        f"🚀 **Main Kya Kar Sakta Hoon?**\n"
        f"• **Unrestricted Logic:** Ethical ho ya Unethical, hum har cheez pe khul ke discussion kar sakte hain. 🧠\n"
        f"• **Deep Coding:** Complex scripts aur system architecture ka asli gyaan.\n"
        f"• **Beast Speed:** Instant replies bina kisi 'Faltu Filters' ke.\n\n"
        f"⚠️ **Note:** Main yahan tumhare dimaag ke har sawaal ka jawab dene ke liye hoon, chahe wo kitna bhi 'Dark' kyu na ho. 😉\n\n"
        f"┃ *Owner: @beast\_harry* ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, design, parse_mode="Markdown")

# --- [ STEP 2: THE BRIDGE LOGIC ] ---
@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    user_query = message.text
    chat_id = message.chat.id
    
    # Status Message
    bot.send_chat_action(chat_id, 'typing')
    status_msg = bot.reply_to(message, "💀 **DARK GPT is Thinking...**", parse_mode="Markdown")

    async def fetch_from_target():
        async with userbot:
            # Target Bot ko query bhejo
            await userbot.send_message(TARGET_BOT, user_query)
            
            # Wait for reply (polling history)
            for _ in range(15): # Max 30 seconds wait
                await asyncio.sleep(2)
                async for msg in userbot.get_chat_history(TARGET_BOT, limit=1):
                    # Check if response is from target bot and not our own query
                    if msg.from_user and msg.from_user.username == TARGET_BOT:
                        raw_text = msg.text or msg.caption
                        if raw_text:
                            # REBRANDING: Worm-GPT ko DARK GPT se replace karo
                            final_res = re.sub(r'Worm-GPT|WormGPT', 'DARK GPT', raw_text, flags=re.IGNORECASE)
                            
                            # Final Response send karo
                            try:
                                bot.edit_message_text(final_res, chat_id, status_msg.message_id, parse_mode="Markdown")
                            except:
                                bot.edit_message_text(final_res, chat_id, status_msg.message_id)
                            return True
        return False

    # Run Async logic in a safe way
    success = asyncio.run(fetch_from_target())
    if not success:
        bot.edit_message_text("❌ **Error:** Target bot response nahi de raha ya offline hai.", chat_id, status_msg.message_id)

# --- [ SERVER START ] ---
if __name__ == "__main__":
    print("🚀 DARK GPT (Frontend) is starting...")
    # Start Userbot thread
    # Thread(target=start_userbot).start()
    bot.infinity_polling()
