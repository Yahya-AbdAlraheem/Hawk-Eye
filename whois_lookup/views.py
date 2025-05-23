import socket
from datetime import datetime
import whois
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import render
from urllib.parse import urlparse
import re


def is_valid_domain(domain_input):
    if not domain_input.startswith(("http://", "https://")):
        domain_input = f"http://{domain_input}"

    parsed = urlparse(domain_input)
    domain = parsed.netloc or parsed.path

    if domain.startswith("www."):
        domain = domain[4:]

    domain_pattern = r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
    return domain if re.match(domain_pattern, domain) else None

def format_date(dt):
    try:
        if isinstance(dt, list):
            dt = dt[0]
        return dt.strftime('%d %B %Y, %I:%M %p') if isinstance(dt, datetime) else 'Blocked'
    except:
        return 'Blocked'

def whois_lookup(request):
    if request.method == 'GET':
        domain = request.GET.get('domain')

        if not domain:
            return render(request, 'pages/WHOIS.html', {'error_message': None})

        valid_domain = is_valid_domain(domain)
        if not valid_domain:
            return render(request, 'pages/WHOIS.html', {
                'error_message': 'Invalid Domain Format. Please enter a valid domain like example.com'
            })

        try:
            whois_info = whois.whois(valid_domain)

            if not whois_info:
                return render(request, 'pages/WHOIS.html', {
                    'error_message': 'No WHOIS Data Found For The Domain.'
                })

            creation_date = format_date(whois_info.creation_date)
            expiration_date = format_date(whois_info.expiration_date)

            try:
                ip_address = socket.gethostbyname(valid_domain)
            except:
                ip_address = 'Blocked'

            name_servers_info = []
            for ns in whois_info.name_servers if whois_info.name_servers else ['Blocked']:
                try:
                    ns_ip = socket.gethostbyname(ns)
                except:
                    ns_ip = 'Blocked'
                name_servers_info.append({'name': ns, 'ip': ns_ip})

            # معالجة حالة الدومين
            status_raw = whois_info.status
            if isinstance(status_raw, list):
                status = status_raw
            elif isinstance(status_raw, str):
                status = [status_raw]
            else:
                status = ['Blocked']

            # معالجة البريد الإلكتروني
            emails_raw = whois_info.emails
            if isinstance(emails_raw, list):
                email = emails_raw[0] if emails_raw else 'Blocked'
            else:
                email = emails_raw or 'Blocked'

            # معالجة الموقع الجغرافي
            location = f"{whois_info.city or ''}, {whois_info.country or ''}".strip(', ') or 'Blocked'

            domain_info = {
                'domain': valid_domain,
                'registrar': whois_info.registrar or 'Blocked',
                'creation_date': creation_date,
                'expiration_date': expiration_date,
                'name_servers': name_servers_info,
                'status': status,
                'org_name': whois_info.org or 'Blocked',
                'owner': whois_info.name or 'Blocked',
                'email': email,
                'country': whois_info.country or 'Blocked',
                'city': whois_info.city or 'Blocked',
                'location': location,
                'ip_address': ip_address,
            }

            request.session['domain_info'] = domain_info

            return render(request, 'pages/WHOIS.html', {
                'domain_info': domain_info,
                'error_message': None
            })

        except whois.parser.PywhoisError:
            return render(request, 'pages/WHOIS.html', {
                'error_message': 'WHOIS data could not be retrieved. The domain may be private or unavailable.'
            })

        except Exception as e:
            return render(request, 'pages/WHOIS.html', {
                'error_message': f'An error occurred: {str(e)}'
            })


# دالة لتحميل التقرير بصيغة PDF
def download_pdf(request):
    # استرجاع بيانات WHOIS من الجلسة
    domain_info = request.session.get('domain_info',{})

    if not domain_info:
        return HttpResponse("No data to generate PDF", status=400)

    # تجهيز اسم الملف بناءً على الدومين
    domain_name = domain_info['domain'].replace(" ", "_")
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="whois_data_{domain_name}.pdf"'

    # إعداد التقرير
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
