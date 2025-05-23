from django.shortcuts import render
import asyncio
from .queue_manager import process_queue
import re
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

# دالة تحقق لاسم المستخدم
def validate_telegram_username(username):
    validator = URLValidator()
    try:
        validator(f"https://t.me/{username}")
    except ValidationError:
        raise ValidationError("Invalid Telegram username.")

def search_view(request):
    error_message = None
    results = None

    if request.method == "POST":
        telegram_query = request.POST.get("telegram_query", "").strip()
        keyword = request.POST.get("keyword", "").strip()

        # تحقق من صحة اسم المستخدم
        try:
            validate_telegram_username(telegram_query)
        except ValidationError as ve:
            error_message = str(ve)

        # تنقية البيانات
        telegram_query = re.sub(r"(https?://)?(t\.me/)?", "", telegram_query)
        telegram_query = re.sub(r"[^\w]", "", telegram_query)

        if not telegram_query:
            error_message = "Please enter a valid Telegram username."
        elif not keyword:
            error_message = "Please enter a keyword for search."

        if not error_message:
            try:
                # نادينا الكيو وحصلنا على النتائج
                results = asyncio.run(process_queue(telegram_query, keyword))

                # إذا كانت النتائج تحتوي على خطأ، نعرض رسالة الخطأ
                if isinstance(results, dict) and results.get("error"):
                    error_message = results["error"]
                    results = None

                # إذا كانت النتائج صحيحة، نقوم بتخزينها في الجلسة
                else:
                    request.session['telegram_results'] = results

            except Exception as e:
                error_type = type(e).__name__

                if error_type == "ConnectionError":
                    error_message = "Failed to connect to Telegram. Please check your internet connection or try again later."
                elif error_type == "Timeout":
                    error_message = "The request to Telegram timed out. Please try again in a few moments."
                elif error_type == "HTTPError":
                    error_message = f"An HTTP error occurred: {str(e)}. Please check the file and try again."
                else:
                    error_message = f"An unexpected error occurred: {str(e)}. Please try again later."

    # عرض الصفحة مع النتائج أو رسالة الخطأ
    return render(request, "pages/TelegramManagement.html", {
        "results": results,
        "error_message": error_message,
        "channel_name": results.get('channel_name') if results and 'channel_name' in results else None,
        "messages": results.get('messages') if results else [],
    })
