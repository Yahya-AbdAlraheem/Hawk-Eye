from django.db import models
from django.core.cache import cache
from .AES import encrypt, decrypt

class ExtractedData(models.Model):
    CATEGORY_CHOICES = [
        ('letter', 'Letter'),
        ('number', 'Number'),
        ('symbol', 'Symbol'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    description = models.TextField(blank=True, null=True)  
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    first_character = models.CharField(max_length=1, blank=True, null=True)
    second_character = models.CharField(max_length=1, blank=True, null=True)
    third_character = models.CharField(max_length=1, blank=True, null=True)
    fourth_character = models.CharField(max_length=1, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to='darkweb_images/', blank=True, null=True)
    video = models.FileField(upload_to='darkweb_videos/', blank=True, null=True)

    title_1 = models.TextField(blank=True, null=True)  # عنوان H1
    title_2 = models.TextField(blank=True, null=True)  # عنوان H2
    title_3 = models.TextField(blank=True, null=True)  # عنوان H3

    url = models.URLField(max_length=200, blank=True, null=True)  # الرابط الذي تم البحث فيه
    query = models.CharField(max_length=255, blank=True, null=True)  # الكلمة المفتاحية للبحث

    class Meta:
        indexes = [
            models.Index(fields=['first_character', 'second_character']),
            models.Index(fields=['third_character', 'fourth_character']),
        ]
    
    def save(self, *args, **kwargs):
        # حفظ البيانات في الكاش أولًا، ثم التحقق من التكرار قبل الحفظ في الموديل   
        if not self.query:
            return  

        # إنشاء نسخة غير مشفرة من البيانات للكاش
        raw_data = {
            'title_1': self.title_1,
            'title_2': self.title_2,
            'title_3': self.title_3,
            'description': self.description,
            'image': self.image.url if self.image else None,
            'video': self.video.url if self.video else None,
            'url': self.url
        }

        cache_key = f"query:{self.query.lower()}"
        cached_data = cache.get(cache_key, set())

        # التحقق من التكرار قبل الحفظ في الكاش
        if str(raw_data) not in cached_data:
            cached_data.add(str(raw_data))
            cache.set(cache_key, cached_data, timeout=600)

        # التحقق من التكرار قبل الحفظ في قاعدة البيانات
        duplicate = ExtractedData.objects.filter(
            title_1=encrypt(self.title_1) if self.title_1 else None,
            title_2=encrypt(self.title_2) if self.title_2 else None,
            title_3=encrypt(self.title_3) if self.title_3 else None,
            description=encrypt(self.description) if self.description else None,
            url=self.url
        ).exists()

        if duplicate:
            return  

        # تشفير البيانات قبل الحفظ في قاعدة البيانات
        self.title_1 = encrypt(self.title_1) if self.title_1 else None
        self.title_2 = encrypt(self.title_2) if self.title_2 else None
        self.title_3 = encrypt(self.title_3) if self.title_3 else None
        self.description = encrypt(self.description) if self.description else None

        super().save(*args, **kwargs)

    def get_decrypted_title_1(self):
        return decrypt(self.title_1) if self.title_1 else None

    def get_decrypted_title_2(self):
        return decrypt(self.title_2) if self.title_2 else None

    def get_decrypted_title_3(self):
        return decrypt(self.title_3) if self.title_3 else None

    def get_decrypted_description(self):
        return decrypt(self.description) if self.description else None
