"""
WebP Image Optimization Utility

This module handles automatic conversion of all image formats to WebP.
Supports: JPG, JPEG, PNG, GIF, BMP, TIFF, AVIF, HEIC

Key Features:
- Automatic conversion of uploaded images to WebP format
- Preserves image quality while reducing file size
- Handles corrupted or unsupported files gracefully
- Supports both single images and multiple images
- Efficient compression with fallback options
- Comprehensive error logging and handling
"""

import os
import logging
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings

logger = logging.getLogger(__name__)

# Supported image formats for conversion
SUPPORTED_FORMATS = {
    'JPEG', 'JPG', 'PNG', 'GIF', 'BMP', 'TIFF', 'AVIF', 'HEIC', 'WEBP'
}

# Default WebP settings when Django settings are unavailable
DEFAULT_WEBP_QUALITY = 85
DEFAULT_WEBP_METHOD = 6


def is_image_file(filename):
    """
    Check if a file is a supported image format.
    
    Args:
        filename (str): The filename to check
        
    Returns:
        bool: True if the file is a supported image format
    """
    if not filename:
        return False
    
    ext = os.path.splitext(filename)[1].lstrip('.').upper()
    return ext in SUPPORTED_FORMATS


def get_webp_filename(original_filename):
    """
    Convert filename to WebP format.
    
    Args:
        original_filename (str): Original filename (e.g., 'photo.jpg')
        
    Returns:
        str: WebP filename (e.g., 'photo.webp')
    """
    if not original_filename:
        return 'image.webp'
    
    name, _ = os.path.splitext(original_filename)
    # Remove any invalid characters
    name = name.replace(' ', '_')
    return f"{name}.webp"


def convert_image_to_webp(image_file, filename=None):
    """
    Convert an image file to WebP format.
    
    This function:
    1. Opens the image file
    2. Converts it to RGB if necessary (handles RGBA, L, etc.)
    3. Saves it as WebP with optimized settings
    4. Returns a ContentFile with the WebP data
    
    Args:
        image_file: Django UploadedFile or file-like object
        filename (str, optional): Original filename. If not provided, uses image_file.name
        
    Returns:
        tuple: (ContentFile, webp_filename) or (None, None) on error
    """
    try:
        if not image_file:
            logger.warning("Image optimization: No image file provided")
            return None, None
        
        filename = filename or getattr(image_file, 'name', 'image.webp')
        
        # Check if already WebP
        if filename.lower().endswith('.webp'):
            logger.debug(f"Image already in WebP format: {filename}")
            return image_file, filename
        
        # Check if supported format
        if not is_image_file(filename):
            logger.warning(f"Unsupported image format: {filename}")
            return None, None
        
        # Reset file pointer if it's a file-like object
        if hasattr(image_file, 'seek'):
            image_file.seek(0)
        
        # Open image
        img = Image.open(image_file)
        
        # Log original format and size
        original_format = img.format
        original_size = image_file.size if hasattr(image_file, 'size') else len(image_file.read())
        logger.info(f"Converting image: {filename} ({original_format}, {original_size} bytes)")
        
        # Convert RGBA to RGB (WebP handles both, but RGB is more compatible)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode not in ('RGB', 'L'):
            # Convert any other mode to RGB
            img = img.convert('RGB')
        
        # Optimize image dimensions (optional: limit max size)
        max_width = getattr(settings, 'MAX_IMAGE_WIDTH', 4000)
        max_height = getattr(settings, 'MAX_IMAGE_HEIGHT', 4000)
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            logger.info(f"Image resized to: {img.width}x{img.height}")
        
        # Save as WebP
        webp_filename = get_webp_filename(filename)
        webp_buffer = BytesIO()
        webp_quality = getattr(settings, 'WEBP_QUALITY', DEFAULT_WEBP_QUALITY)
        webp_method = getattr(settings, 'WEBP_METHOD', DEFAULT_WEBP_METHOD)
        
        img.save(
            webp_buffer,
            format='WEBP',
            quality=webp_quality,
            method=webp_method,
            optimize=True
        )
        
        webp_buffer.seek(0)
        webp_size = webp_buffer.getbuffer().nbytes
        compression_ratio = (1 - webp_size / max(original_size, 1)) * 100
        
        logger.info(
            f"WebP conversion successful: {filename} -> {webp_filename} "
            f"({original_size} -> {webp_size} bytes, {compression_ratio:.1f}% reduction)"
        )
        
        # Create ContentFile with WebP data
        content_file = ContentFile(webp_buffer.getvalue(), name=webp_filename)
        return content_file, webp_filename
        
    except Image.UnidentifiedImageError as e:
        logger.error(f"Cannot identify image format: {filename} - {str(e)}")
        return None, None
    except IOError as e:
        logger.error(f"IO error while processing image {filename}: {str(e)}")
        return None, None
    except Exception as e:
        logger.error(f"Unexpected error converting image {filename}: {str(e)}", exc_info=True)
        return None, None


