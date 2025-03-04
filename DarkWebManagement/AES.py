from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import os

# مفتاح AES يجب أن يكون 16 أو 24 أو 32 بايت
SECRET_KEY = os.urandom(32)  # يمكن أن تغيره لمفتاح ثابت إذا أردت

# وظيفة لتشفير النص
def encrypt(data: str) -> str:
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')  # حفظ ال IV
    ct = base64.b64encode(ct_bytes).decode('utf-8')  # تشفير النص نفسه
    return iv + ct  # نرجع الـ IV مع النص المشفر

# وظيفة لفك تشفير النص
def decrypt(data: str) -> str:
    iv = base64.b64decode(data[:24])  # أول 16 حرف تمثل الـ IV
    ct = base64.b64decode(data[24:])  # باقي النص هو النص المشفر
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode('utf-8')

