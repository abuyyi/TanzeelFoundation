from .models import SiteSettings

# Import homepage models lazily to avoid import-time DB access when running management commands
def site_settings(request):
    settings = SiteSettings.objects.first()
    return {'site_settings': settings}


def division_footer_links(request):
    """Build robust anchors for footer division links by scanning homepage models.

    This searches multiple homepage models and returns the exact fragment
    identifiers used by the homepage Continue Reading buttons so the footer
    navigates to the exact same anchors on the blog page.
    """
    try:
        from pages.models import (
            HomePage_Sliding_Image,
            HomePage_Category_Section,
            HomePage_Posts_Main,
            HomePage_Posts_Side,
            HomePage_Posts_Bottom_Section,
            HomePage_Category_Bottom_Section,
        )
    except Exception:
        # In situations where apps aren't ready (manage.py commands) fail gracefully
        return {
            'division_footer_tsdf': None,
            'division_footer_tanzeel_waqfu': None,
            'division_footer_social_service': None,
            'division_footer_education_center': None,
        }

    # Normalize helper
    def norm(s):
        return (s or '').strip().lower()

    targets = {
        'tsdf': None,
        'tanzeel waqfu': None,
        'social service': None,
        'education center': None,
    }

    def try_set(label, anchor):
        if not label:
            return
        key = norm(label)
        for desired in list(targets.keys()):
            if targets[desired]:
                continue
            # fuzzy match: either contains or is contained
            if desired in key or key in desired:
                targets[desired] = anchor

    # Sliding images: homepage uses "#article-{{ Sliding_image.link_url1 }}"
    for slide in HomePage_Sliding_Image.objects.filter(aprove=True):
        anchor = None
        if slide.link_url1:
            anchor = f"article-{slide.link_url1.strip()}"
        try_set(slide.category, anchor)
        try_set(slide.small_title, anchor)

    # Category section: homepage uses "#article-{{ HomePage_Category_Sections.link_url1 }}"
    cat = HomePage_Category_Section.objects.filter(aprove=True).first()
    if cat and cat.link_url1:
        try_set(cat.title, f"article-{cat.link_url1.strip()}")

    # Main post: homepage uses "#article3-{{ HomePage_Posts_Mains.link_url }}"
    main = HomePage_Posts_Main.objects.filter(aprove=True).first()
    if main and main.link_url:
        try_set(main.small_title, f"article3-{main.link_url.strip()}")
        try_set(main.large_title, f"article3-{main.link_url.strip()}")

    # Side posts: homepage uses "#article4-{{ side_post.link_url }}"
    for side in HomePage_Posts_Side.objects.filter(aprove=True):
        if side.link_url:
            try_set(side.major_title, f"article4-{side.link_url.strip()}")
            try_set(side.descriptive_title, f"article4-{side.link_url.strip()}")

    # Bottom posts: homepage uses "#article5-{{ posts.link_url }}" and sometimes "#article2-{{ post.link_url }}"
    for post in HomePage_Posts_Bottom_Section.objects.filter(aprove=True):
        if post.link_url:
            try_set(post.title, f"article5-{post.link_url.strip()}")
            try_set(post.descriptive_title, f"article5-{post.link_url.strip()}")
            try_set(getattr(post, 'title1', None), f"article5-{post.link_url.strip()}")

    for post in HomePage_Category_Bottom_Section.objects.filter(aprove=True):
        link = post.link_url if hasattr(post, 'link_url') else None
        if link:
            try_set(getattr(post, 'title1', None) or (post.title if hasattr(post, 'title') else None), f"article2-{link.strip()}")

    return {
        'division_footer_tsdf': targets.get('tsdf'),
        'division_footer_tanzeel_waqfu': targets.get('tanzeel waqfu'),
        'division_footer_social_service': targets.get('social service'),
        'division_footer_education_center': targets.get('education center'),
    }
