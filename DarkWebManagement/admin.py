from django.contrib import admin

from DarkWebManagement.models import ExtractedData

# Register your models here.

admin.site.register(ExtractedData)
admin.site.site_header='Database Administrator'
admin.site.site_title='Hawk Eye'
