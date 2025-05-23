import re
import redis
import os
import json
from pyrogram import Client

# إعداد Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# إعداد API من المتغيرات البيئية
api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")

# تأكد من وجود مجلد لتخزين الصور
os.makedirs("media/telegram_photos", exist_ok=True)

async def search_telegram(channel_username, keyword, message_limit=30):
    cache_key = f"Telegram: {channel_username}/{keyword}"
    cached_results = r.get(cache_key)
    if cached_results:
        print("🔄 Data found in cache!")
        return json.loads(cached_results.decode('utf-8'))

    async with Client("telegram_scraper", api_id=api_id, api_hash=api_hash) as app:
        try:
            await app.join_chat(channel_username)
        except Exception as e:
            print(f"Join error: {e}")

        entity = await app.get_chat(channel_username)

        channel_info = {
            "username": channel_username,
            "name": entity.title,
            "subscribers": entity.members_count if hasattr(entity, 'members_count') else "N/A",
            "posts_count": 0,
            "last_activity": None,
            "description": entity.description,
            "pinned_message": entity.pinned_message.text if entity.pinned_message else None,
            "links": [],
            "messages": []
        }

        count = 0
        async for msg in app.get_chat_history(entity.id, limit=message_limit):
            msg_text = msg.text or msg.caption
            if msg_text and keyword.lower() in msg_text.lower():
                message_data = {
                    "full_text": msg_text,
                    "links": re.findall(r"http[s]?://\S+", msg_text),
                    "attachments": [],
                    "photo_path": None,
                    "date": msg.date.strftime('%Y-%m-%d %H:%M:%S'),
                }

                print(f"🔍 Found match: {msg.id} | Media: {msg.media}")

                # تحميل الصورة إذا موجودة
                if msg.media:
                    if msg.photo:
                        try:
                            filename = f"media/telegram_photos/{channel_username}_{msg.id}.jpg"
                            await app.download_media(msg, file_name=filename)
                            message_data['photo_path'] = filename
                            message_data['attachments'].append("Photo")
                            print(f"✅ Photo downloaded: {filename}")
                        except Exception as e:
                            print(f"❌ Failed to download photo for msg {msg.id}: {e}")
                    else:
                        print(f"⚠️ Media exists but no photo in msg {msg.id}")

                    if msg.document:
                        message_data['attachments'].append("Document")
                    if msg.audio:
                        message_data['attachments'].append("Audio")

                channel_info["messages"].append(message_data)
                channel_info["links"].extend(message_data["links"])
                count += 1

        channel_info["posts_count"] = count
        if channel_info["messages"]:
            channel_info["last_activity"] = channel_info["messages"][0]["date"]

    # تخزين في الكاش لمدة ساعة
    r.setex(cache_key, 86400, json.dumps(channel_info))
    print("✅ Data cached successfully!")

    return channel_info
