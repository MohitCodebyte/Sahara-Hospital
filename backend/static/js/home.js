/* ============================================
   SAHARA HOSPITAL - PREMIUM HOMEPAGE JAVASCRIPT
   Modern SaaS Dashboard Quality Experience
   ============================================ */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all systems
    initCustomCursor();
    initSmoothScroll();
    initScrollReveal();
    initNavbarScroll();
    initHeroAnimations();
    initCounterAnimations();
    initParticleSystem();
    initFloatingIcons();
});

/* ============================================
   CUSTOM PREMIUM CURSOR
   ============================================ */
function initCustomCursor() {
    // Check if device supports hover (disable on touch devices)
    const isTouchDevice = window.matchMedia('(hover: none) and (pointer: coarse)').matches;
    
    if (isTouchDevice) {
        return; // Skip cursor initialization on touch devices
    }

    // Create cursor elements
    const cursorDot = document.createElement('div');
    cursorDot.className = 'cursor-dot';
    
    const cursorRing = document.createElement('div');
    cursorRing.className = 'cursor-ring';
    
    document.body.appendChild(cursorDot);
    document.body.appendChild(cursorRing);

    // Cursor state
    let mouseX = 0, mouseY = 0;
    let ringX = 0, ringY = 0;
    let isHovering = false;

    // Track mouse movement with high precision
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        // Move dot instantly
        cursorDot.style.transform = `translate(${mouseX}px, ${mouseY}px)`;
    });

    // Smooth ring following with interpolation
    function animateCursor() {
        // Linear interpolation for smooth following
        ringX += (mouseX - ringX) * 0.15;
        ringY += (mouseY - ringY) * 0.15;
        
        cursorRing.style.transform = `translate(${ringX}px, ${ringY}px)`;
        
        requestAnimationFrame(animateCursor);
    }
    animateCursor();

    // Hover effects on interactive elements
    const interactiveElements = document.querySelectorAll('a, button, .action-card-premium, .department-card-premium, .doctor-card-premium');
    
    interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            isHovering = true;
            cursorRing.classList.add('hover');
        });
        
        el.addEventListener('mouseleave', () => {
            isHovering = false;
            cursorRing.classList.remove('hover');
        });
    });

    // Click animation
    document.addEventListener('mousedown', () => {
        cursorRing.classList.add('click');
    });
    
    document.addEventListener('mouseup', () => {
        cursorRing.classList.remove('click');
    });

    // Cursor trails
    const trails = [];
    const maxTrails = 10;
    
    for (let i = 0; i < maxTrails; i++) {
        const trail = document.createElement('div');
        trail.className = 'cursor-trail';
        trail.style.opacity = (1 - i / maxTrails) * 0.3;
        document.body.appendChild(trail);
        trails.push({ el: trail, x: mouseX, y: mouseY });
    }

    function animateTrails() {
        trails.forEach((trail, index) => {
            // Each trail follows with delay
            const delay = (index + 1) * 2;
            trail.x += (mouseX - trail.x) * (0.1 / (index + 1));
            trail.y += (mouseY - trail.y) * (0.1 / (index + 1));
            
            trail.el.style.transform = `translate(${trail.x}px, ${trail.y}px)`;
        });
        
        requestAnimationFrame(animateTrails);
    }
    animateTrails();
}

/* ============================================
   SMOOTH SCROLL SYSTEM
   ============================================ */
function initSmoothScroll() {
    // Override default anchor behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
                const startPosition = window.pageYOffset;
                const distance = targetPosition - startPosition;
                const duration = 1000;
                let startTime = null;

                // Easing function for smooth momentum
                function easeInOutCubic(t) {
                    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
                }

                function animation(currentTime) {
                    if (startTime === null) startTime = currentTime;
                    const timeElapsed = currentTime - startTime;
                    const progress = Math.min(timeElapsed / duration, 1);
                    
                    const ease = easeInOutCubic(progress);
                    window.scrollTo(0, startPosition + distance * ease);
                    
                    if (timeElapsed < duration) {
                        requestAnimationFrame(animation);
                    }
                }

                requestAnimationFrame(animation);
            }
        });
    });
}

/* ============================================
   NAVBAR SCROLL EFFECT
   ============================================ */
function initNavbarScroll() {
    const navbar = document.getElementById('mainNavbar');
    let lastScroll = 0;
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        // Add/remove scrolled class
        if (currentScroll > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        lastScroll = currentScroll;
    });
}

/* ============================================
   SCROLL REVEAL SYSTEM
   ============================================ */
function initScrollReveal() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all animated elements
    const animatedElements = document.querySelectorAll(
        '.animate-fade-up, .animate-fade-left, .animate-fade-right, .animate-scale, .animate-blur'
    );
    
    animatedElements.forEach(el => observer.observe(el));
}

