import requests
import os
import time
from datetime import datetime
from django.shortcuts import render

# جلب مفتاح API من متغيرات البيئة
VT_API_KEY = os.environ.get('VT_API_KEY')
if not VT_API_KEY:
    raise ValueError("API Key not found in environment variables!")

def Check_File(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        file_content = file.read()

        headers = {
            "x-apikey": VT_API_KEY
        }
        upload_url = "https://www.virustotal.com/api/v3/files"
        files = {"file": (file.name, file_content)}

        try:
            # إرسال الملف للحصول على ID التحليل
            response = requests.post(upload_url, headers=headers, files=files)
            if response.status_code != 200:
                # عرض رسالة خطأ مختصرة
                error_message = f"Failed to Upload File : {response.status_code} - "
                if response.status_code == 413:
                    error_message += "The File is Too Large."
                else:
                    error_message += response.text[:100]  # عرض مقتطف قصير من النص
                return render(request, 'pages/Check_File.html', {
                    "error": error_message,
                    "file": file.name
                })

            analysis_id = response.json()['data']['id']
            analysis_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"

            # ننتظر انتهاء التحليل
            max_attempts = 50
            for attempt in range(max_attempts):
                analysis_response = requests.get(analysis_url, headers=headers)
                if analysis_response.status_code == 200:
                    analysis_data = analysis_response.json()
                    status = analysis_data['data']['attributes']['status']
                    if status == "completed":
                        break
                time.sleep(5)
            else:
                return render(request, 'pages/Check_File.html', {
                    "error": f"Analysis did not complete after {max_attempts * 5} seconds. Try again later.",
                    "file": file.name
                })

            # استخراج sha256 لجلب التقرير الكامل
            sha256 = analysis_data['meta']['file_info']['sha256']
            report_url = f"https://www.virustotal.com/api/v3/files/{sha256}"
            report_response = requests.get(report_url, headers=headers)

            if report_response.status_code == 200:
                report_data = report_response.json()

                # حساب مؤشر الخطورة
                stats = report_data['data']['attributes']['last_analysis_stats']
                malicious = stats.get('malicious', 0)
                harmless = stats.get('harmless', 0)
                undetected = stats.get('undetected', 0)
                total = malicious + harmless + undetected

                if total > 0:
                    risk_percentage = (malicious / total) * 100
                else:
                    risk_percentage = 0

                # تحديد مستوى الخطورة
                if risk_percentage < 10:
                    risk_level = ("Low", "🟢 Low", "harmless")
                elif 10 <= risk_percentage <= 30:
                    risk_level = ("Medium", "🟠 Medium", "medium-risk")
                else:
                    risk_level = ("High", "🔴 High", "malicious")

                return render(request, 'pages/Check_File.html', {
                    "result": report_data,
                    "file": file.name,
                    "scan_time": datetime.now(),  # هذا هو المتغير
                    "risk_level": risk_level[1],
                    "risk_class": risk_level[2],
                    "risk_value": f"{risk_percentage:.2f}%"
                })

            else:
                return render(request, 'pages/Check_File.html', {
                    "error": f"Failed to retrieve full scan report: {report_response.text}",
                    "file": file.name
                })

        except Exception as e:
            return render(request, 'pages/Check_File.html', {
                "error": f"An error occurred during scanning: {str(e)}"
            })

    return render(request, 'pages/Check_File.html')
