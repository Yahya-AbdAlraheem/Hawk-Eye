from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import os

# قراءة المفتاح من المتغير البيئي
SECRET_KEY = os.getenv("AES_SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("Key Not Found in Environmental Variables!")

SECRET_KEY = SECRET_KEY.encode()  # تحويله إلى bytes

# التحقق من طول المفتاح (يجب أن يكون 16, 24, أو 32 بايت)
if len(SECRET_KEY) not in [16, 24, 32]:
    raise ValueError("Invalid Key Length! Must be 16, 24, or 32 bytes.")

# وظيفة لتشفير النص
def encrypt(data: str) -> str:
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    iv = cipher.iv  # الـ IV العشوائي
    return base64.b64encode(iv + ct_bytes).decode('utf-8')  # تخزين IV مع النص المشفر

# وظيفة لفك تشفير النص
def decrypt(data: str) -> str:
    raw_data = base64.b64decode(data)  # فك تشفير Base64
    iv = raw_data[:16]  # استخراج أول 16 بايت كـ IV
    ct = raw_data[16:]  # الباقي هو النص المشفر
    
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode('utf-8')


# اختبار التشفير وفك التشفير
#if __name__ == "__main__":
#    text = "Hiii"
#    encrypted = encrypt(text)
#    decrypted = decrypt(encrypted)
#
#   print(f"🔒 Encrypted: {encrypted}")
#    print(f"🔓 Decrypted: {decrypted}")
