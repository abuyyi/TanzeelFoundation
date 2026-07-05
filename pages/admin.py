from django.contrib import admin
from django.utils.html import format_html
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
                     ContactMessage,
                     Appeal,
                     AppealImpact,
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

# ─────────────────────────────────────────────────────────────────────
# ABOUT US ADMIN CLASSES  –  premium list display
# ─────────────────────────────────────────────────────────────────────

@admin.register(About_us_title)
class About_us_titleAdmin(admin.ModelAdmin):
    list_display = ('record_label', 'description_preview')
    list_per_page = 25
    verbose_name_plural = "1. About Us - Title"
    group = "About Us"

    @admin.display(description='Record')
    def record_label(self, obj):
        return format_html(
            '<span style="display:inline-flex;align-items:center;gap:7px;font-weight:700;'
            'color:#6d28d9;">'
            '<span style="width:8px;height:8px;border-radius:50%;background:#6d28d9;'
            'display:inline-block;"></span> About Us Content</span>'
        )

    @admin.display(description='Description Preview')
    def description_preview(self, obj):
        text = obj.description or ''
        preview = (text[:120] + '…') if len(text) > 120 else text
        return format_html(
            '<span style="font-size:13px;color:#475569;line-height:1.5;">{}</span>',
            preview
        )


@admin.register(About_us_top_section)
class About_us_top_sectionAdmin(admin.ModelAdmin):
    list_display = ('major_title', 'experience_badge', 'events_badge',
                    'minor_title1', 'minor_title2')
    list_display_links = ('major_title',)
    search_fields = ('major_title', 'minor_title1', 'minor_title2')
    list_per_page = 25
    verbose_name_plural = "2. About Us - Top Section"
    group = "About Us"

    @admin.display(description='Years of Experience')
    def experience_badge(self, obj):
        return format_html(
            '<span style="display:inline-flex;align-items:center;gap:5px;'
            'background:rgba(37,99,235,0.08);color:#2563eb;padding:4px 12px;'
            'border-radius:50px;font-size:12px;font-weight:700;'
            'border:1px solid rgba(37,99,235,0.2);">'
            '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" '
            'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'
            '</svg> {}+ yrs</span>',
            obj.years_of_experience
        )

    @admin.display(description='No. of Events')
    def events_badge(self, obj):
        return format_html(
            '<span style="display:inline-flex;align-items:center;gap:5px;'
            'background:rgba(34,197,94,0.08);color:#16a34a;padding:4px 12px;'
            'border-radius:50px;font-size:12px;font-weight:700;'
            'border:1px solid rgba(34,197,94,0.2);">{} events</span>',
            obj.no_of_events
        )


@admin.register(About_us_team_title)
class About_us_team_titleAdmin(admin.ModelAdmin):
    list_display = ('record_label', 'description_preview')
    list_per_page = 25
    verbose_name_plural = "3. About Us - Team Title"
    group = "About Us"

    @admin.display(description='Record')
    def record_label(self, obj):
        return format_html(
            '<span style="display:inline-flex;align-items:center;gap:7px;font-weight:700;'
            'color:#0891b2;">'
            '<span style="width:8px;height:8px;border-radius:50%;background:#0891b2;'
            'display:inline-block;"></span> Team Section Title</span>'
        )

    @admin.display(description='Description Preview')
    def description_preview(self, obj):
        text = obj.description or ''
        preview = (text[:120] + '…') if len(text) > 120 else text
        return format_html(
            '<span style="font-size:13px;color:#475569;line-height:1.5;">{}</span>',
            preview
        )


