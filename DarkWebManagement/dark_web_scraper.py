import requests
from bs4 import BeautifulSoup
from urllib.parse import quote


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

def scrape_darkweb(query):
    if not check_tor_connection():
        return []

    session = get_tor_session()
    url = f"http://exampledarkweb.onion/search?q={quote(query)}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for item in soup.find_all('div', class_='result'):
            title = item.find('h2').text if item.find('h2') else 'No Title'
            description = item.find('p').text if item.find('p') else 'No Description'
            image = item.find('img')['src'] if item.find('img') else None
            video = item.find('video') if item.find('video') else None
            results.append({
                'title': title,
                'description': description,
                'image': image,
                'video': video
            })
        return results
    except requests.RequestException as e:
        print(f"❌ Error scraping {url}: {e}")
        return []

def search_darkweb(query):
    raw_results = scrape_darkweb(query)
    return raw_results
