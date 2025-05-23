# generate_session.py
from pyrogram import Client, errors
import os

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH") 
phone_number = int(os.getenv("PHONE_NUMBER"))  

# إنشاء الجلسة باستخدام Pyrogram
try:
    with Client("telegram_scraper", api_id=api_id, api_hash=api_hash, phone_number=phone_number) as app:
        print("✅ Session created and saved as telegram_scraper.session")
except errors.FloodWait as e:
    print(f"❌ You are being rate-limited, please try again after {e.x} seconds.")
except Exception as e:
    print(f"❌ An error occurred: {str(e)}")



# to run and generate session : python generate_session.py
