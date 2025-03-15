from django.core.cache import cache
from django.http import JsonResponse
from .dark_web_scraper import search_darkweb
from .models import ExtractedData
from .AES import decrypt

def get_results(request):
    query = request.GET.get('query', '').strip()
    if not query:
        return JsonResponse({'error': 'Please Enter Your Search Term !!'}, status=400)

    # 🔥 البحث في الكاش أولًا
    cached_data = cache.get(query)
    if cached_data:
        # فك تشفير العناوين، الأوصاف، والهيدرز في الكاش
        for result in cached_data:
            result['title_1'] = decrypt(result['title_1'])
            result['title_2'] = decrypt(result['title_2'])
            result['title_3'] = decrypt(result['title_3'])
            result['description'] = decrypt(result['description'])
        return JsonResponse({'source': 'cache', 'results': cached_data})
    else:
        # 🔥 حذف البيانات القديمة
        ExtractedData.objects.filter(query=query).delete()


        # 🔥 البحث في الدارك ويب وحفظ البيانات في الموديل
        search_darkweb(query)

        # 🔥 جلب البيانات من الموديل بعد حفظها
        extracted_data = ExtractedData.objects.filter(query=query)

        # فك تشفير البيانات المجلوبة من الموديل
        results = []
        for data in extracted_data:
            results.append({
                'title_1': data.get_decrypted_title_1(),
                'title_2': data.get_decrypted_title_2(),
                'title_3': data.get_decrypted_title_3(),
                'description': data.get_decrypted_description(),
                'image': data.image.url if data.image else None,
                'video': data.video.url if data.video else None,
                'url': data.url
            })

        # حفظ البيانات في الكاش بعد فك تشفيرها
        cache.set(query, results, timeout=600)

        return JsonResponse({'source': 'db', 'results': results})
