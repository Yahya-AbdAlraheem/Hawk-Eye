from django.urls import path
from . import views  

urlpatterns = [
    path('', views.WelcomePage, name='WelcomePage'),  
    path('hawk-eye/', views.HomePage, name='HomePage'),
    path('create-password/', views.CreatePassword, name='CreatePassword'),
    path('about-us/', views.AboutUs, name='AboutUs'),
    path('contact/', views.Contact, name='Contact')
]
