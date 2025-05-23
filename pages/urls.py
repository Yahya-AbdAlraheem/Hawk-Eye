from django.urls import path 
from . import views  

urlpatterns = [
    path('', views.WelcomePage, name='WelcomePage'),  
    path('home/', views.HomePage, name='HomePage'),
    path('check-password/', views.CreatePassword, name='CreatePassword'),
    path('about-us/', views.AboutUs, name='AboutUs'),
    path('contact/', views.Contact, name='Contact'),
    path('whois_lookup/', views.whois_lookup, name='whois_lookup'),
    path('dns_lookup/', views.dns_lookup, name='dns_lookup'),
    path('reverse_dns_lookup/', views.reverse_dns_lookup, name='reverse_dns_lookup'),
    path('TelegramManagement/', views.TelegramManagement, name='TelegramManagement'),
    path('contact/', views.Contact, name= 'Contact'), 
]