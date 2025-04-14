import whois
from django.shortcuts import render
from datetime import datetime

def whois_lookup(request):
    if request.method == 'GET':
        domain = request.GET.get('domain')
        
        if not domain:
            return render(request, 'pages/WHOIS.html', {'error': 'No Domain Provided'})
        
        # التحقق من صحة اسم النطاق
        if not domain.endswith(('.com', '.net', '.org', '.gov', '.edu', '.io', '.co', '.info', '.biz', '.tv', '.me', '.us', '.ca', '.eu', '.asia', '.mobi', '.tel')):
            return render(request, 'pages/WHOIS.html', {'error': 'Invalid Domain Format. Please Use a Valid Domain Such as .com, .net, .org, etc.'})


        try:
            # إجراء البحث عن WHOIS باستخدام مكتبة python-whois
            whois_info = whois.whois(domain)

            # التحقق من البيانات المستخرجة من WHOIS
            if not whois_info:
                return render(request, 'pages/WHOIS.html', {'error': 'No WHOIS Data Found For The Domain.'})
            
            # استخراج المعلومات من WHOIS
            registrar = whois_info.registrar or 'N/A'

            # التحقق من التواريخ
            creation_date = whois_info.creation_date if isinstance(whois_info.creation_date, datetime) else whois_info.creation_date[0] if whois_info.creation_date else 'N/A'
            expiration_date = whois_info.expiration_date if isinstance(whois_info.expiration_date, datetime) else whois_info.expiration_date[0] if whois_info.expiration_date else 'N/A'
            
            # تنسيق التواريخ لتكون بالشكل المطلوب
            if creation_date != 'N/A':
                creation_date = creation_date.strftime('%b. %d, %Y, %I %p')  # تنسيق مثل Jan. 30, 2033, 05 am
            if expiration_date != 'N/A':
                expiration_date = expiration_date.strftime('%b. %d, %Y, %I %p')  # تنسيق مثل Jan. 30, 2033, 05 am

            name_servers = whois_info.name_servers if whois_info.name_servers else ['N/A']
            status = whois_info.status if whois_info.status else ['N/A']

            # تجهيز الـ context لتمريره إلى القالب
            domain_info = {
                'domain': domain,
                'registrar': registrar,
                'creation_date': creation_date,  # إضافة تاريخ الإنشاء
                'expiration_date': expiration_date,  # إضافة تاريخ الانتهاء
                'name_servers': name_servers,
                'status': status,
            }

            return render(request, 'pages/WHOIS.html', {'domain_info': domain_info})
        
        except whois.parser.PywhoisError:
            return render(request, 'pages/WHOIS.html', {'error': 'WHOIS data could not be retrieved. The domain may be private or unavailable.'})
        except Exception as e:
            return render(request, 'pages/WHOIS.html', {'error': f'An error occurred: {str(e)}'})
