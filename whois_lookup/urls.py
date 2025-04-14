from django.urls import path
from . import views

urlpatterns = [
    path('', views.whois_lookup, name='whois_lookup'),
]
