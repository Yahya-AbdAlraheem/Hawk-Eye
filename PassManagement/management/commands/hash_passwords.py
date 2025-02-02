import os
from django.core.management.base import BaseCommand
from argon2 import PasswordHasher
from PassManagement.models import PasswordHash  

class Command(BaseCommand):
    help = "Remove duplicate passwords and hash the unique ones from rockyou.txt and store them in the database"

    def handle(self, *args, **kwargs):
        input_file_path = r"C:\Users\user\Downloads\rockyou.txt"  # المسار الأصلي للملف
        output_file_path = r"C:\Users\user\Downloads\rockyou_no_duplicates.txt"  # مسار الملف بعد إزالة التكرار

        # خطوة 1: حذف التكرار
        try:
            with open(input_file_path, 'r', encoding='latin-1') as file:
                passwords = set()  # استخدام set لحذف التكرار
                for line in file:
                    password = line.strip()
                    if password:
                        passwords.add(password)  # إضافة كلمة المرور إلى المجموعة (حذف التكرار)

            # كتابة الكلمات المصفاة إلى ملف جديد
            with open(output_file_path, 'w', encoding='latin-1') as file:
                for password in passwords:
                    file.write(password + '\n')

            self.stdout.write(self.style.SUCCESS(f"Duplicate passwords removed successfully. File saved to {output_file_path}"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {input_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))

        # خطوة 2: تجزئة الكلمات المصفاة
        ph = PasswordHasher()
        try:
            with open(output_file_path, 'r', encoding='latin-1') as file:
                for line in file:
                    password = line.strip()
                    if password:
                        try:
                            hashed_password = ph.hash(password)
                            PasswordHash.objects.create(hash=hashed_password)
                        except Exception as e:
                            self.stdout.write(f"Error processing {password}: {e}")

            self.stdout.write(self.style.SUCCESS("Passwords hashed and stored successfully!"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {output_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))

        
# To Run Code : python manage.py hash_passwords