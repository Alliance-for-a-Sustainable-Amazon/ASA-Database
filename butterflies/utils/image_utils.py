import os
from django.conf import settings


import requests

def get_specimen_image_urls(catalog_number):
    """
    Returns URLs for dorsal and ventral images for a specimen, if they exist in the Azure container.
    If not accessible, returns 'no data' for that image.
    """
    BASE_URL = getattr(settings, 'LEPIDOPTERA_ADULTS_IMAGES_URL', 'https://asadatabasestorage.blob.core.windows.net/lepidoptera-adults-images/')
    # Convert hyphens to underscores for image filename format
    image_filename_base = catalog_number.replace('-', '_')
    
    # Possible file extensions to check
    extensions = ['jpg', 'JPG', 'jpeg', 'JPEG']
    
    def url_exists(url):
        try:
            response = requests.head(url, timeout=3)
            return response.status_code == 200
        except Exception as e:
            print(f"[DEBUG] Error checking {url}: {e}")
            return False
    
    def find_image_url(image_type):
        """Find the correct URL with the right extension for the given image type (d or v)"""
        for ext in extensions:
            url = f"{BASE_URL}{image_filename_base}_{image_type}.{ext}"
            if url_exists(url):
                print(f"[DEBUG] Found {image_type} image: {url}")
                return url
        print(f"[DEBUG] No {image_type} image found for {catalog_number}")
        return "no data"
    
    dorsal = find_image_url('d')
    ventral = find_image_url('v')
    
    print(f"[DEBUG] Final specimen image URLs for {catalog_number}:")
    print(f"  Dorsal:  {dorsal}")
    print(f"  Ventral: {ventral}")
    
    return {'dorsal': dorsal, 'ventral': ventral}
