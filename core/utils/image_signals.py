"""
Django Signals for Automatic WebP Image Optimization

This module automatically converts all uploaded images to WebP format
when they are saved to any model in the application.

Usage:
    Signals are automatically registered when the app is ready.
    No additional configuration needed beyond importing this module in apps.py
"""

import logging
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models import ImageField
from core.utils.image_optimizer import convert_image_to_webp

logger = logging.getLogger(__name__)


def get_image_fields(model):
    """
    Get all ImageField instances from a Django model.
    
    Args:
        model: Django model class
        
    Returns:
        list: List of ImageField field names
    """
    return [f.name for f in model._meta.get_fields() if isinstance(f, ImageField)]


@receiver(pre_save, dispatch_uid='webp_image_optimization')
def optimize_images_pre_save(sender, instance, **kwargs):
    """
    Signal handler to automatically convert all image fields to WebP format.
    
    This signal is triggered BEFORE any model is saved to the database.
    It:
    1. Detects all ImageField instances in the model
    2. Checks if the image file was changed
    3. Converts the image to WebP format
    4. Updates the field with the optimized WebP image
    
    Supported Models:
    - SiteSettings (logo, favicon)
    - HomePage_Image (image)
    - HomePage_Sliding_Image (image1, image2)
    - HomePage_Category_Section (image1, image2)
    - HomePage_Category_Side_Section (image)
    - HomePage_Category_Bottom_Section (image1, image2)
    - HomePage_Posts_Main (image)
    - HomePage_Posts_Side (image)
    - HomePage_Posts_Bottom_Section (image)
    - About_us_top_section (image)
    - About_us_team (image)
    - blog_top_image (image, image_profile)
    - tab_three_post (image)
    
    Args:
        sender: Model class being saved
        instance: Instance of the model
        **kwargs: Additional signal arguments
    """
    try:
        # Get all ImageField names from the model
        image_fields = get_image_fields(sender)
        
        if not image_fields:
            return  # No image fields in this model
        
        model_name = sender.__name__
        optimized_count = 0
        
        # Process each image field
        for field_name in image_fields:
            image_field = getattr(instance, field_name, None)
            
            if not image_field:
                continue
            
            # Check if this is a new file or if the file was changed.
            # If the old image and current image share the same name but the field
            # has a freshly uploaded file, convert again.
            try:
                original_instance = sender.objects.get(pk=instance.pk)
                original_image = getattr(original_instance, field_name, None)
                is_same_file_name = original_image and original_image.name == image_field.name
                is_committed = getattr(image_field, '_committed', True)

                if is_same_file_name and is_committed:
                    continue
                    
            except sender.DoesNotExist:
                # This is a new instance, not in database yet
                pass
            
            # Perform WebP conversion
            if hasattr(image_field, 'name') and image_field.name:
                logger.debug(f"Processing {model_name}.{field_name}: {image_field.name}")
                
                content_file, webp_filename = convert_image_to_webp(
                    image_field,
                    image_field.name
                )
                
                if content_file:
                    # Replace the image field with optimized WebP version
                    setattr(instance, field_name, content_file)
                    optimized_count += 1
                    logger.info(
                        f"Image optimized: {model_name}.{field_name} "
                        f"-> {webp_filename}"
                    )
                else:
                    logger.warning(
                        f"Failed to optimize {model_name}.{field_name}, "
                        f"keeping original"
                    )
        
        if optimized_count > 0:
            logger.info(
                f"Image optimization complete for {model_name}: "
                f"{optimized_count} image(s) converted to WebP"
            )
            
    except Exception as e:
        logger.error(
            f"Error in image optimization signal for {sender.__name__}: {str(e)}",
            exc_info=True
        )
        # Don't prevent model from saving on optimization errors
        pass


def connect_signals():
    """
    Explicitly connect image optimization signals.
    
    This function is called in the app's ready() method to ensure
    signals are properly registered before any models are saved.
    """
    logger.info("Image optimization signals connected")
