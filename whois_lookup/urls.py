from django.urls import path
from . import views

urlpatterns = [
    path('', views.whois_lookup, name='whois_lookup'),
    path('download_pdf/', views.download_pdf, name='download_pdf'),
]
