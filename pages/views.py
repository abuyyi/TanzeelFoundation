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
