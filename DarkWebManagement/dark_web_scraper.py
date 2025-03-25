import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from .models import ExtractedData
from django.conf import settings
from .MediaCompression import compress_image, compress_video  # استدعاء دوال الضغط

# إعداد جلسة الاتصال بـ Tor
def get_tor_session():
    session = requests.Session()
    session.proxies = {'http': 'socks5h://192.168.190.128:9050',
                       'https': 'socks5h://192.168.190.128:9050'}
    return session

# التحقق من الاتصال بـ Tor
def check_tor_connection():
    try:
        response = requests.get('http://check.torproject.org', proxies={'http': 'socks5h://192.168.190.128:9050', 'https': 'socks5h://192.168.190.128:9050'}, timeout=10)
        return "Congratulations. This browser is configured to use Tor." in response.text
    except requests.RequestException:
        return False

# تحميل الملفات (صور وفيديوهات)
def download_file(url, base_url, folder_path):
    try:
        full_url = urljoin(base_url, url)  # التعامل مع الروابط النسبية
        response = requests.get(full_url, timeout=15)
        response.raise_for_status()
        
        file_name = os.path.basename(url)
        file_path = os.path.join(folder_path, file_name)

        temp_file = NamedTemporaryFile(delete=False)
        with open(temp_file.name, 'wb') as f:
            f.write(response.content)
        
        # ضغط الصور أو الفيديوهات
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            compress_image(temp_file.name)
        elif file_name.lower().endswith(('.mp4', '.mkv', '.avi')): 
            compress_video(temp_file.name)

        return temp_file.name  # إرجاع مسار الملف المؤقت
    except requests.RequestException:
        return None

# استخراج البيانات من صفحة الويب
def scrape_page(url, session):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        results = []
        futures = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            for item in soup.find_all('div', class_='result'):
                title_1 = item.find('h1').text if item.find('h1') else 'No Title 1'
                title_2 = item.find('h2').text if item.find('h2') else 'No Sub Title 2'
                title_3 = item.find('h3').text if item.find('h3') else 'No Sub Title 3'
                description = item.find('p').text if item.find('p') else 'No Description'
                link = item.find('a')['href'] if item.find('a') else 'No Link'
                
                image_url = item.find('img')['src'] if item.find('img') else None
                video_tag = item.find('video')
                video_url = video_tag.find('source')['src'] if video_tag and video_tag.find('source') else None

                # تحميل الصورة والفيديو إذا كانا موجودين
                image_path = video_path = None
                if image_url:
                    futures.append(executor.submit(download_file, image_url, url, os.path.join(settings.MEDIA_ROOT, 'darkweb_images')))
                if video_url:
                    futures.append(executor.submit(download_file, video_url, url, os.path.join(settings.MEDIA_ROOT, 'darkweb_videos')))

                # معالجة النتائج بعد اكتمال التحميل
                for future in as_completed(futures):
                    file_path = future.result()
                    if file_path:
                        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                            image_path = file_path
                        elif file_path.lower().endswith(('.mp4', '.mkv', '.avi')):
                            video_path = file_path

                results.append({
                    'title_1': title_1,
                    'title_2': title_2,
                    'title_3': title_3,
                    'description': description,
                    'image': image_path,
                    'video': video_path,
                    'url': link
                })

        return results
    except requests.RequestException:
        return []

# البحث المتوازي في الدارك ويب
def scrape_darkweb_parallel(query):
    if not check_tor_connection():
        return []

    session = get_tor_session()
    base_url = f"http://exampledarkweb.onion/search?q={quote(query)}"

    results = []
    page_number = 1

    while True:
        url = f"{base_url}&page={page_number}"
        page_results = scrape_page(url, session)
        if not page_results:
            break
        results.extend(page_results)
        page_number += 1

    return results

# البحث في الدارك ويب وحفظ البيانات
def search_darkweb(query):
    raw_results = scrape_darkweb_parallel(query)

    for raw in raw_results:
        image_file = video_file = None

        # حفظ الصور والفيديوهات في قاعدة البيانات
        if raw['image']:
            with open(raw['image'], 'rb') as img_file:
                image_file = File(img_file)

        if raw['video']:
            with open(raw['video'], 'rb') as vid_file:
                video_file = File(vid_file)

        extracted_data = ExtractedData(
            title_1=raw['title_1'],
            title_2=raw['title_2'],
            title_3=raw['title_3'],
            description=raw['description'],
            image=image_file,
            video=video_file,
            url=raw['url'],
            query=query
        )
        extracted_data.save()

        # حذف الملفات المؤقتة
        if raw['image']:
            os.remove(raw['image'])
        if raw['video']:
            os.remove(raw['video'])

    return raw_results
