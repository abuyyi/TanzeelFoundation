/**
* Template Name: Story
* Template URL: https://bootstrapmade.com/story-bootstrap-blog-template/
* Updated: Aug 11 2025 with Bootstrap v5.3.7
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/

(function() {
  "use strict";

  /**
   * Apply .scrolled class to the body as the page is scrolled down
   */
  function toggleScrolled() {
    const selectBody = document.querySelector('body');
    const selectHeader = document.querySelector('#header');
    if (!selectHeader.classList.contains('scroll-up-sticky') && !selectHeader.classList.contains('sticky-top') && !selectHeader.classList.contains('fixed-top')) return;
    window.scrollY > 100 ? selectBody.classList.add('scrolled') : selectBody.classList.remove('scrolled');
  }

  document.addEventListener('scroll', toggleScrolled);
  window.addEventListener('load', toggleScrolled);

  /**
   * Mobile nav toggle
   */
  const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');

  function mobileNavToogle() {
    document.querySelector('body').classList.toggle('mobile-nav-active');
    mobileNavToggleBtn.classList.toggle('bi-list');
    mobileNavToggleBtn.classList.toggle('bi-x');
  }
  if (mobileNavToggleBtn) {
    mobileNavToggleBtn.addEventListener('click', mobileNavToogle);
  }

  /**
   * Hide mobile nav on same-page/hash links
   */
  document.querySelectorAll('#navmenu a').forEach(navmenu => {
    navmenu.addEventListener('click', () => {
      if (document.querySelector('.mobile-nav-active')) {
        mobileNavToogle();
      }
    });

  });

  /**
   * Toggle mobile nav dropdowns
   */
  document.querySelectorAll('.navmenu .toggle-dropdown').forEach(navmenu => {
    navmenu.addEventListener('click', function(e) {
      e.preventDefault();
      this.parentNode.classList.toggle('active');
      this.parentNode.nextElementSibling.classList.toggle('dropdown-active');
      e.stopImmediatePropagation();
    });
  });

  /**
   * Preloader
   */
  const preloader = document.querySelector('#preloader');
  if (preloader) {
    window.addEventListener('load', () => {
      preloader.remove();
    });
  }

  /**
   * Scroll top button
   */
  let scrollTop = document.querySelector('.scroll-top');

  function toggleScrollTop() {
    if (scrollTop) {
      window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
    }
  }
  scrollTop.addEventListener('click', (e) => {
    e.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  window.addEventListener('load', toggleScrollTop);
  document.addEventListener('scroll', toggleScrollTop);

  /**
   * Animation on scroll function and init
   */
  function aosInit() {
    AOS.init({
      duration: 600,
      easing: 'ease-in-out',
      once: true,
      mirror: false
    });
  }
  window.addEventListener('load', aosInit);

  /**
   * Init swiper sliders
   */
  function initSwiper() {
    document.querySelectorAll(".init-swiper").forEach(function(swiperElement) {
      let config = JSON.parse(
        swiperElement.querySelector(".swiper-config").innerHTML.trim()
      );

      if (swiperElement.classList.contains("swiper-tab")) {
        initSwiperWithCustomPagination(swiperElement, config);
      } else {
        new Swiper(swiperElement, config);
      }
    });
  }

  window.addEventListener("load", initSwiper);

  /**
   * Initiate Pure Counter
   */
  new PureCounter();

})();

/**
 * Seamless Infinite Marquee Logic (Left to Right)
 * Preserves exact original layout, classes, and breakpoints.
 */
document.addEventListener('DOMContentLoaded', () => {
  const sliders = document.querySelectorAll('.custom-marquee');
  
  sliders.forEach(slider => {
    const wrapper = slider.querySelector('.marquee-wrapper');
    if (!wrapper) return;
    
    // Store original items without any previous clones
    const originalSlides = Array.from(wrapper.children).filter(child => !child.classList.contains('marquee-clone'));

    const setupMarquee = () => {
      // 1. Clean up old clones (important for resizing)
      Array.from(wrapper.children).forEach(child => {
        if (child.classList.contains('marquee-clone')) {
          wrapper.removeChild(child);
        }
      });

      const containerWidth = slider.offsetWidth;
      if (containerWidth === 0) return;

      // 2. Exact Swiper breakpoints logic to maintain original appearance perfectly
      let slidesPerView = 1;
      let spaceBetween = 40;
      const winWidth = window.innerWidth;
      
      if (winWidth >= 1200) {
        slidesPerView = 2.2;
        spaceBetween = 40;
      } else if (winWidth >= 768) {
        slidesPerView = 1.5;
        spaceBetween = 30;
      }

      // Calculate width for each slide exactly as Swiper did
      const slideWidth = (containerWidth - (spaceBetween * (slidesPerView - 1))) / slidesPerView;

      let originalWidth = 0;
      originalSlides.forEach(slide => {
        slide.style.width = `${slideWidth}px`;
        slide.style.marginRight = `${spaceBetween}px`;
        slide.style.flexShrink = '0';
        originalWidth += slideWidth + spaceBetween;
      });

      if (originalWidth === 0) return;

      // 3. Fill screen width to avoid gaps if there are very few items
      let currentSetWidth = originalWidth;
      while (currentSetWidth < containerWidth && currentSetWidth > 0) {
        originalSlides.forEach(slide => {
          const clone = slide.cloneNode(true);
          clone.classList.add('marquee-clone');
          clone.setAttribute('aria-hidden', 'true');
          wrapper.appendChild(clone);
        });
        currentSetWidth += originalWidth;
      }

      // 4. Mirror track for seamless -50% CSS transition
      const firstHalfSlides = Array.from(wrapper.children);
      firstHalfSlides.forEach(slide => {
        const clone = slide.cloneNode(true);
        clone.classList.add('marquee-clone');
        clone.setAttribute('aria-hidden', 'true');
        wrapper.appendChild(clone);
      });
      
      // 5. Animation Speed 
      // Current set width determines duration to keep speed constant
      const speedPixelsPerSecond = 50; 
      const duration = currentSetWidth / speedPixelsPerSecond;
      wrapper.style.animationDuration = `${duration}s`;
    };

    // Use setTimeout to ensure container has rendered its width
    setTimeout(setupMarquee, 100);

    let resizeTimeout;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(setupMarquee, 250);
    });
  });
});