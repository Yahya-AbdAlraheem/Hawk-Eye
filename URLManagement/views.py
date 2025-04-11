from django.shortcuts import render
import requests
import base64
import os
from django.conf import settings

VT_API_KEY = os.environ.get('VT_API_KEY')
if not VT_API_KEY:
    raise ValueError("API Key not found in environment variables!")

def check_url(request):
    context = {}

    if request.method == 'GET':
        url_to_check = request.GET.get('url')
        
        if url_to_check:
            headers = {
                "x-apikey": VT_API_KEY
            }

            # encode للـ URL حسب متطلبات فايروس توتل
            url_id = base64.urlsafe_b64encode(url_to_check.encode()).decode().strip("=")
            endpoint = f"https://www.virustotal.com/api/v3/urls/{url_id}"

            response = requests.get(endpoint, headers=headers)

            if response.status_code == 200:
                vt_data = response.json()
                context['result'] = vt_data
                context['url'] = url_to_check
            else:
                context['error'] = 'فشل في جلب البيانات من VirusTotal.'

    return render(request, 'pages/Check_URL.html', context)


