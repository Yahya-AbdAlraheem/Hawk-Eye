from django.urls import path 
from . import views  

urlpatterns = [
    path('', views.WelcomePage, name='WelcomePage'),  
    path('hawk-eye/', views.HomePage, name='HomePage'),
    path('check-password/', views.CreatePassword, name='CreatePassword'),
    path('about-us/', views.AboutUs, name='AboutUs'),
    path('contact/', views.Contact, name='Contact'),
    path('whois_lookup/', views.whois_lookup, name='whois_lookup'),
    path('dns_lookup/', views.dns_lookup, name='dns_lookup'),
]