/* ============================================
   HERO ANIMATIONS
   ============================================ */
function initHeroAnimations() {
    const heroContent = document.querySelector('.hero-content');
    
    if (heroContent) {
        // Staggered entrance animations
        const elements = heroContent.querySelectorAll('h1, p, .d-flex');
        
        elements.forEach((el, index) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            
            setTimeout(() => {
                el.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }, 200 + (index * 150));
        });
    }
}

/* ============================================
   COUNTER ANIMATIONS
   ============================================ */
function initCounterAnimations() {
    const counters = document.querySelectorAll('.counter');
    
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.getAttribute('data-target'));
                const duration = 2000;
                const increment = target / (duration / 16);
                let current = 0;
                
                function updateCounter() {
                    current += increment;
                    if (current < target) {
                        counter.textContent = Math.ceil(current);
                        requestAnimationFrame(updateCounter);
                    } else {
                        counter.textContent = target;
                    }
                }
                
                updateCounter();
                counterObserver.unobserve(counter);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => counterObserver.observe(counter));
}

/* ============================================
   PARTICLE SYSTEM
   ============================================ */
function initParticleSystem() {
    const hero = document.querySelector('.hero');
    
    if (!hero) return;
    
    const particleCount = 30;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'hero-particle';
        
        // Random positioning
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 15 + 's';
        particle.style.animationDuration = (10 + Math.random() * 10) + 's';
        
        hero.appendChild(particle);
    }
}

/* ============================================
   FLOATING ICONS
   ============================================ */
function initFloatingIcons() {
    const hero = document.querySelector('.hero');
    
    if (!hero) return;
    
    const icons = [
        { icon: 'fa-heartbeat', top: '15%', left: '10%' },
        { icon: 'fa-stethoscope', top: '25%', right: '15%' },
        { icon: 'fa-pills', top: '60%', left: '8%' },
        { icon: 'fa-syringe', top: '70%', right: '12%' },
        { icon: 'fa-dna', top: '40%', left: '5%' },
        { icon: 'fa-user-md', top: '50%', right: '8%' }
    ];
    
    icons.forEach((item, index) => {
        const icon = document.createElement('i');
        icon.className = `fas ${item.icon} hero-floating-icon`;
        icon.style.top = item.top;
        
        if (item.left) {
            icon.style.left = item.left;
        }
        if (item.right) {
            icon.style.right = item.right;
        }
        
        icon.style.animationDelay = (index * 0.5) + 's';
        
        hero.appendChild(icon);
    });
}

/* ============================================
   BUTTON RIPPLE EFFECT
   ============================================ */
document.addEventListener('click', function(e) {
    const button = e.target.closest('.btn-premium, .btn-primary, .btn-gradient');
    
    if (button) {
        const rect = button.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const ripple = document.createElement('span');
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'rgba(255, 255, 255, 0.4)';
        ripple.style.width = '100px';
        ripple.style.height = '100px';
        ripple.style.left = x - 50 + 'px';
        ripple.style.top = y - 50 + 'px';
        ripple.style.transform = 'scale(0)';
        ripple.style.animation = 'ripple 0.6s ease-out';
        ripple.style.pointerEvents = 'none';
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }
});

// Add ripple animation keyframes dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

/* ============================================
   MAGNETIC EFFECT FOR CARDS
   ============================================ */
function initMagneticEffect() {
    const cards = document.querySelectorAll('.action-card-premium, .department-card-premium');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-10px)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
        });
    });
}

// Initialize magnetic effect after DOM is ready
setTimeout(initMagneticEffect, 100);

/* ============================================
   PERFORMANCE OPTIMIZATION
   ============================================ */

// Throttle function for performance
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Optimize scroll events
window.addEventListener('scroll', throttle(() => {
    // Scroll-related operations
}, 100));

// Optimize resize events
window.addEventListener('resize', debounce(() => {
    // Resize-related operations
}, 250));

/* ============================================
   LAZY LOADING FOR IMAGES
   ============================================ */
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

initLazyLoading();

/* ============================================
   PREFETCHING FOR PERFORMANCE
   ============================================ */
function initPrefetching() {
    const prefetchLinks = document.querySelectorAll('[data-prefetch]');
    
    prefetchLinks.forEach(link => {
        link.addEventListener('mouseenter', () => {
            const href = link.getAttribute('data-prefetch');
            if (href) {
                const prefetchLink = document.createElement('link');
                prefetchLink.rel = 'prefetch';
                prefetchLink.href = href;
                document.head.appendChild(prefetchLink);
            }
        });
    });
}

initPrefetching();
