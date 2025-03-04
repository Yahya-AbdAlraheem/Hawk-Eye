import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

# إعداد جلسة Tor
def get_tor_session():
    session = requests.Session()
    session.proxies = {'http': 'socks5h://192.168.190.128:9050',
                       'https': 'socks5h://192.168.190.128:9050'}
    return session

# فحص الاتصال بـ Tor
def check_tor_connection():
    try:
        # محاولة الوصول إلى موقع معروف لفحص اتصال Tor
        response = requests.get('http://check.torproject.org', proxies={'http': 'socks5h://192.168.190.128:9050', 'https': 'socks5h://192.168.190.128:9050'}, timeout=10)
        if "Congratulations. This browser is configured to use Tor." in response.text:
            print("✅ Tor connection is successful!")
            return True
        else:
            print("❌ Tor connection failed!")
            return False
    except requests.RequestException as e:
        print(f"❌ Failed to connect to Tor: {e}")
        return False

# البحث في مواقع الدارك ويب
def search_darkweb(session, query, url):
    try:
        response = session.get(url + quote(query), timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "Title not available"
        print(f"🔎 Search result from {url}: {title}")
    except requests.RequestException as e:
        print(f"❌ Error accessing {url}: {e}")

# تنفيذ البحث باستخدام `ThreadPoolExecutor`
def search_using_threads(queries, urls):
    # التأكد من أن Tor متصل
    if not check_tor_connection():
        print("❌ Cannot proceed with search without a working Tor connection.")
        return

    session = get_tor_session()
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(search_darkweb, session, query, url) for query in queries for url in urls]
        for future in futures:
            future.result()

# الاستعلامات والروابط
queries = ['bitcoin', 'cybersecurity', 'darkweb marketplaces']
urls = [
    'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/',
    'http://haystak5njsmn2hqkewecpaxetahtwhsbsa64jom2k22z5afxhnpxfid.onion/',
    'http://xmh57jrknzkhv6y3ls3ubitzfqnkrwxhopf5aygthi7d6rplyvk3noyd.onion/',
    'http://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion/'
]

# تشغيل البحث
search_using_threads(queries, urls)
