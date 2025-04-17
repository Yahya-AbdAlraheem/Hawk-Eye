import socket
from datetime import datetime

import whois
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from django.http import HttpResponse
from django.shortcuts import render



import re

def is_valid_domain(domain):
    pattern = r'^(?!\-)([a-zA-Z0-9\-]{1,63}\.)+[a-zA-Z]{2,}$'
    return re.match(pattern, domain) is not None


def whois_lookup(request):
    if request.method == 'GET':
        domain = request.GET.get('domain')
        
        if not domain:
            return render(request, 'pages/WHOIS.html', {'error': 'No Domain Provided'})
        
        # تحقق باستخدام regex بدل allowed_extensions
        if not is_valid_domain(domain):
            return render(request, 'pages/WHOIS.html', {'error': 'Invalid Domain Format. Please enter a valid domain like example.com'})

        try:
            whois_info = whois.whois(domain)

            if not whois_info:
                return render(request, 'pages/WHOIS.html', {'error': 'No WHOIS Data Found For The Domain.'})
            
            creation_date = whois_info.creation_date if isinstance(whois_info.creation_date, datetime) else whois_info.creation_date[0] if whois_info.creation_date else 'Blocked'
            expiration_date = whois_info.expiration_date if isinstance(whois_info.expiration_date, datetime) else whois_info.expiration_date[0] if whois_info.expiration_date else 'Blocked'
            if creation_date != 'Blocked':
                creation_date = creation_date.strftime('%d %B %Y, %I:%M %p')
            if expiration_date != 'Blocked':
                expiration_date = expiration_date.strftime('%d %B %Y, %I:%M %p')

            try:
                ip_address = socket.gethostbyname(domain)
            except:
                ip_address = 'Blocked'

            name_servers_info = []
            for ns in whois_info.name_servers if whois_info.name_servers else ['Blocked']:
                try:
                    ns_ip = socket.gethostbyname(ns)
                except:
                    ns_ip = 'Blocked'
                name_servers_info.append({'name': ns, 'ip': ns_ip})

            domain_info = {
                'domain': domain,
                'registrar': whois_info.registrar or 'Blocked',
                'creation_date': creation_date,
                'expiration_date': expiration_date,
                'name_servers': name_servers_info,
                'status': whois_info.status if whois_info.status else ['Blocked'],
                'org_name': whois_info.org or 'Blocked',
                'owner': whois_info.name or 'Blocked',
                'email': whois_info.emails[0] if whois_info.emails and isinstance(whois_info.emails, list) else whois_info.emails or 'Blocked',
                'country': whois_info.country or 'Blocked',
                'city': whois_info.city or 'Blocked',
                'ip_address': ip_address,
            }

            request.session['domain_info'] = domain_info

            return render(request, 'pages/WHOIS.html', {'domain_info': domain_info})

        except whois.parser.PywhoisError:
            return render(request, 'pages/WHOIS.html', {'error': 'WHOIS data could not be retrieved. The domain may be private or unavailable.'})
        except Exception as e:
            return render(request, 'pages/WHOIS.html', {'error': f'An error occurred: {str(e)}'})



def download_pdf(request):
    # استرجاع بيانات WHOIS من الجلسة
    domain_info = request.session.get('domain_info')

    if not domain_info:
        return HttpResponse("No data to generate PDF", status=400)
    
    # تجهيز اسم الملف بناءً على الدومين
    domain_name = domain_info['domain'].replace(" ", "_")
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="whois_data_{domain_name}.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    y_position = 750

    def write_line(label, value=None):
        nonlocal y_position
        if y_position <= 50:
            p.showPage()
            y_position = 750
        if value is not None:
            p.drawString(80, y_position, f"{label} :    {value}")
        else:
            p.drawString(80, y_position, label)
        y_position -= 20

    # المعلومات الرئيسية
    write_line(f"Domain: {domain_info['domain']}")
    write_line(f"Registrar: {domain_info['registrar']}")
    write_line(f"Creation Date: {domain_info['creation_date']}")
    write_line(f"Expiration Date: {domain_info['expiration_date']}")
    write_line(f"IP Address: {domain_info['ip_address']}")

    # باقي البيانات
    write_line(f"Owner: {domain_info['owner']}")
    write_line(f"Organization: {domain_info['org_name']}")
    write_line(f"Email: {domain_info['email']}")
    write_line(f"Country: {domain_info['country']}")
    write_line(f"City: {domain_info['city']}")

    # إضافة سطر فارغ للفصل بين المجموعات
    write_line("")

    # خوادم الأسماء
    write_line("Name Servers:")
    for ns_info in domain_info['name_servers']:
        ns_name = ns_info.get('name', 'Blocked')
        ns_ip = ns_info.get('ip', 'Blocked')
        write_line(f"{ns_name}  -  {ns_ip}")

    # إضافة سطر فارغ بعد خوادم الأسماء
    write_line("")

    # الحالة
    write_line("Status:")
    for status in domain_info['status']:
        write_line(f"{status}")


    # إنهاء الملف
    p.showPage()
    p.save()
    
    return response

