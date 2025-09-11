from django.contrib import admin
from .models import (HomePage_Image, 
                     HomePage_Sliding_Image, 
                     HomePage_Category_Section,
                     HomePage_Category_Side_Section,
                     HomePage_Category_Bottom_Section,
                     HomePage_Posts_Main,
                     HomePage_Posts_Side,
                     HomePage_Posts_Bottom_Section,
                    )


# Register your models here.
admin.site.register(HomePage_Image)
admin.site.register(HomePage_Sliding_Image)
admin.site.register(HomePage_Category_Section)
admin.site.register(HomePage_Category_Side_Section)
admin.site.register(HomePage_Category_Bottom_Section)
admin.site.register(HomePage_Posts_Main)
admin.site.register(HomePage_Posts_Side)
admin.site.register(HomePage_Posts_Bottom_Section)
