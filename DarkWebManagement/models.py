from django.db import models
from .AES import encrypt, decrypt

class ExtractedData(models.Model):
    CATEGORY_CHOICES = [
        ('letter', 'Letter'),
        ('number', 'Number'),
        ('symbol', 'Symbol'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    content = models.TextField(blank=True, null=True)  # العنوان المشفر
    description = models.TextField(blank=True, null=True)  # الوصف المشفر
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    first_character = models.CharField(max_length=1, blank=True, null=True)
    second_character = models.CharField(max_length=1, blank=True, null=True)
    third_character = models.CharField(max_length=1, blank=True, null=True)
    fourth_character = models.CharField(max_length=1, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to='darkweb_images/', blank=True, null=True)
    video = models.FileField(upload_to='darkweb_videos/', blank=True, null=True)

    h1 = models.TextField(blank=True, null=True)  
    h2 = models.TextField(blank=True, null=True)  
    h3 = models.TextField(blank=True, null=True)  

    class Meta:
        indexes = [
            models.Index(fields=['first_character', 'second_character']),
            models.Index(fields=['third_character', 'fourth_character']),
        ]

    def save(self, *args, **kwargs):
        if self.content:
            self.content = encrypt(self.content)
        if self.description:
            self.description = encrypt(self.description)
        if self.h1:
            self.h1 = encrypt(self.h1)
        if self.h2:
            self.h2 = encrypt(self.h2)
        if self.h3:
            self.h3 = encrypt(self.h3)

        super().save(*args, **kwargs)

    def get_decrypted_content(self):
        return decrypt(self.content) if self.content else None

    def get_decrypted_description(self):
        return decrypt(self.description) if self.description else None

    def get_decrypted_h1(self):
        return decrypt(self.h1) if self.h1 else None

    def get_decrypted_h2(self):
        return decrypt(self.h2) if self.h2 else None

    def get_decrypted_h3(self):
        return decrypt(self.h3) if self.h3 else None
