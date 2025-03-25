from PIL import Image
import subprocess
import os

# الضغط على الصور باستخدام Pillow
def compress_image(image_path):
    try:
        with Image.open(image_path) as img:
            img.save(image_path, quality=85)  # ضبط الجودة حسب الحاجة
        print(f"Image {image_path} compressed successfully.")
    except Exception as e:
        print(f"Error compressing image {image_path}: {e}")

# الضغط على الفيديوهات باستخدام ffmpeg
def compress_video(video_path):
    try:
        compressed_video_path = video_path.replace('.mp4', '_compressed.mp4')  # حفظ الفيديو المضغوط
        subprocess.run(['ffmpeg', '-i', video_path, '-vcodec', 'libx264', '-crf', '28', compressed_video_path])
        os.rename(compressed_video_path, video_path)  # استبدال الفيديو الأصلي بالفيديو المضغوط
        print(f"Video {video_path} compressed successfully.")
    except Exception as e:
        print(f"Error compressing video {video_path}: {e}")
