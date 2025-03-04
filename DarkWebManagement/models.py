from functools import cache
from django.db import models
from .AES import encrypt, decrypt  # استيراد وظائف التشفير وفك التشفير

class ExtractedData(models.Model):
    CATEGORY_CHOICES = [
        ('letter', 'Letter'),
        ('number', 'Number'),
        ('symbol', 'Symbol'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    content = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    first_character = models.CharField(max_length=1, blank=True, null=True)
    second_character = models.CharField(max_length=1, blank=True, null=True)
    third_character = models.CharField(max_length=1, blank=True, null=True)
    fourth_character = models.CharField(max_length=1, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to='darkweb_images/', blank=True, null=True)
    video = models.FileField(upload_to='darkweb_videos/', blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['first_character', 'second_character']),
            models.Index(fields=['third_character', 'fourth_character']),
        ]

    def save(self, *args, **kwargs):
        # تشفير البيانات النصية فقط
        if self.content:
            self.content = encrypt(self.content)
            self.first_character = self.content[0].upper() if self.content else ''
            if len(self.content) > 1:
                self.second_character = self.content[1].upper()
            if len(self.content) > 2:
                self.third_character = self.content[2].upper()
            if len(self.content) > 3:
                self.fourth_character = self.content[3].upper()
        
        super().save(*args, **kwargs)

    def get_decrypted_content(self):
        return decrypt(self.content) if self.content else None
    
    @staticmethod
    def get_cached_data(content):
        # محاولة جلب البيانات من الكاش
        cached_data = cache.get(content)
        
        if cached_data:
            return cached_data
        
        data = ExtractedData.objects.filter(content=content).first()
        
        if data:
            cache.set(content, data, timeout=60*15)
        
        return data
