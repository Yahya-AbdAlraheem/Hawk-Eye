import socket
import re
import requests
from ipwhois import IPWhois
from ipwhois.net import IPDefinedError
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from io import BytesIO
from urllib.parse import unquote


# الدالة reverse_dns_lookup
def reverse_dns_lookup(request):
    context = {}

    if request.method == 'POST':
        ip_address = request.POST.get('ip_address')
        context['ip_address'] = ip_address
        
        ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$|^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'

        if not re.match(ip_pattern, ip_address):
            error_message = "Sorry, The IP Address You Entered is Invalid. Please Type The Correct IP Address, Such as: 192.168.1.1."
            return render(request, 'pages/reverse_dns_lookup.html', {'error_message': error_message})

        # 1. PTR Record
        try:
            ptr_record = socket.gethostbyaddr(ip_address)
            context['hostname'] = ptr_record[0]
            context['ttl'] = ptr_record[1]  # استخراج TTL
        except Exception:
            context['hostname'] = 'Not Found'
            context['ttl'] = 'Not Found'  # إذا لم يتم العثور على TTL

        # 2. ASN & Org Info using ipwhois
        try:
            obj = IPWhois(ip_address)
            res = obj.lookup_rdap()

            context['asn'] = res.get('asn', 'Unknown')
            context['org'] = res.get('network', {}).get('name', 'Unknown')
            context['asn_description'] = res.get('network', {}).get('type', 'Public Network')

        except IPDefinedError:
            context['asn'] = context['org'] = context['asn_description'] = 'Error'
        except Exception:
            context['asn'] = context['org'] = context['asn_description'] = 'Not Found'

        # 3. Geo Info from ipinfo.io
        try:
            response = requests.get(f'https://ipinfo.io/{ip_address}/json')
            if response.status_code == 200:
                data = response.json()
                city = data.get('city', 'Unknown')
                country = data.get('country', 'Unknown')
                context['location'] = f"{city}, {country}"
                location_lat, location_lon = data.get('loc', '0,0').split(',')
                context['location_lat'] = location_lat
                context['location_lon'] = location_lon
                context['isp'] = data.get('org', 'Unknown')
            else:
                context['location'] = context['isp'] = 'Unavailable'
                context['location_lat'] = context['location_lon'] = '0'
        except Exception:
            context['location'] = context['isp'] = 'Unavailable'
            context['location_lat'] = context['location_lon'] = '0'

        # 4. AbuseIPDB Check
        try:
            headers = {
                'Accept': 'application/json',
                'Key': 'bd51423d3bc0191419b9085d47cd81968879af02c047111af3d1579d7f61552411038efab62fcd1e'
            }
            params = {
                'ipAddress': ip_address,
                'maxAgeInDays': '90'
            }
            r = requests.get("https://api.abuseipdb.com/api/v2/check", headers=headers, params=params)
            if r.status_code == 200:
                d = r.json().get("data", {})
                context['abuse_confidence'] = d.get('abuseConfidenceScore', 'N/A')
                context['total_reports'] = d.get('totalReports', 'N/A')
            else:
                context['abuse_confidence'] = context['total_reports'] = 'Unavailable'
        except Exception:
            context['abuse_confidence'] = context['total_reports'] = 'Error'

        # Save data to session for PDF
        request.session['reverse_dns_results'] = {  # تغيير المفتاح هنا
            'ptr_record': [context.get('hostname', 'N/A')],
            'ttl': context.get('ttl', 'N/A'),  # إضافة الـ TTL
            'asn': context.get('asn', 'N/A'),
            'org': context.get('org', 'N/A'),
            'asn_description': context.get('asn_description', 'N/A'),
            'location': context.get('location', 'N/A'),
            'isp': context.get('isp', 'N/A'),
            'abuse_confidence': context.get('abuse_confidence', 'N/A'),
            'total_reports': context.get('total_reports', 'N/A'),
        }

    return render(request, 'pages/reverse_dns_lookup.html', context)


# دالة تحميل PDF
def download_pdf(request, ip_address):
    ip_address = unquote(ip_address)  # إزالة أي ترميز URL
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    title_style = styles["Heading1"]
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], spaceAfter=10)

    flowables = []
    flowables.append(Paragraph(f"Reverse DNS Lookup Results for {ip_address}", title_style))
    flowables.append(Spacer(1, 12))

    # استخراج البيانات من الجلسة باستخدام المفتاح الصحيح
    results = request.session.get('reverse_dns_results', {})

    # التحقق من وجود البيانات في الجلسة
    if not results:
        flowables.append(Paragraph("No Reverse DNS data available.", normal_style))
    else:
        # دالة لإضافة أقسام جديدة في الـ PDF
        def add_section(label, value):
            flowables.append(Paragraph(label, section_style))
            if isinstance(value, list):  # إذا كانت القيمة قائمة
                items = [ListItem(Paragraph(item, normal_style)) for item in value]
                flowables.append(ListFlowable(items, bulletType='bullet', leftIndent=20))
            else:  # إذا كانت القيمة غير قائمة
                flowables.append(Paragraph(str(value), normal_style))
            flowables.append(Spacer(1, 12))

        # إضافة الأقسام الخاصة بالـ Reverse DNS
        add_section("Hostname", results.get('ptr_record', ["No Hostname Found."]))
        add_section("ASN", results.get('asn', "No ASN Found."))
        add_section("Org", results.get('org', "No Org Found."))
        add_section("ASN Description", results.get('asn_description', "No ASN Description Found."))
        add_section("Location", results.get('location', "No Location Found."))
        add_section("ISP", results.get('isp', "No ISP Found."))
        add_section("Abuse Confidence", results.get('abuse_confidence', "No Abuse Confidence Found."))
        add_section("Total Reports", results.get('total_reports', "No Total Reports Found."))
        add_section("TTL", results.get('ttl', "No TTL Found."))  
        

    # بناء الـ PDF
    doc.build(flowables)

    # إرجاع الـ PDF للمستخدم
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{ip_address}_reverse_dns_lookup_results.pdf"'
    return response
