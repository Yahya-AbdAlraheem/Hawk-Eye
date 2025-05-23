from django.shortcuts import render


# Create your views here.

def WelcomePage(request):
    return render(request, 'pages/WelcomePage.html')

def HomePage(request):
    return render(request, 'pages/HomePage.html')

def CreatePassword(request):
    return render(request, 'pages/CreatePassword.html')

def AboutUs(request):
    return render(request, 'pages/AboutUs.html')

def Contact(request):
    return render(request, 'pages/Contact.html')

def whois_lookup(request):
    return render(request, 'pages/whois_lookup.html')

def dns_lookup(request):
    return render(request, 'pages/dns_lookup.html')

def reverse_dns_lookup(request):
    return render(request, 'pages/reverse_dns_lookup.html')

def TelegramManagement(request):
    return render(request, 'pages/TelegramManagement.html')

def Contact(request):
    return render(request, 'pages/Contact.html')