from django.core.cache import cache
from django.views import View
from django.http import JsonResponse
from .dark_web_scraper import search_darkweb
from .models import ExtractedData
from .AES import decrypt

class GetResultsView(View):
    def get(self, request):
        query = request.GET.get("query", "").strip()
        
        if not query:
            return JsonResponse({'error': 'Please Enter Your Search Term !!'}, status=400)

        # البحث في الكاش أولًا
        cached_data = cache.get(query)
        if cached_data:
            return JsonResponse({'source': 'cache', 'results': cached_data})

        # حذف البيانات القديمة مباشرة
        ExtractedData.objects.filter(query=query).delete()

        # البحث في الدارك ويب وحفظ البيانات في الموديل
        search_darkweb(query)

        # جلب البيانات من الموديل بعد حفظها
        extracted_data = ExtractedData.objects.filter(query=query)

        # فك تشفير البيانات المجلوبة من الموديل
        results = [
            {
                'title_1': decrypt(data.title_1),
                'title_2': decrypt(data.title_2),
                'title_3': decrypt(data.title_3),
                'description': decrypt(data.description),
                'image': data.image.url if data.image else None,
                'video': data.video.url if data.video else None,
                'url': data.url
            }
            for data in extracted_data
        ]

        # حفظ البيانات في الكاش بعد فك تشفيرها
        cache.set(query, results, timeout=600)

        return JsonResponse({'source': 'db', 'results': results})
