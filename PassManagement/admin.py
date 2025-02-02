from django.contrib import admin
from .models import PasswordHash

# Register your models here.
admin.site.register(PasswordHash)
admin.site.site_header='Database Administrator'
admin.site.site_title='Hawk Eye'