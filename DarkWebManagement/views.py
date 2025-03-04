from django.shortcuts import render
from django.http import JsonResponse
from .models import ExtractedData
from .AES import encrypt, decrypt
import subprocess
import json
import os
import shutil
import requests
from django.conf import settings

def save_media_files(media_list, media_type):
    """Helper function to save images and videos to the correct media folder"""
    media_dir = os.path.join(settings.MEDIA_ROOT, f'darkweb_{media_type}')
    os.makedirs(media_dir, exist_ok=True)
    stored_files = []
    
    for media_url in media_list:
        filename = os.path.basename(media_url)
        file_path = os.path.join(media_dir, filename)
        
        try:
            response = requests.get(media_url, stream=True, timeout=10)
            response.raise_for_status()
            
            with open(file_path, 'wb') as file:
                shutil.copyfileobj(response.raw, file)
                stored_files.append(f'darkweb_{media_type}/{filename}')
        except Exception as e:
            print(f"Error saving {media_type}: {e}")
    
    return stored_files

def search_darkweb(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        
        if not query:
            return JsonResponse({'error': 'Search query is required'}, status=400)
        
        try:
            result = subprocess.run(['python3', 'dark_web_scraper.py', query], capture_output=True, text=True)
            scraped_data = json.loads(result.stdout)  # يفترض أن يكون الناتج JSON
        except Exception as e:
            return JsonResponse({'error': f'Failed to run scraper: {str(e)}'}, status=500)
        
        for entry in scraped_data:
            encrypted_title = encrypt(entry['title'])
            encrypted_description = encrypt(entry['description'])
            encrypted_url = encrypt(entry['url'])
            
            images = save_media_files(entry.get('images', []), 'images')
            videos = save_media_files(entry.get('videos', []), 'videos')
            
            ExtractedData.objects.create(
                query=query,
                title=encrypted_title,
                description=encrypted_description,
                url=encrypted_url,
                headings=json.dumps(entry.get('headings', [])),
                links=json.dumps(entry.get('links', [])),
                images=json.dumps(images),
                videos=json.dumps(videos)
            )
        
        return JsonResponse({'message': 'Search completed and data stored successfully'})
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_results(request):
    query = request.GET.get('query')
    if not query:
        return JsonResponse({'error': 'Query parameter is required'}, status=400)
    
    results = ExtractedData.objects.filter(query=query)
    
    decrypted_results = []
    for result in results:
        decrypted_results.append({
            'title': decrypt(result.title),
            'description': decrypt(result.description),
            'url': decrypt(result.url),
            'headings': json.loads(result.headings),
            'links': json.loads(result.links),
            'images': json.loads(result.images),
            'videos': json.loads(result.videos)
        })
    
    return JsonResponse({'results': decrypted_results})
