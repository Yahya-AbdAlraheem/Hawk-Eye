from django.core.cache import cache
from django.http import JsonResponse
from .dark_web_scraper import search_darkweb
from .models import ExtractedData
from .AES import encrypt, decrypt
import string

def get_results(request):
    query = request.GET.get('query', '').strip()
    if not query:
        return JsonResponse({'error': 'يرجى إدخال كلمة البحث'}, status=400)

    # 🔥 البحث في الكاش أولًا
    cached_data = cache.get(query)
    if cached_data:
        # فك تشفير العناوين، الأوصاف، والهيدرز في الكاش
        for result in cached_data:
            result['title'] = decrypt(result['title'])
            result['description'] = decrypt(result['description'])
            for key in ['h1', 'h2', 'h3']:  # فك تشفير الهيدرز
                if result.get(key):
                    result[key] = decrypt(result[key])
        return JsonResponse({'source': 'cache', 'results': cached_data})

    # 🔥 حذف البيانات القديمة
    ExtractedData.objects.all().delete()

    # 🔥 البحث في الدارك ويب
    raw_results = search_darkweb(query)

    # 🔥 تنظيف البيانات (إزالة التكرار)
    unique_results = list(set(raw_results))  # حذف المكرر

    # 🔥 تخزين البيانات بعد التشفير
    stored_results = []
    for result in unique_results:
        title = result.get('title', '')
        description = result.get('description', '')
        h1 = result.get('h1', '')
        h2 = result.get('h2', '')
        h3 = result.get('h3', '')
        image = result.get('image', '')
        video = result.get('video', '')

        # تحديد التصنيف بناء على أول حرف
        first_char = title[0].upper() if title else ''
        second_char = title[1].upper() if len(title) > 1 else ''
        third_char = title[2].upper() if len(title) > 2 else ''
        fourth_char = title[3].upper() if len(title) > 3 else ''

        if first_char.isdigit():
            category = "number"
        elif first_char in string.punctuation:
            category = "symbol"
        else:
            category = "letter"

        # تشفير العنوان، الوصف، والهيدرز
        encrypted_title = encrypt(title)
        encrypted_description = encrypt(description)
        encrypted_h1 = encrypt(h1)
        encrypted_h2 = encrypt(h2)
        encrypted_h3 = encrypt(h3)

        # حفظ البيانات في قاعدة البيانات
        ExtractedData.objects.create(
            content=encrypted_title,
            description=encrypted_description,
            category=category,
            first_character=first_char,
            second_character=second_char,
            third_character=third_char,
            fourth_character=fourth_char,
            image=image,
            video=video,
            h1=encrypted_h1,
            h2=encrypted_h2,
            h3=encrypted_h3
        )
        stored_results.append({
            'title': decrypt(encrypted_title),
            'description': decrypt(encrypted_description),
            'h1': decrypt(encrypted_h1),
            'h2': decrypt(encrypted_h2),
            'h3': decrypt(encrypted_h3),
            'image': image,
            'video': video
        })

    # 🔥 تخزين البيانات في الكاش لمدة 10 دقائق
    cache.set(query, stored_results, timeout=600)

    return JsonResponse({'source': 'darkweb', 'results': stored_results})
