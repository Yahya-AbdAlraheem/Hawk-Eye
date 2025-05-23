import os
import hashlib
from django.core.management.base import BaseCommand
from PassManagement.models import *

class Command(BaseCommand):
    help = "Remove duplicate passwords from rockyou.txt and save unique ones."

    def handle(self, *args, **kwargs):
        input_file_path = r"C:\Users\user\Downloads\rockyou.txt"  
        output_file_path = r"C:\Users\user\Downloads\rockyou_no_duplicates.txt"

        # عداد الكلمات المخزنة
        word_counter = 0

        try:
            if not os.path.exists(input_file_path):
                self.stderr.write(self.style.ERROR(f"File not found: {input_file_path}"))
                return

            # قراءة الملف وإزالة التكرارات
            with open(input_file_path, "r", encoding="latin1") as file:
                unique_passwords = set(file.read().splitlines())

            # حفظ الكلمات غير المكررة في ملف جديد
            with open(output_file_path, "w", encoding="latin1") as file:
                file.write("\n".join(unique_passwords))

            self.stdout.write(self.style.SUCCESS(f"Duplicate passwords removed. File saved to: {output_file_path}"))
        
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {e}"))

        # قراءة الكلمات من الملف
        with open(output_file_path, "r", encoding="latin1", errors="ignore") as file:
            for line in file:
                word = line.strip()
                if not word:
                    continue

                first_char = word[0]

                # تحديد الجدول بناءً على أول حرف
                if first_char.islower():
                    model_class = globals().get(f"Lowercase_{first_char}")
                elif first_char.isupper():
                    model_class = globals().get(f"{first_char}")
                elif first_char.isdigit():
                    model_class = globals().get(f"table_{first_char}")
                else:
                    model_class = SomthingElse

                if model_class:
                    try:
                        hashed_word = hashlib.sha512(word.encode()).hexdigest()
                        model_class.objects.create(hash=hashed_word)
                        word_counter += 1  # زيادة العداد عند إضافة كلمة جديدة
                        self.stdout.write(self.style.SUCCESS(f"Inserted word number {word_counter}: {word} into table: {model_class.__name__}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error inserting word {word} into {model_class.__name__}: {e}"))
                else:
                    self.stdout.write(self.style.WARNING(f"⚠ Table for {word} does not exist, skipping..."))

# To Run Code : python manage.py hash_passwords