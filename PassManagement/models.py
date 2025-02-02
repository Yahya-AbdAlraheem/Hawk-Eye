from django.db import models

# Create your models here.

class PasswordHash(models.Model):
    hash = models.TextField()  # النص المشفر باستخدام Argon2
    created_at = models.DateTimeField(auto_now_add=True)  # تعيين الوقت تلقائيًا عند إنشاء السجل
