from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from .models import PasswordHash

def check_password_view(request):
    message = None
    try:
        if request.method == "POST":
            # أخذ كلمة المرور من الطلب
            password = request.POST.get('password')

            # التحقق من إذا كانت كلمة المرور موجودة بالفعل في قاعدة البيانات
            existing_hashes = PasswordHash.objects.values_list('hash', flat=True)
            if any(check_password(password, stored_hash) for stored_hash in existing_hashes):
                message = "Weak password. It's already used."
            else:
                # تحويل كلمة المرور إلى تجزئة باستخدام Argon2
                hashed_password = make_password(password, hasher='argon2')

                # حفظ التجزئة في قاعدة البيانات
                PasswordHash.objects.create(hash=hashed_password)
                message = "Strong Password."

    except Exception as e:
        message = f"An error occurred: {e}"

    # عرض الرسالة للمستخدم في الـ template
    return render(request, 'CreatePassword.html', {'message': message})
