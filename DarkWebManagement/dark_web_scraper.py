import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from .models import ExtractedData
from django.conf import settings


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
        if "Congratulations. This browser is configured to use Tor." in response.text:
            print("Tor connection is successful!")
            return True
        else:
            print("Tor connection failed!")
            return False
    except requests.RequestException as e:
        print(f"Failed to connect to Tor: {e}")
        return False


# تحميل الملفات (صور وفيديوهات)
def download_file(url, folder_path):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        file_name = os.path.basename(url)
        file_path = os.path.join(folder_path, file_name)

        # حفظ الملف في المسار الصحيح
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return file_path
    except requests.RequestException as e:
        print(f"Error downloading file from {url}: {e}")
        return None


# استخراج البيانات من صفحة الويب
def scrape_page(url, session):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        results = []
        for item in soup.find_all('div', class_='result'):
            title_1 = item.find('h1').text if item.find('h1') else 'No Title 1'
            title_2 = item.find('h2').text if item.find('h2') else 'No Sub Title 2'
            title_3 = item.find('h3').text if item.find('h3') else 'No Sub Title 3'
            description = item.find('p').text if item.find('p') else 'No Description'
            image_url = item.find('img')['src'] if item.find('img') else None
            video_url = item.find('video') if item.find('video') else None
            link = item.find('a')['href'] if item.find('a') else 'No Link'

            # تحميل الصورة والفيديو إذا كانا موجودين
            image_path = None
            if image_url:
                image_path = download_file(image_url, os.path.join(settings.MEDIA_ROOT, 'darkweb_images'))

            video_path = None
            if video_url:
                video_path = download_file(video_url, os.path.join(settings.MEDIA_ROOT, 'darkweb_videos'))

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
    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return []


# جمع النتائج بشكل متوازي
def scrape_darkweb_parallel(query):
    if not check_tor_connection():
        return []

    session = get_tor_session()
    base_url = f"http://exampledarkweb.onion/search?q={quote(query)}"

    results = []
    page_number = 1  # بدءًا من الصفحة 1

    while True:
        # إعداد الرابط للبحث في الصفحة الحالية
        url = f"{base_url}&page={page_number}"
        print(f"Scraping page {page_number}...")

        # استخراج البيانات من الصفحة
        page_results = scrape_page(url, session)

        if not page_results:
            break  # إذا لم توجد نتائج، نوقف البحث (أي لا يوجد المزيد من الصفحات)

        results.extend(page_results)  # إضافة النتائج إلى القائمة العامة

        page_number += 1  # الانتقال إلى الصفحة التالية

    return results



# البحث في الدارك ويب وحفظ البيانات في قاعدة البيانات
def search_darkweb(query):
    raw_results = scrape_darkweb_parallel(query)

    for raw in raw_results:
        image_file = None
        if raw['image']:
            with open(raw['image'], 'rb') as img_file:
                image_file = File(img_file)

        video_file = None
        if raw['video']:
            with open(raw['video'], 'rb') as vid_file:
                video_file = File(vid_file)

        # حفظ البيانات في قاعدة البيانات
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

    return raw_results
