/* ============================================
   PREMIUM ANIMATION SYSTEM
   IntersectionObserver-based scroll reveal
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    // Animation Observer Configuration
    const animationObserverOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    // Create Intersection Observer
    const animationObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                
                // Optional: Unobserve after animation
                // animationObserver.unobserve(entry.target);
            }
        });
    }, animationObserverOptions);

    // Observe all animation elements
    const animatedElements = document.querySelectorAll(
        '.animate-fade-up, .animate-fade-down, .animate-fade-left, .animate-fade-right, .animate-scale, .animate-blur, [data-animate-stagger]'
    );

    animatedElements.forEach(el => {
        animationObserver.observe(el);
    });

    // Counter Animation
    const counterObserverOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.5
    };

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.getAttribute('data-target'));
                const duration = 2000;
                const increment = target / (duration / 16);
                let current = 0;

                const updateCounter = () => {
                    current += increment;
                    if (current < target) {
                        counter.textContent = Math.ceil(current);
                        requestAnimationFrame(updateCounter);
                    } else {
                        counter.textContent = target;
                    }
                };

                updateCounter();
                counterObserver.unobserve(counter);
            }
        });
    }, counterObserverOptions);

    const counters = document.querySelectorAll('.counter');
    counters.forEach(counter => {
        counterObserver.observe(counter);
    });

    // Stagger Animation for Dynamic Elements
    const staggerObserverOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const staggerObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                staggerObserver.unobserve(entry.target);
            }
        });
    }, staggerObserverOptions);

    const staggerElements = document.querySelectorAll('[data-animate-stagger]');
    staggerElements.forEach(el => {
        staggerObserver.observe(el);
    });

    // Parallax Effect for Hero Elements
    const parallaxElements = document.querySelectorAll('[data-parallax]');
    
    if (parallaxElements.length > 0) {
        let ticking = false;

        window.addEventListener('scroll', function() {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const scrollY = window.scrollY;
                    
                    parallaxElements.forEach(el => {
                        const speed = parseFloat(el.getAttribute('data-parallax')) || 0.5;
                        const yPos = -(scrollY * speed);
                        el.style.transform = `translateY(${yPos}px)`;
                    });

                    ticking = false;
                });
                ticking = true;
            }
        }, { passive: true });
    }

    // Magnetic Effect for Buttons
    const magneticElements = document.querySelectorAll('[data-magnetic]');
    
    magneticElements.forEach(el => {
        el.addEventListener('mousemove', function(e) {
            const rect = el.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            
            el.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px)`;
        });

        el.addEventListener('mouseleave', function() {
            el.style.transform = 'translate(0, 0)';
        });
    });
});
