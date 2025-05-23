import httpx, asyncio, re, os, time, random
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from httpx import AsyncClient
from httpx_socks import AsyncProxyTransport
from colorama import Fore
from datetime import datetime
from dateutil.parser import parse  # استيراد dateutil.parser

# قائمة User-Agents للتدوير
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
]

# إعدادات العميل مع وكيل Tor
tor_proxy = "socks5://192.168.100.150:9050"
transport = AsyncProxyTransport.from_url(tor_proxy)
client = AsyncClient(
    transport=transport,
    headers={'User-Agent': random.choice(user_agents)},
    timeout=httpx.Timeout(60.0, connect=20.0),
    follow_redirects=True
)

image_counter = 1

def sanitize_folder_name(name):
    return re.sub(r'[\\/*?:"<>|]', '_', name)

async def download_image(img_url, clean_query, img_number):
    try:
        ext = os.path.splitext(img_url)[1].lower()
        if not ext or ext not in ['.jpg', '.jpeg', '.png']:
            ext = '.jpg'

        filename = f"{clean_query}_{img_number}{ext}"
        filepath = os.path.join("media", f"DarkWeb_{clean_query}", filename).replace('\\', '/')
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        async with AsyncClient(
            transport=transport,
            headers={'User-Agent': random.choice(user_agents)},
            timeout=httpx.Timeout(10.0, connect=5.0),
            follow_redirects=True
        ) as img_client:
            response = await img_client.get(img_url, timeout=5)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                f.write(response.content)

        return filepath
    except Exception as e:
        print(Fore.YELLOW + f"[!] Error downloading image {img_url}\n[-] Type: {type(e).__name__}\n[-] Message: {str(e)}")
        return None

async def search_darkweb(query):
    start_time = time.time()
    global image_counter
    clean_query = sanitize_folder_name(query)
    results = []
    base_url = f"http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/?q={query}"
    try:
        response = await client.get(base_url)
        response.raise_for_status()
        print(Fore.GREEN + "[+] The Data Scraper Process From Dark Web Has Begun ...")
    except Exception as e:
        print(Fore.RED + f"[!] Failed to Connect to Dark web Search Engine: {type(e).__name__}: {str(e)}")
        return [{'error': f"Failed to Connect to Dark web Search Engine: {type(e).__name__}"}]

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)

    blacklisted_domains = ['ahmia', 'search/?q=', base_url]
    max_successful = 15
    max_errors = 10
    successful_attempts = 0
    error_count = 0

    for link in links:
        if successful_attempts >= max_successful or error_count >= max_errors:
            print(Fore.YELLOW + f"[!] Stopping Search Due to {error_count} Errors.")
            break

        url = urljoin(base_url, link['href'])
        if any(domain in url for domain in blacklisted_domains):
            continue

        try:
            page_response = await client.get(url, timeout=10)
            page_response.raise_for_status()

            if query.lower() not in page_response.text.lower():
                continue

            page_soup = BeautifulSoup(page_response.text, 'html.parser')

            description_tag = page_soup.find('meta', attrs={'name': 'description'})
            description = description_tag['content'] if description_tag and 'content' in description_tag.attrs else "No description found"

            h1 = page_soup.find('h1').text.strip() if page_soup.find('h1') else "Not Found "
            h2 = page_soup.find('h2').text.strip() if page_soup.find('h2') else "Not Found "
            h3 = page_soup.find('h3').text.strip() if page_soup.find('h3') else "Not Found "

            image_urls = []
            for img in page_soup.find_all('img', src=True):
                src = img['src']
                if src.startswith('http') and any(src.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                    full_url = urljoin(url, src)
                    image_urls.append(full_url)
                if len(image_urls) >= 2:
                    break

            os.makedirs(f"media/DarkWeb_{clean_query}", exist_ok=True)

            loop = asyncio.get_running_loop()
            download_tasks = [
                loop.create_task(download_image(img_url, clean_query, image_counter + idx))
                for idx, img_url in enumerate(image_urls)
            ]
            downloaded = await asyncio.gather(*download_tasks)
            image_paths = list(filter(None, downloaded))
            image_counter += len(downloaded)

            emails = list(set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', page_soup.text)))

            # استخراج النص الكامل من الصفحة
            text_content = page_soup.get_text(separator=' ', strip=True)

            # استخراج تاريخ النشر بدون استخدام normalize_publish_date
            publish_date = None
            date_meta = page_soup.find('meta', attrs={'name': 'pubdate'}) \
                or page_soup.find('meta', attrs={'property': 'article:published_time'}) \
                or page_soup.find('meta', attrs={'name': 'date'}) \
                or page_soup.find('meta', attrs={'itemprop': 'datePublished'})

            date_str = None
            if date_meta and 'content' in date_meta.attrs:
                date_str = date_meta['content']
            else:
                # البحث عن تاريخ منطقي في النص
                date_patterns = [
                    r"\b(20\d{2}[-/.\s]\d{1,2}[-/.\s]\d{1,2})\b",
                    r"\b(\d{1,2}[-/.\s]\d{1,2}[-/.\s]20\d{2})\b"
                ]
                for pattern in date_patterns:
                    match = re.search(pattern, page_soup.text)
                    if match:
                        date_str = match.group(1)
                        break

            if date_str:
                try:
                    dt = parse(date_str, fuzzy=True)
                    publish_date = dt.strftime("%Y-%m-%d ")
                except Exception:
                    publish_date = "Not Found"
            else:
                publish_date = "Not Found"

            results.append({
                'url': url,
                'description': description,
                'h1': h1,
                'h2': h2,
                'h3': h3,
                'images': image_paths,
                'emails': emails,
                'full_text': text_content,
                'publish_date': publish_date
            })
            print(Fore.GREEN + f"[+] Attempt Number {successful_attempts+1} Success.")
            successful_attempts += 1

        except Exception as e:
            error_count += 1
            print(Fore.RED + f"[!] Error fetching {url}\n[-] Type: {type(e).__name__}\n[-] Message: {str(e)}")
            continue

        await asyncio.sleep(random.uniform(1.0, 3.0))

    if not results:
        return [{'error': 'No results found'}]

    print(Fore.GREEN + "[+] The Data Scraper Process From Dark Web is Done.")
    end_time = time.time()
    total_seconds = int(end_time - start_time)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    print(Fore.BLUE + f"[+] Total Time Elapsed: {minutes} Minutes, {seconds} Seconds.")

    return results
