from django.urls import path
from . import views  

urlpatterns = [
    path('', views.WelcomePage, name='WelcomePage'),  
    path('home/', views.HomePage, name='HomePage'),
    path('creat_password/', views.CreatePassword, name='CreatePassword'),
    path('About_Us/', views.AboutUs, name='AboutUs'),
    path('Contact/', views.Contact, name='Contact')
]