import re
import dns.resolver
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from io import BytesIO
from urllib.parse import unquote


def dns_lookup(request):
    results = {}

    if request.method == "POST":
        domain_name = request.POST.get('domain_name')
        
        domain_name = re.sub(r'^https?://', '', domain_name, flags=re.IGNORECASE)
        domain_name = re.sub(r'^www\.', '', domain_name, flags=re.IGNORECASE)
        domain_name = domain_name.strip().capitalize()

        # نمط التحقق من أسماء DNS
        dns_pattern = r'^(?!-)([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,}$'

        # تحقق من صحة اسم المجال
        if not re.match(dns_pattern, domain_name):
            error_message = "Sorry, The Domain Name You Entered is Invalid. Please Type The Correct Name, Such as: example.com."
            return render(request, 'pages/dns_lookup.html', {'error_message': error_message})

        try:
            try:
                a_records = dns.resolver.resolve(domain_name, 'A')
                results['a_record'] = [str(ip.address) for ip in a_records]
            except dns.resolver.NoAnswer:
                results['a_record'] = ["No IPv4 Record Found."]

            try:
                aaaa_records = dns.resolver.resolve(domain_name, 'AAAA')
                results['ipv6_record'] = [str(ip.address) for ip in aaaa_records]
            except dns.resolver.NoAnswer:
                results['ipv6_record'] = ["No IPv6 Record Found."]

            try:
                cname_records = dns.resolver.resolve(domain_name, 'CNAME')
                results['cname_record'] = [str(cname.target) for cname in cname_records]
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
                results['cname_record'] = []

            try:
                mx_records = dns.resolver.resolve(domain_name, 'MX')
                results['mx_record'] = [str(mx.exchange) for mx in mx_records]
            except dns.resolver.NoAnswer:
                results['mx_record'] = ["No Email Servers Found."]

            try:
                ns_records = dns.resolver.resolve(domain_name, 'NS')
                all_ns = [str(ns.target).rstrip('.') for ns in ns_records]  # نشيل النقطة من نهاية الاسم
                valid_ns = [ns for ns in all_ns if re.match(dns_pattern, ns)]
                results['ns_record'] = valid_ns if valid_ns else ["No valid DNS Servers found."]
            except dns.resolver.NoAnswer:
                results['ns_record'] = ["No DNS Servers Found."]

            try:
                txt_records = dns.resolver.resolve(domain_name, 'TXT')
                results['txt_record'] = [b''.join(txt.strings).decode(errors='ignore') for txt in txt_records]
            except dns.resolver.NoAnswer:
                results['txt_record'] = ["No TXT Records Found."]

            try:
                ttl_record = dns.resolver.resolve(domain_name, 'A')
                results['ttl'] = str(ttl_record.rrset.ttl)
            except dns.resolver.NoAnswer:
                results['ttl'] = "No Time to Live Found."

        except dns.resolver.NXDOMAIN:
            results['message'] = f"The domain '{domain_name}' does not exist."
        except dns.resolver.Timeout:
            results['message'] = "The request timed out. Please try again later."
        except Exception as e:
            results['message'] = f"An error occurred: {str(e)}"

        request.session['dns_results'] = results

        return render(request, 'pages/dns_lookup.html', {
            'results': results,
            'domain_name': domain_name
        })

    return render(request, 'pages/dns_lookup.html')




def download_pdf(request, domain_name):
    domain_name = unquote(domain_name)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    title_style = styles["Heading1"]
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], spaceAfter=10)

    flowables = []
    flowables.append(Paragraph(f"DNS Lookup Results for {domain_name}", title_style))
    flowables.append(Spacer(1, 12))

    results = request.session.get('dns_results', {})

    if not results:
        flowables.append(Paragraph("No DNS data available.", normal_style))
    else:
        def add_section(label, value):
            flowables.append(Paragraph(label, section_style))
            if isinstance(value, list):
                items = [ListItem(Paragraph(item, normal_style)) for item in value]
                flowables.append(ListFlowable(items, bulletType='bullet', leftIndent=20))
            else:
                flowables.append(Paragraph(str(value), normal_style))
            flowables.append(Spacer(1, 12))

        add_section("IPv4", results.get('a_record', ["No IPv4 Record Found."]))
        add_section("IPv6", results.get('ipv6_record', ["No IPv6 Record Found."]))
        add_section("Alias Name", results.get('cname_record', ["No Alias Name Record Found."]))
        add_section("DNS Servers", results.get('ns_record', ["No DNS Servers Found."]))
        add_section("Email Servers", results.get('mx_record', ["No Email Servers Found."]))
        add_section("Time to Live", results.get('ttl', "No Time to Live Found."))
        add_section("TXT Record", results.get('txt_record', ["No TXT Records Found."]))

    doc.build(flowables)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{domain_name}_dns_lookup_results.pdf"'
    return response
