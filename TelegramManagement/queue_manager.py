import asyncio
import time
from .telegram_scraper import search_telegram

# إعدادات
REQUESTS_PER_HOUR = 150
DELAY_BETWEEN_REQUESTS = 5
MESSAGE_LIMIT = 30

# دالة لإدارة الطابور
async def process_queue(channel_username, keyword):
    try:
        print("🔍 Starting data scraping...")
        results = await search_telegram(channel_username, keyword, message_limit=MESSAGE_LIMIT)

        if results and isinstance(results, dict) and results.get("messages"):
            print("✅ Data scraping completed successfully.")
            await asyncio.sleep(DELAY_BETWEEN_REQUESTS)
            return results
        else:
            print("⚠️ No results found.")
            await asyncio.sleep(DELAY_BETWEEN_REQUESTS)
            return {"error": "No results found."}

    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        print(f"❌ Error during scraping: {error_message}")
        await asyncio.sleep(DELAY_BETWEEN_REQUESTS)
        return {"error": error_message}
