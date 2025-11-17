import os
from django.conf import settings
import requests
from django.core.cache import cache
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import hashlib

logger = logging.getLogger(__name__)

# Thread-local session for better performance
_thread_local = threading.local()

def get_session():
    """Get a thread-local requests session for better performance"""
    if not hasattr(_thread_local, 'session'):
        _thread_local.session = requests.Session()
        _thread_local.session.headers.update({'User-Agent': 'ASA-Database/1.0'})
        # Add connection pooling for better performance
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=1
        )
        _thread_local.session.mount('http://', adapter)
        _thread_local.session.mount('https://', adapter)
    return _thread_local.session

def check_image_url_fast(url):
    """Fast image URL checking with optimized requests and aggressive caching"""
    # Create a cache key for individual URL checks (even more granular caching)
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    url_cache_key = f"img_check_{url_hash}"
    
    # Check if we've already verified this specific URL
    cached_url_result = cache.get(url_cache_key)
    if cached_url_result is not None:
        return url if cached_url_result else None
    
    try:
        session = get_session()
        # Reduce timeout to 2 seconds - fail fast if blob storage is slow
        response = session.head(url, timeout=2.0)
        exists = response.status_code == 200
        
        # Cache individual URL results for 4 hours
        cache.set(url_cache_key, exists, 14400)
        
        return url if exists else None
    except Exception:
        # Cache negative results for 1 hour to avoid repeated failed checks
        cache.set(url_cache_key, False, 3600)
        return None

def get_specimen_image_urls(catalog_number):
    """
    Returns URLs for dorsal and ventral images for a specimen, if they exist in the Azure container.
    Returns dictionary format for backward compatibility: {'dorsal': url, 'ventral': url}
    Uses aggressive caching and optimized checking to improve performance.
    """
    # Check cache first to avoid repeated HTTP requests
    cache_key = f"specimen_images_{catalog_number}"
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    BASE_URL = getattr(settings, 'LEPIDOPTERA_ADULTS_IMAGES_URL', 'https://asadatabasestorage.blob.core.windows.net/lepidoptera-adults-images/')
    # Convert hyphens to underscores for image filename format
    image_filename_base = catalog_number.replace('-', '_')
    
    # Possible file extensions to check
    extensions = ['jpg', 'JPG', 'jpeg', 'JPEG']
    
    # Generate all possible URLs
    possible_urls = []
    for image_type in ['d', 'v']:  # dorsal, ventral
        for ext in extensions:
            url = f"{BASE_URL}{image_filename_base}_{image_type}.{ext}"
            possible_urls.append((url, image_type))
    
    # Check URLs concurrently for better performance
    found_urls = {'dorsal': 'no data', 'ventral': 'no data'}
    try:
        # Use ThreadPoolExecutor for concurrent checking
        with ThreadPoolExecutor(max_workers=4, thread_name_prefix='image_check') as executor:
            # Submit all URL checks
            future_to_url = {executor.submit(check_image_url_fast, url): (url, image_type) for url, image_type in possible_urls}
            
            # Collect results as they complete
            for future in as_completed(future_to_url, timeout=60):
                result = future.result()
                if result:
                    url, image_type = future_to_url[future]
                    if image_type == 'd':
                        found_urls['dorsal'] = result
                    elif image_type == 'v':
                        found_urls['ventral'] = result
    except Exception as e:
        logger.warning(f"Error checking images for {catalog_number}: {e}")
    
    # Cache the result for 2 hours to avoid repeated requests
    cache.set(cache_key, found_urls, 7200)
    
    return found_urls

def get_specimen_image_urls_batch(catalog_numbers):
    """
    Batch process multiple specimen image URLs for better performance.
    Returns dictionary format for each catalog number.
    """
    results = {}
    
    # Check cache first for all catalog numbers
    uncached_numbers = []
    for catalog_number in catalog_numbers:
        cache_key = f"specimen_images_{catalog_number}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            results[catalog_number] = cached_result
        else:
            uncached_numbers.append(catalog_number)
    
    if uncached_numbers:
        try:
            with ThreadPoolExecutor(max_workers=6, thread_name_prefix='batch_image_check') as executor:
                future_to_catalog = {
                    executor.submit(get_specimen_image_urls, catalog_number): catalog_number 
                    for catalog_number in uncached_numbers
                }
                
                # Process all futures
                for future in as_completed(future_to_catalog):
                    catalog_number = future_to_catalog[future]
                    try:
                        result = future.result()
                        results[catalog_number] = result
                    except Exception as e:
                        logger.warning(f"Error getting images for {catalog_number}: {e}")
                        results[catalog_number] = {'dorsal': 'no data', 'ventral': 'no data'}
        except Exception as e:
            logger.error(f"Error in batch image processing: {e}")
            # Fallback to empty results for failed ones
            for catalog_number in uncached_numbers:
                if catalog_number not in results:
                    results[catalog_number] = {'dorsal': 'no data', 'ventral': 'no data'}
    
    return results
