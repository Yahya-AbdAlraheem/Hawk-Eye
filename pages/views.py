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