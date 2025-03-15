import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from .models import ExtractedData


def get_tor_session():
    session = requests.Session()
    session.proxies = {'http': 'socks5h://192.168.190.128:9050',
                       'https': 'socks5h://192.168.190.128:9050'}
    return session

def check_tor_connection():
    try:
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
            image = item.find('img')['src'] if item.find('img') else None
            video = item.find('video') if item.find('video') else None
            link = item.find('a')['href'] if item.find('a') else 'No Link'

            results.append({
                'title_1': title_1,
                'title_2': title_2,
                'title_3': title_3,
                'description': description,
                'image': image,
                'video': video,
                'url': link
            })

        return results
    except requests.RequestException as e:
        print(f"❌ Error scraping {url}: {e}")
        return []


def scrape_darkweb_parallel(query):
    if not check_tor_connection():
        return []

    session = get_tor_session()
    base_url = f"http://exampledarkweb.onion/search?q={quote(query)}"

    # Prepare list of URLs to scrape (simulating paginated results here)
    urls = [f"{base_url}&page={i}" for i in range(1, 6)]  # 5 صفحات مثلاً

    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(scrape_page, url, session): url for url in urls}

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                results.extend(result)  # تجميع النتائج
            except Exception as e:
                print(f"❌ Error processing {url}: {e}")
    
    return results


def search_darkweb(query):
    raw_results = scrape_darkweb_parallel(query)
    
    for raw in raw_results:
        extracted_data = ExtractedData(
            title_1=raw['title_1'],
            title_2=raw['title_2'],
            title_3=raw['title_3'],
            description=raw['description'],
            image=raw['image'],
            video=raw['video'],
            url=raw['url'],
            query=query
        )
        extracted_data.save()  

    return raw_results
