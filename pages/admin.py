from django.contrib import admin
from admin_interface.models import Theme
from .models import (HomePage_Image,
                     HomePage_Sliding_Image,
                     HomePage_Category_Section,
                     HomePage_Category_Side_Section,
                     HomePage_Category_Bottom_Section,
                     HomePage_Posts_Main,
                     HomePage_Posts_Side,
                     HomePage_Posts_Bottom_Section,
                     About_us_title,
                     About_us_team,
                     About_us_team_title,
                     About_us_top_section,
                     blog_top_image,
                     Article_tab,
                     tab_one,
                     tab_three,
                     tab_three_post,
                     tab_four,
                     tab_five,
                     tab_five_post,
                     tab_six,
                     tab_seven,
                     tab_eight,
                     tab_nine,
                     ContactMessage,
                    )


# Unregister the default theme to simplify the admin interface
admin.site.unregister(Theme)

# Define custom ordering and grouping for the admin interface
admin.site.order = (
    ("pages", ("Homepage", "About Us", "Blog & Articles")),
)

admin.site.apps_order = admin.site.order

admin.site.app_config = {
    "pages": {"icon": "fas fa-file-alt"}
}

# Register your models here.

# --- Homepage Models ---

@admin.register(HomePage_Image)
class HomePage_ImageAdmin(admin.ModelAdmin):
    list_display = ('large_title', 'event_date', 'aprove')
    list_display_links = ('large_title',)
    list_filter = ('aprove', 'event_date')
    search_fields = ('large_title', 'small_title')
    verbose_name_plural = "1. Homepage - Main Image"
    group = "Homepage"

@admin.register(HomePage_Sliding_Image)
class HomePage_Sliding_ImageAdmin(admin.ModelAdmin):
    list_display = ('small_title', 'category', 'date', 'aprove')
    list_display_links = ('small_title',)
    list_filter = ('aprove', 'category', 'date')
    search_fields = ('small_title', 'category', 'description')
    verbose_name_plural = "2. Homepage - Sliding Images"
    group = "Homepage"

@admin.register(HomePage_Category_Section)
class HomePage_Category_SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'aprove')
    list_display_links = ('title',)
    list_filter = ('aprove', 'date')
    search_fields = ('title',)
    verbose_name_plural = "3. Homepage - Category Section"
    group = "Homepage"

@admin.register(HomePage_Category_Side_Section)
class HomePage_Category_Side_SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'aprove')
    list_display_links = ('title',)
    list_filter = ('aprove', 'date')
    search_fields = ('title',)
    verbose_name_plural = "4. Homepage - Category Side Section"
    group = "Homepage"

@admin.register(HomePage_Category_Bottom_Section)
class HomePage_Category_Bottom_SectionAdmin(admin.ModelAdmin):
    list_display = ('title1', 'title2', 'aprove')
    list_display_links = ('title1',)
    list_filter = ('aprove',)
    search_fields = ('title1', 'title2', 'description')
    verbose_name_plural = "5. Homepage - Category Bottom Section"
    group = "Homepage"

@admin.register(HomePage_Posts_Main)
class HomePage_Posts_MainAdmin(admin.ModelAdmin):
    list_display = ('large_title', 'hoster_name', 'aprove')
    list_display_links = ('large_title',)
    list_filter = ('aprove',)
    search_fields = ('large_title', 'small_title', 'hoster_name')
    verbose_name_plural = "6. Homepage - Main Post"
    group = "Homepage"

@admin.register(HomePage_Posts_Side)
class HomePage_Posts_SideAdmin(admin.ModelAdmin):
    list_display = ('major_title', 'date', 'aprove')
    list_display_links = ('major_title',)
    list_filter = ('aprove', 'date')
    search_fields = ('major_title', 'descriptive_title')
    verbose_name_plural = "7. Homepage - Side Posts"
    group = "Homepage"

@admin.register(HomePage_Posts_Bottom_Section)
class HomePage_Posts_Bottom_SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'hoster_name', 'aprove')
    list_display_links = ('title',)
    list_filter = ('aprove',)
    search_fields = ('title', 'hoster_name')
    verbose_name_plural = "8. Homepage - Bottom Posts"
    group = "Homepage"

# --- About Us Models ---

