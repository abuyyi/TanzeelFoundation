from django.shortcuts import render,redirect
from django.http import Http404
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
                    )

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
    return render(request, 'pages/contact.html')