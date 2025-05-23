from django.shortcuts import render
import redis
import json
import re
import asyncio
from .dark_web_scraper import search_darkweb
from colorama import Fore

# Clean the query from unwanted characters and noise
def clean_query(query):
    query = query.strip()
    query = re.sub(r'[\\/*?:"<>|]', ' ', query)  # Remove illegal characters
    query = re.sub(r'\s+', ' ', query)  # Remove extra spaces
    return query

# View
def view_DarkWeb(request):
    query = request.GET.get('query', '')
    if not query:
        return render(request, 'pages/HomePage.html')

    query = clean_query(query)

    if len(query) < 3:
        return render(request, 'pages/HomePage.html', {'error': 'Search query is too short or invalid.'})

    # Initialize Redis only after valid query
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
    except redis.exceptions.ConnectionError:
        print(Fore.RED + "[!] Failed to connect to Redis database.")
        return render(request, 'pages/HomePage.html', {
            'error': 'Failed to connect to the Redis database. Please try again later.',
            'query': query
        })

    key = f"Dark Web: {query}"

    try:
        cached_data = r.get(key)
    except Exception as e:
        return render(request, 'pages/HomePage.html', {
            'error': f"Failed to access cache: {str(e)}", 'query': query
        })

    if cached_data:
        try:
            results = json.loads(cached_data)
            print(Fore.GREEN + "[+] Data found in cache.")
            return render(request, 'pages/HomePage.html', {'results': results, 'query': query})
        except json.JSONDecodeError:
            return render(request, 'pages/HomePage.html', {
                'error': 'Error decoding data from cache.', 'query': query
            })

    # Run async search_darkweb safely using event loop
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(search_darkweb(query))
        loop.close()
    except Exception as e:
        print(Fore.RED + f"[!] Failed to Connect to Dark web Search Engine: {str(e)}")
        return render(request, 'pages/HomePage.html', {
            'error': f"An error occurred during search: {str(e)}", 'query': query
        })

    if isinstance(results, list) and results and 'error' not in results[0]:
        try:
            r.setex(key, 86400, json.dumps(results))
        except Exception as e:
            return render(request, 'pages/HomePage.html', {
                'error': f"Failed to store data in cache: {str(e)}", 'query': query
            })
    else:
        return render(request, 'pages/HomePage.html', {
            'error': results[0].get('error', 'Unknown error'), 'query': query
        })

    return render(request, 'pages/HomePage.html', {'results': results, 'query': query})
