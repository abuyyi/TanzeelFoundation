from django.shortcuts import render,redirect
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
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
from .forms import ContactMessageForm

# Create your views here.
def homepage(request):
    # Get all the homepage content
    homepage_content = HomePage_Image.objects.filter(aprove=True)
    homepage_sliding_images = HomePage_Sliding_Image.objects.filter(aprove=True)
    HomePage_Category_Sections = HomePage_Category_Section.objects.filter(aprove=True).first()
    HomePage_Category_Side_Sections = HomePage_Category_Side_Section.objects.filter(aprove=True)
    HomePage_Category_Bottom_Sections = HomePage_Category_Bottom_Section.objects.filter(aprove=True)
    HomePage_Posts_Mains = HomePage_Posts_Main.objects.filter(aprove=True).first()
    HomePage_Posts_Sides = HomePage_Posts_Side.objects.filter(aprove=True)
    HomePage_Posts_Bottom_Sections = HomePage_Posts_Bottom_Section.objects.filter(aprove=True)


    # Pass it to the template in a context dictionary
    context = {
            'homepage_content': homepage_content,
            'homepage_sliding_images': homepage_sliding_images,
            'HomePage_Category_Sections': HomePage_Category_Sections,
            'HomePage_Category_Side_Sections': HomePage_Category_Side_Sections,
            'HomePage_Category_Bottom_Sections': HomePage_Category_Bottom_Sections,
            'HomePage_Posts_Mains': HomePage_Posts_Mains,
            'HomePage_Posts_Sides': HomePage_Posts_Sides,
            'HomePage_Posts_Bottom_Sections': HomePage_Posts_Bottom_Sections,
        }
    return render(request, 'pages/homepage.html', context)

def about(request):
    # Get all the about us content
    about_us_title = About_us_title.objects.first()
    About_us_teams = About_us_team.objects.filter(aprove = True)
    About_us_team_titles = About_us_team_title.objects.first()
    About_us_top_sections = About_us_top_section.objects.first()
    # Pass it to the template in a context dictionary
    context = {
            'about_us_title': about_us_title,
            'About_us_teams': About_us_teams,
            'About_us_team_titles': About_us_team_titles,
            'About_us_top_sections': About_us_top_sections,
        }
    return render(request, 'pages/about.html', context)

def contact(request):
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Your message has been sent. Thank you!'})
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('pages:contact')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ContactMessageForm()
    
    context = {'form': form}
    return render(request, 'pages/contact.html', context)

def blog(request):
    # Get all the blog content
    blog_top_images = blog_top_image.objects.filter(aprove=True).first()
    article_tabs = Article_tab.objects.first()
    tab_ones = tab_one.objects.first()
    tab_threes = tab_three.objects.first()
    tab_three_posts = tab_three_post.objects.filter(aprove=True)
    tab_fours = tab_four.objects.first()
    tab_fives = tab_five.objects.first()
    tab_five_posts = tab_five_post.objects.filter(aprove=True)
    tab_sixs = tab_six.objects.first()
    tab_sevens = tab_seven.objects.first()
    tab_eights = tab_eight.objects.first()
    tab_nines = tab_nine.objects.first()
    homepage_sliding_images = HomePage_Sliding_Image.objects.filter(aprove=True)
    HomePage_Category_Sections = HomePage_Category_Section.objects.filter(aprove=True).first()
    HomePage_Category_Bottom_Sections = HomePage_Category_Bottom_Section.objects.filter(aprove=True)
    HomePage_Posts_Mains = HomePage_Posts_Main.objects.filter(aprove=True).first()
    HomePage_Posts_Sides = HomePage_Posts_Side.objects.filter(aprove=True)
    HomePage_Posts_Bottom_Sections = HomePage_Posts_Bottom_Section.objects.filter(aprove=True)


    # Pass it to the template in a context dictionary
    context = {
            'blog_top_images': blog_top_images,
            'article_tabs': article_tabs,
            'tab_ones': tab_ones,
            'tab_threes': tab_threes,
            'tab_three_posts': tab_three_posts,
            'tab_fours': tab_fours,
            'tab_fives': tab_fives,
            'tab_five_posts': tab_five_posts,
            'tab_sixs': tab_sixs,
            'tab_sevens': tab_sevens,
            'tab_eights': tab_eights,
            'tab_nines': tab_nines,
            'homepage_sliding_images': homepage_sliding_images,
            'HomePage_Category_Sections': HomePage_Category_Sections,
            'HomePage_Category_Bottom_Sections': HomePage_Category_Bottom_Sections,
            'HomePage_Posts_Mains': HomePage_Posts_Mains,
            'HomePage_Posts_Sides': HomePage_Posts_Sides,
            'HomePage_Posts_Bottom_Sections': HomePage_Posts_Bottom_Sections,
        }
    return render(request, 'pages/blog.html', context)