@admin.register(About_us_team)
class About_us_teamAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'occupation_badge', 'social_links', 'status_badge')
    list_display_links = ('member_name',)
    list_filter = ('aprove', 'ocupation')
    search_fields = ('name', 'ocupation', 'description')
    list_per_page = 25
    verbose_name_plural = "4. About Us - Team Members"
    group = "About Us"

    @admin.display(description='Team Member', ordering='name')
    def member_name(self, obj):
        return format_html(
            '<div style="display:flex;align-items:center;gap:10px;">'  
            '<div style="width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,'
            'rgba(109,40,217,0.15),rgba(6,182,212,0.15));color:#6d28d9;display:flex;'
            'align-items:center;justify-content:center;font-weight:800;font-size:13px;'
            'flex-shrink:0;border:2px solid rgba(109,40,217,0.2);">{}</div>'
            '<div><div style="font-weight:700;font-size:14px;color:#0f172a;">{}</div>'
            '<div style="font-size:11px;color:#94a3b8;">Team Member</div></div></div>',
            obj.name[:1].upper(),
            obj.name
        )

    @admin.display(description='Occupation', ordering='ocupation')
    def occupation_badge(self, obj):
        return format_html(
            '<span style="display:inline-flex;align-items:center;gap:5px;'
            'background:rgba(6,182,212,0.08);color:#0891b2;padding:5px 14px;'
            'border-radius:50px;font-size:12px;font-weight:600;'
            'border:1px solid rgba(6,182,212,0.2);white-space:nowrap;">{}</span>',
            obj.ocupation
        )

    @admin.display(description='Social Links')
    def social_links(self, obj):
        links = []
        if obj.linkedin_link_url:
            links.append(
                '<a href="{}" target="_blank" style="display:inline-flex;align-items:center;'
                'gap:4px;font-size:11px;font-weight:600;color:#0a66c2;background:rgba(10,102,194,0.08);'
                'padding:3px 9px;border-radius:6px;border:1px solid rgba(10,102,194,0.15);'
                'text-decoration:none;">in LinkedIn</a>'.format(obj.linkedin_link_url)
            )
        if obj.twitter_link_url:
            links.append(
                '<a href="{}" target="_blank" style="display:inline-flex;align-items:center;'
                'gap:4px;font-size:11px;font-weight:600;color:#1d9bf0;background:rgba(29,155,240,0.08);'
                'padding:3px 9px;border-radius:6px;border:1px solid rgba(29,155,240,0.15);'
                'text-decoration:none;">𝕏 Twitter</a>'.format(obj.twitter_link_url)
            )
        if obj.instagram_link_url:
            links.append(
                '<a href="{}" target="_blank" style="display:inline-flex;align-items:center;'
                'gap:4px;font-size:11px;font-weight:600;color:#e1306c;background:rgba(225,48,108,0.08);'
                'padding:3px 9px;border-radius:6px;border:1px solid rgba(225,48,108,0.15);'
                'text-decoration:none;">📷 Instagram</a>'.format(obj.instagram_link_url)
            )
        if not links:
            return format_html('<span style="color:#94a3b8;font-size:12px;">—</span>')
        return format_html(
            '<div style="display:flex;flex-wrap:wrap;gap:6px;">{}</div>',
            format_html(''.join(links))
        )

    @admin.display(description='Status', ordering='aprove', boolean=False)
    def status_badge(self, obj):
        if obj.aprove:
            return format_html(
                '<span style="display:inline-flex;align-items:center;gap:5px;'
                'background:rgba(34,197,94,0.1);color:#16a34a;padding:5px 14px;'
                'border-radius:50px;font-size:11px;font-weight:700;text-transform:uppercase;'
                'letter-spacing:0.04em;border:1px solid rgba(34,197,94,0.2);white-space:nowrap;">'
                '<span style="width:6px;height:6px;border-radius:50%;'
                'background:currentColor;"></span> Published</span>'
            )
        return format_html(
            '<span style="display:inline-flex;align-items:center;gap:5px;'
            'background:rgba(245,158,11,0.1);color:#d97706;padding:5px 14px;'
            'border-radius:50px;font-size:11px;font-weight:700;text-transform:uppercase;'
            'letter-spacing:0.04em;border:1px solid rgba(245,158,11,0.2);white-space:nowrap;">'
            '<span style="width:6px;height:6px;border-radius:50%;'
            'background:currentColor;"></span> Draft</span>'
        )

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

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'name', 'email', 'subject', 'message')
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)

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


# --- Appeals ---

@admin.register(AppealImpact)
class AppealImpactAdmin(admin.ModelAdmin):
    list_display = ('title', 'stat_number', 'stat_label', 'order', 'aprove')
    list_editable = ('aprove', 'order')
    search_fields = ('title', 'description')
    list_filter = ('aprove',)
    verbose_name_plural = "Appeal Impacts"


@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category', 'region', 'goal_amount', 'raised_amount', 'is_urgent', 'aprove', 'order')
    list_editable = ('aprove', 'order', 'is_urgent')
    readonly_fields = ('slug',)
    list_filter = ('category', 'region', 'aprove', 'is_urgent')
    search_fields = ('title', 'short_description')
    verbose_name_plural = "Appeals"