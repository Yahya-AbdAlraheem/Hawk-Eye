import os
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


# الحصول على مفتاح API من المتغيرات البيئية
ABUSEIPDB_API_KEY = os.getenv('ABUSEIPDB_API_KEY')


# الدالة reverse_dns_lookup
def reverse_dns_lookup(request):
    context = {}

    if request.method == 'POST':
        ip_address = request.POST.get('ip_address', '').strip()
        context['ip_address'] = ip_address

        blocked_ips = ['192.168.56.1', '192.168.100.26', '127.0.0.1']
        if ip_address in blocked_ips:
            error_message = "Access Denied. This IP Address is Blocked."
            return render(request, 'pages/reverse_dns_lookup.html', {'error_message': error_message})

        ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$|^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        if not re.match(ip_pattern, ip_address):
            error_message = "Sorry, The IP Address You Entered is Invalid. Please Type The Correct IP Address, Such as: 8.8.8.8."
            return render(request, 'pages/reverse_dns_lookup.html', {'error_message': error_message})

        # 1. PTR Record
        try:
            ptr_record = socket.gethostbyaddr(ip_address)
            context['hostname'] = ptr_record[0]
            context['ttl'] = ptr_record[1]
        except Exception:
            context['hostname'] = 'Not Found'
            context['ttl'] = 'Not Found'

        # 2. ASN & Org Info
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

        # 3. Geo Info
        try:
            response = requests.get(f'https://ipinfo.io/{ip_address}/json')
            if response.status_code == 200:
                data = response.json()
                city = data.get('city', 'Unknown')
                country = data.get('country', 'Unknown')
                context['location'] = f"{city}, {country}"
                loc = data.get('loc', '0,0')
                latitude, longitude = loc.split(',')
                context['location_lat'] = latitude
                context['location_lon'] = longitude
            else:
                context['location'] = 'Unavailable'
                context['location_lat'] = '0'
                context['location_lon'] = '0'
        except Exception:
            context['location'] = 'Unavailable'
            context['location_lat'] = '0'
            context['location_lon'] = '0'

        # 4. ISP
        try:
            response = requests.get(f'https://ipinfo.io/{ip_address}/json')
            if response.status_code == 200:
                data = response.json()
                context['isp'] = data.get('org', 'Unknown')
            else:
                context['isp'] = 'Unavailable'
        except Exception:
            context['isp'] = 'Unavailable'

        # 5. AbuseIPDB
        try:
            headers = {
                'Accept': 'application/json',
                'Key': ABUSEIPDB_API_KEY
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

        # Save to session
        request.session['reverse_dns_results'] = {
            'ptr_record': [context.get('hostname', 'N/A')],
            'ttl': context.get('ttl', 'N/A'),
            'asn': context.get('asn', 'N/A'),
            'org': context.get('org', 'N/A'),
            'asn_description': context.get('asn_description', 'N/A'),
            'location': context.get('location', 'N/A'),
            'latitude': context.get('location_lat', '0'),
            'longitude': context.get('location_lon', '0'),
            'isp': context.get('isp', 'N/A'),
            'abuse_confidence': context.get('abuse_confidence', 'N/A'),
            'total_reports': context.get('total_reports', 'N/A'),
        }

    return render(request, 'pages/reverse_dns_lookup.html', context)

# =============================
# تحميل الـ PDF
def download_pdf(request, ip_address):
    ip_address = unquote(ip_address)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    title_style = styles["Heading1"]
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], spaceAfter=10)

    flowables = []
    flowables.append(Paragraph(f"Reverse DNS Lookup Results for {ip_address}", title_style))
    flowables.append(Spacer(1, 12))

    results = request.session.get('reverse_dns_results', {})
    if not results:
        flowables.append(Paragraph("No Reverse DNS data available.", normal_style))
    else:
        def add_section(label, value):
            flowables.append(Paragraph(label, section_style))
            if isinstance(value, list):
                items = [ListItem(Paragraph(item, normal_style)) for item in value]
                flowables.append(ListFlowable(items, bulletType='bullet', leftIndent=20))
            else:
                flowables.append(Paragraph(str(value), normal_style))
            flowables.append(Spacer(1, 12))

        add_section("Hostname", results.get('ptr_record', ["No Hostname Found."]))
        add_section("Org", results.get('org', "No Org Found."))
        add_section("ISP", results.get('isp', "No ISP Found."))
        add_section("ASN Description", results.get('asn_description', "No ASN Description Found."))
        add_section("TTL", results.get('ttl', "No TTL Found."))
        add_section("Abuse Confidence", results.get('abuse_confidence', "No Abuse Confidence Found."))
        add_section("Total Reports", results.get('total_reports', "No Total Reports Found."))
        add_section("Location", results.get('location', "No Location Found."))
        add_section("Latitude", results.get('latitude', "Not Available"))
        add_section("Longitude", results.get('longitude', "Not Available"))

    doc.build(flowables)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{ip_address}_reverse_dns_lookup_results.pdf"'
    return response