def optimize_multiple_images(image_dict):
    """
    Convert multiple image fields in a dictionary to WebP.
    
    Usage in signals:
        images = {
            'image1': uploaded_file_1,
            'image2': uploaded_file_2,
        }
        optimized = optimize_multiple_images(images)
        
    Args:
        image_dict (dict): Dictionary of field_name: image_file pairs
        
    Returns:
        dict: Dictionary of field_name: (ContentFile, filename) pairs
    """
    results = {}
    for field_name, image_file in image_dict.items():
        if image_file:
            content_file, webp_filename = convert_image_to_webp(image_file)
            if content_file:
                results[field_name] = (content_file, webp_filename)
            else:
                logger.warning(f"Failed to optimize {field_name}, keeping original")
                results[field_name] = (image_file, getattr(image_file, 'name', 'image'))
        else:
            results[field_name] = (None, None)
    
    return results


def optimize_model_image_field(instance, field_name):
    """
    Convert an ImageField on a model instance to WebP and save the model.

    Args:
        instance: Django model instance
        field_name (str): Name of the ImageField

    Returns:
        bool: True if conversion succeeded, False otherwise
    """
    image_field = getattr(instance, field_name, None)
    if not image_field or not getattr(image_field, 'name', None):
        return False

    if image_field.name.lower().endswith('.webp'):
        return False

    try:
        if hasattr(image_field, 'open'):
            image_field.open('rb')
        
        content_file, webp_filename = convert_image_to_webp(
            image_field,
            image_field.name
        )
        
        if not content_file:
            return False

        old_name = image_field.name
        image_field.save(webp_filename, content_file, save=False)
        instance.save(update_fields=[field_name])

        logger.info(
            f"Existing model image field converted: {instance.__class__.__name__}."
            f"{field_name} ({old_name} -> {webp_filename})"
        )
        return True

    except Exception as exc:
        logger.error(
            f"Failed to convert model image field {instance.__class__.__name__}.{field_name}: {exc}",
            exc_info=True
        )
        return False


def get_image_url(image_field):
    """
    Get the URL for an image field, ensuring WebP format.
    
    Args:
        image_field: Django ImageField instance
        
    Returns:
        str: URL to the WebP image or empty string if no image
    """
    if not image_field or not image_field.name:
        return ''
    
    return image_field.url


def get_fallback_image_url(image_field):
    """
    Get fallback image URL for browsers that don't support WebP.
    
    Note: Since we convert all images to WebP at upload, there is no fallback.
    This function is kept for compatibility with potential future changes.
    
    Args:
        image_field: Django ImageField instance
        
    Returns:
        str: URL to the image (same as get_image_url in WebP-only setup)
    """
    return get_image_url(image_field)


# Statistics and monitoring
class ImageOptimizationStats:
    """Helper class for tracking image optimization statistics."""
    
    @staticmethod
    def get_stats():
        """
        Get image optimization statistics from log files.
        
        Returns:
            dict: Statistics about converted images
        """
        # This would typically query a database table or parse logs
        # For now, returns a template for future implementation
        return {
            'total_conversions': 0,
            'total_bytes_saved': 0,
            'failed_conversions': 0,
            'average_compression': 0,
        }
    
    @staticmethod
    def log_conversion(original_size, webp_size, filename):
        """
        Log a successful conversion for statistics.
        
        Args:
            original_size (int): Original file size in bytes
            webp_size (int): WebP file size in bytes
            filename (str): Image filename
        """
        bytes_saved = original_size - webp_size
        logger.info(
            f"CONVERSION_STATS: {filename} | "
            f"Original: {original_size} bytes | "
            f"WebP: {webp_size} bytes | "
            f"Saved: {bytes_saved} bytes"
        )
