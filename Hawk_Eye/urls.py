"""
URL configuration for Hawk_Eye project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('check-password/', include('PassManagement.urls')),
    path('darkweb_lookup/', include('DarkWebManagement.urls')),
    path('whois/', include('whois_lookup.urls')),
    path('dns/', include('dns_lookup.urls')),
    path('reverse_dns/', include('reverse_dns_lookup.urls')),
    path('telegram_lookup/', include('TelegramManagement.urls')),
    path('contact/', include('Contact.urls')),
    
]

# دعم عرض الملفات عند تشغيل السيرفر في وضع DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

