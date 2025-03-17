from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from passlib.hash import argon2
from .models import *
from concurrent.futures import ThreadPoolExecutor

class CheckPasswordView(View):
    def post(self, request):
        password = request.POST.get("password")

        if not password:
            return JsonResponse({"status": "error", "message": "Password is required"}, status=400)

        first_char = password[0]
        if first_char.islower():
            model_class = globals().get(f"Lowercase_{first_char}")
        elif first_char.isupper():
            model_class = globals().get(f"{first_char}")
        elif first_char.isdigit():
            model_class = globals().get(f"table_{first_char}")
        else:
            model_class = SomthingElse

        try:
            if not model_class:
                return JsonResponse({"status": "error", "message": "Invalid table selection"}, status=400)

            # مقارنة التجزئة بدون الـ Salt
            stored_hashes = model_class.objects.values_list("hash", flat=True)
            stored_hashes = set(stored_hashes)

            # استخدم ThreadPoolExecutor لتوزيع العمل بين عدة خيوط
            def check_hash(stored_hash):
                return argon2.verify(password, stored_hash)

            with ThreadPoolExecutor() as executor:
                results = list(executor.map(check_hash, stored_hashes))

            # إذا كان أحد الـ hashes متطابق، أعد الجواب
            if any(results):
                return JsonResponse({"status": "weak", "message": "Weak password! Already exists."})

            return JsonResponse({"status": "strong", "message": "Strong password! Not found in database."})

        except Exception as e:
            return JsonResponse({"⚠️status": "error", "message": str(e)}, status=500)