@admin.register(About_us_title)
class About_us_titleAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    verbose_name_plural = "1. About Us - Title"
    group = "About Us"

@admin.register(About_us_top_section)
class About_us_top_sectionAdmin(admin.ModelAdmin):
    list_display = ('major_title', 'years_of_experience', 'no_of_events')
    list_display_links = ('major_title',)
    verbose_name_plural = "2. About Us - Top Section"
    group = "About Us"

@admin.register(About_us_team_title)
class About_us_team_titleAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    verbose_name_plural = "3. About Us - Team Title"
    group = "About Us"

@admin.register(About_us_team)
class About_us_teamAdmin(admin.ModelAdmin):
    list_display = ('name', 'ocupation', 'aprove')
    list_display_links = ('name',)
    list_filter = ('aprove', 'ocupation')
    search_fields = ('name', 'ocupation')
    verbose_name_plural = "4. About Us - Team Members"
    group = "About Us"

# --- Blog & Article Models ---

@admin.register(blog_top_image)
class blog_top_imageAdmin(admin.ModelAdmin):
    list_display = ('image_description_major', 'profile_name', 'date_posted', 'aprove')
    list_display_links = ('image_description_major',)
    list_filter = ('aprove', 'date_posted')
    search_fields = ('image_description_major', 'profile_name')
    verbose_name_plural = "1. Blog - Top Image"
    group = "Blog & Articles"

@admin.register(Article_tab)
class Article_tabAdmin(admin.ModelAdmin):
    list_display = ('tab_one', 'tab_two', 'tab_three', 'tab_four', 'tab_five')
    list_display_links = ('tab_one',)
    verbose_name_plural = "2. Blog - Article Tab Names"
    group = "Blog & Articles"

@admin.register(tab_one)
class tab_oneAdmin(admin.ModelAdmin):
    search_fields = ('major_description', 'quote_author')
    verbose_name_plural = "3. Blog - Article Tab 1 Content"
    group = "Blog & Articles"



@admin.register(tab_three)
class tab_threeAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_display_links = ('title',)
    search_fields = ('title', 'description')
    verbose_name_plural = "5. Blog - Article Tab 3 Content"
    group = "Blog & Articles"

@admin.register(tab_three_post)
class tab_three_postAdmin(admin.ModelAdmin):
    list_display = ('image_title', 'aprove')
    list_display_links = ('image_title',)
    list_filter = ('aprove',)
    verbose_name_plural = "6. Blog - Article Tab 3 Posts"
    group = "Blog & Articles"

@admin.register(tab_four)
class tab_fourAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_display_links = ('title',)
    search_fields = ('title',)
    verbose_name_plural = "7. Blog - Article Tab 4 Content"
    group = "Blog & Articles"

@admin.register(tab_five)
class tab_fiveAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_display_links = ('title',)
    search_fields = ('title',)
    verbose_name_plural = "8. Blog - Article Tab 5 Content"
    group = "Blog & Articles"

@admin.register(tab_five_post)
class tab_five_postAdmin(admin.ModelAdmin):
    list_display = ('title', 'aprove')
    list_display_links = ('title',)
    list_filter = ('aprove',)
    search_fields = ('title',)
    verbose_name_plural = "9. Blog - Article Tab 5 Posts"
    group = "Blog & Articles"

@admin.register(tab_six)
class tab_sixAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_display_links = ('title',)
    search_fields = ('title',)
    verbose_name_plural = "10. Blog - Article Tab 6 Content"
    group = "Blog & Articles"

@admin.register(tab_seven)
class tab_sevenAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_display_links = ('title',)
    search_fields = ('title',)
    verbose_name_plural = "11. Blog - Article Tab 7 Content"
    group = "Blog & Articles"

@admin.register(tab_eight)
class tab_eightAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_display_links = ('title',)
    search_fields = ('title',)
    verbose_name_plural = "11. Blog - Article Tab 8 Content"
    group = "Blog & Articles"

@admin.register(tab_nine)
class tab_nineAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_display_links = ('title',)
    search_fields = ('title',)
    verbose_name_plural = "12. Blog - Article Tab 9 Content"

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'name', 'email', 'subject', 'message')
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected messages as unread"

    fieldsets = (
        ('Message Information', {
            'fields': ('name', 'email', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )

    def has_add_permission(self, request):
        return False
    group = "Blog & Articles"