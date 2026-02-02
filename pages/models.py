from django.db import models
from django.utils.text import slugify
from django.utils.text import slugify

# Create your models here.

class HomePage_Image(models.Model):
    image = models.ImageField(upload_to='homepage_images/')
    small_title = models.CharField(max_length=15)
    large_title = models.CharField(max_length=60)
    link_url = models.CharField(max_length=200, blank=True, help_text="Optional: For an external link, enter the full URL (e.g., https://example.com). For an internal link, enter the path (e.g., /about/).")
    event_date = models.DateField(null=True, blank=True, help_text="Optional: Date of the event if applicable.")
    event_location = models.CharField(max_length=255, blank=True, help_text="Optional")
    event_time = models.TimeField(null=True, blank=True, help_text="Optional")
    aprove = models.BooleanField(default=False)

    def __str__(self):
        return self.large_title
    
class HomePage_Sliding_Image(models.Model):
    image1 = models.ImageField(upload_to='homepage_sliding_images/')
    category = models.CharField(max_length=15)
    image2 = models.ImageField(upload_to='homepage_sliding_images/')
    small_title = models.CharField(max_length=30)
    date = models.DateField(null=True, blank=True)
    link_url1 = models.CharField(max_length=200, blank=True, help_text="Optional: For an external link, enter the full URL (e.g., https://example.com). For an internal link, enter the path (e.g., /about/).")
    description = models.TextField(("Optional: A brief description of the image or event."), blank=True)
    description = models.TextField(("Optional: A brief description of the image or event."), blank=True)
    time = models.TimeField(null=True, blank=True)
    link_url2 = models.CharField(max_length=200, blank=True, help_text="Optional: For an external link, enter the full URL (e.g., https://example.com). For an internal link, enter the path (e.g., /about/).")
    aprove = models.BooleanField(default=False)

    def __str__(self):
        return self.small_title
    
class HomePage_Category_Section(models.Model):
    image1 = models.ImageField(upload_to='homepage_category_sections/', blank=True, null=True)
    image2 = models.ImageField(upload_to='homepage_category_sections/', blank=True, null=True)
    title = models.CharField(max_length=100)
    date = models.DateField(null=True, blank=True)
    link_url1 = models.CharField(max_length=200, blank=True, help_text="Optional: For an external link, enter the full URL (e.g., https://example.com). For an internal link, enter the path (e.g., /about/).")
    description = models.CharField(max_length=500,blank=True)
    time = models.TimeField(null=True, blank=True)
    comment = models.CharField(max_length=20, blank=True)
    aprove = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class HomePage_Category_Side_Section(models.Model):
    image = models.ImageField(upload_to='homepage_category_side_section/')
    title = models.CharField(max_length=100)
    link_url = models.CharField(max_length=200, blank=True, help_text="Optional: For an external link, enter the full URL (e.g., https://example.com). For an internal link, enter the path (e.g., /about/).")
    date = models.DateField(null=True, blank=True)
    aprove = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class HomePage_Category_Bottom_Section(models.Model):
    image1 = models.ImageField(upload_to='homepage_Posts/')
    title1 = models.CharField(max_length=200)
    link_url = models.CharField(max_length=200, blank=True, help_text="Optional: For an external link, enter the full URL (e.g., https://example.com). For an internal link, enter the path (e.g., /about/).")
    description = models.CharField(max_length=500,blank=True)
    image2 = models.ImageField(upload_to='homepage_Posts/')
    title2 = models.CharField(max_length=200)
    time = models.TimeField(null=True, blank=True)
    aprove = models.BooleanField(default=False)

    def __str__(self):
        return self.title1
    
class HomePage_Posts_Main(models.Model):
    image = models.ImageField(upload_to='homepage_Posts_Main/')
    day = models.CharField(max_length=10, help_text="e.g., 12")
    month = models.CharField(max_length=10, help_text="e.g., Dec")
    small_title = models.CharField(max_length=20)
    large_title = models.CharField(max_length=200)
    description = models.CharField(max_length=255,blank=True)
    hoster_name = models.CharField(max_length=100)
    content = models.CharField(max_length=10)
    link_url = models.CharField(max_length=200, blank=True, help_text="Optional: For an external link, enter the full URL (e.g., https://example.com). For an internal link, enter the path (e.g., /about/).")
    aprove = models.BooleanField(default=False)

    def __str__(self):
        return self.small_title
    
class HomePage_Posts_Side(models.Model):
    image = models.ImageField(upload_to='homepage_Posts_Side/')
    date = models.DateField(null=True, blank=True)
    major_title = models.CharField(max_length=200)
    descriptive_title = models.CharField(max_length=255,blank=True)
    link_url = models.CharField(max_length=200, blank=True, help_text="Optional: For an external link, enter the full URL (e.g., https://example.com). For an internal link, enter the path (e.g., /about/).")
    aprove = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.major_title
    
