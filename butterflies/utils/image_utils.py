import os
from django.conf import settings


import requests

def get_specimen_image_urls(catalog_number):
    """
    Returns URLs for dorsal and ventral images for a specimen, if they exist in the Azure container.
    If not accessible, returns 'no data' for that image.
    """
    BASE_URL = getattr(settings, 'LEPIDOPTERA_ADULTS_IMAGES_URL', 'https://asadatabasestorage.blob.core.windows.net/lepidoptera-adults-images/')
    SAS_TOKEN = os.environ.get('AZURE_BLOB_SAS_TOKEN', '')
    suffix = f"?{SAS_TOKEN}" if SAS_TOKEN else ""
    dorsal_url = f"{BASE_URL}{catalog_number}_dorsal.jpg{suffix}"
    ventral_url = f"{BASE_URL}{catalog_number}_ventral.jpg{suffix}"
    print(f"[DEBUG] Specimen image URLs for {catalog_number}:")
    print(f"  Dorsal:  {dorsal_url}")
    print(f"  Ventral: {ventral_url}")

    def url_exists(url):
        try:
            response = requests.head(url, timeout=3)
            return response.status_code == 200
        except Exception as e:
            print(f"[DEBUG] Error checking {url}: {e}")
            return False

    dorsal = dorsal_url if url_exists(dorsal_url) else "no data"
    ventral = ventral_url if url_exists(ventral_url) else "no data"
    return {'dorsal': dorsal, 'ventral': ventral}
