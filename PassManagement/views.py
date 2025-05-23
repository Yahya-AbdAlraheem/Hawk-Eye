from django.shortcuts import render
from django.views import View
import hashlib
from .models import *
import re
import string

# الأحرف غير المرغوبة
UNWANTED_CHARS = [' ', '\n', '\t', '\r', '"', "'", '`', '<', '>', '{', '}', '[', ']', '\\', '/', '|', '~']

# دالة تنظيف الباسورد
def clean_password(password):
    for char in UNWANTED_CHARS:
        password = password.replace(char, '')
    return password.strip()

class CheckPasswordView(View):
    def post(self, request):
        raw_password = request.POST.get("password")

        if not raw_password:
            return render(request, 'pages/CreatePassword.html', {
                'message': "Password is required",
            })

        password = clean_password(raw_password)

        # تحقق من الأحرف غير المدعومة
        if re.search(r'[^\x00-\x7F]', password):  # أي شيء غير ASCII
            return render(request, 'pages/CreatePassword.html', {
                'error_message': "Error: Password contains unsupported characters. Please use only English letters, numbers, and standard symbols.",
            })

        if not password:
            return render(request, 'pages/CreatePassword.html', {
                'message': "Password contains only invalid characters.",
            })

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
                return render(request, 'pages/CreatePassword.html', {
                    'message': "Invalid Table Selection",
                })

            stored_hashes = set(model_class.objects.values_list("hash", flat=True))
            hashed_password = hashlib.sha512(password.encode()).hexdigest()

            if hashed_password in stored_hashes:
                return render(request, 'pages/CreatePassword.html', {
                    'message': "Password Leaked! It Was Previously Leaked in rockyou.txt Files.",
                })

            # لو ما كانت مسربة لكن قصيرة (<= 6)
            if len(password) < 8 or not any(char in string.punctuation for char in password):
                message = "Note: This Password Was Not Found in The rockyou.txt File. However, "
                if len(password) < 8 and not any(char in string.punctuation for char in password):
                    message += "it is Too Short and Lacks Special Characters. "
                elif len(password) < 8:
                    message += "it is Too Short. "
                elif not any(char in string.punctuation for char in password):
                    message += "it Lacks Special Characters. "

                message += "This Tool Still Checks For Leaks, But We Recommend Using Longer, More Complex Passwords."

                return render(request, 'pages/CreatePassword.html', {
                    'message': message,
                })

            return render(request, 'pages/CreatePassword.html', {
                'message': "Strong Password! Not Leaked Before in rockyou.txt Files.",
            })

        except Exception as e:
            return render(request, 'pages/CreatePassword.html', {
                'message': str(e),
            })