class HomePage_Posts_Bottom_Section(models.Model):
    image = models.ImageField(upload_to='homepage_Posts_Bottom_Section/')
    title = models.CharField(max_length=200)
    hoster_name = models.CharField(max_length=20)
    description = models.CharField(max_length=500,blank=True)
    link_url = models.CharField(max_length=200, blank=True, help_text="Optional: For an external link, enter the full URL (e.g., https://example.com). For an internal link, enter the path (e.g., /about/).")
    aprove = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    


    
class About_us_title(models.Model):
    description = models.TextField()

    def __str__(self):
        return "About Us Content"
    
class About_us_top_section(models.Model):
    image = models.ImageField(upload_to='Top_section/')
    years_of_experience = models.CharField(max_length=2)
    no_of_events = models.CharField(max_length=3)
    major_title = models.CharField(max_length=30)
    major_description = models.CharField(max_length=255,blank=True)
    minor_title1 = models.CharField(max_length=30)
    minor_description1 = models.CharField(max_length=255,blank=True)
    minor_title2 = models.CharField(max_length=30)
    minor_description2 = models.CharField(max_length=255,blank=True)
    comment1 = models.CharField(max_length=100, blank=True)
    comment2 = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return "Top Section"

    
class About_us_team_title(models.Model):
    description = models.TextField()

    def __str__(self):
        return "About Us Team Title"
    
class About_us_team(models.Model):
    image = models.ImageField(upload_to='About_us_team/')
    linkedin_link_url = models.CharField(max_length=200, blank=True, help_text="Optional: For an external link, enter the full URL (e.g., https://example.com). For an internal link, enter the path (e.g., /about/).")
    twitter_link_url = models.CharField(max_length=200, blank=True, help_text="Optional: For an external link, enter the full URL (e.g., https://example.com). For an internal link, enter the path (e.g., /about/).")
    instagram_link_url = models.CharField(max_length=200, blank=True, help_text="Optional: For an external link, enter the full URL (e.g., https://example.com). For an internal link, enter the path (e.g., /about/).")
    name = models.CharField(max_length=20)
    ocupation = models.CharField(max_length=20)
    description = models.CharField(max_length=255,blank=True)
    aprove = models.BooleanField(default=False)

    def __str__(self):
        return self.ocupation
    


class blog_top_image(models.Model):
    image = models.ImageField(upload_to='blog_top_image')
    image_description_major = models.CharField(max_length=100)
    image_description_minor = models.CharField(max_length=255, blank=True)
    image_profile = models.ImageField(upload_to='blog_top_image_profile')
    profile_name = models.CharField(max_length=50)
    profile_occupation = models.CharField(max_length=50)
    date_posted = models.DateField(null=True, blank=True)
    time_posted = models.TimeField(null=True, blank=True)
    aprove = models.BooleanField(default=False)

    def __str__(self):
        return self.image_description_major
    


class Article_tab(models.Model):
    tab_one = models.CharField(max_length=50)
    tab_two = models.CharField(max_length=50)
    tab_three = models.CharField(max_length=50)
    tab_four = models.CharField(max_length=50) 
    tab_five = models.CharField(max_length=50)
    tab_six = models.CharField(max_length=50 , default="")
    tab_seven = models.CharField(max_length=50, default="")
    tab_eight = models.CharField(max_length=50, default="")
    tab_nine = models.CharField(max_length=50, default="")
    

    def __str__(self):
        return self.tab_one
    
class tab_one(models.Model):
    major_description = models.CharField(max_length=300)
    minor_description = models.CharField(max_length=255, blank=True)
    quote = models.CharField(max_length=255, blank=True)
    quote_author = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.major_description
    
    
class tab_three(models.Model):
    title = models.CharField(max_length=40)
    description = models.CharField(max_length=255)
    
    def __str__(self):
        return self.title
    
class tab_three_post(models.Model):
    image = models.ImageField(upload_to='tab_three_images/')
    image_title = models.CharField(max_length=20, blank=True)
    image_description = models.CharField(max_length=80, blank=True)
    aprove = models.BooleanField(default=False)

    def __str__(self):
        return self.image_title
    
class tab_four(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    point_one = models.CharField(max_length=60)
    point_two = models.CharField(max_length=60)
    point_three = models.CharField(max_length=60)
    point_four = models.CharField(max_length=60)

    def __str__(self):
        return self.title
    
class tab_five(models.Model):
    title = models.CharField(max_length=100)
    
    def __str__(self):
        return self.title

class tab_five_post(models.Model):
    title = models.CharField(max_length=40)
    description = models.CharField(max_length=200)
    aprove = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class tab_six(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)

    def __str__(self):
        return self.title

class tab_seven(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)

    def __str__(self):
        return self.title

class tab_eight(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)

    def __str__(self):
        return self.title



class tab_nine(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    """Model to store contact form submissions"""
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
