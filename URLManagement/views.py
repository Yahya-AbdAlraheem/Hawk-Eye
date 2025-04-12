from django.shortcuts import render
import requests
import base64
import os
from django.conf import settings
from datetime import datetime

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

                # جلب التاريخ وتحويله إلى الشكل: April 12, 2025, 6:27 p.m.
                scan_timestamp = vt_data['data']['attributes'].get('last_analysis_date')
                if scan_timestamp:
                    scan_date = datetime.fromtimestamp(scan_timestamp).strftime('%B %d, %Y, %I:%M %p')
                    scan_date = scan_date.replace("AM", "a.m.").replace("PM", "p.m.")
                    context['scan_date'] = scan_date

                # حساب النسبة المئوية للمخاطر
                malicious = vt_data['data']['attributes']['last_analysis_stats']['malicious']
                suspicious = vt_data['data']['attributes']['last_analysis_stats']['suspicious']
                undetected = vt_data['data']['attributes']['last_analysis_stats']['undetected']
                harmless = vt_data['data']['attributes']['last_analysis_stats']['harmless']

                total = malicious + suspicious + undetected + harmless
                risk_value = 0

                if total > 0:
                    # حساب النسبة المئوية للمخاطر
                    risk_value = (malicious + suspicious) / total * 100

                # إضافة النسبة المئوية إلى context
                context['risk_value'] = round(risk_value, 2)

                # تصنيف المخاطر
                if risk_value > 70:
                    context['risk_class'] = 'malicious'
                elif risk_value > 30:
                    context['risk_class'] = 'medium-risk'
                else:
                    context['risk_class'] = 'harmless'

            else:
                context['error'] = 'Failed to Fetch Data From VirusTotal.'

    return render(request, 'pages/Check_URL.html', context)
