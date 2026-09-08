/* ============================================
   PREMIUM SMOOTH SCROLL SYSTEM
   requestAnimationFrame-based smooth scrolling
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#' || href === '#!') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                
                const targetPosition = target.getBoundingClientRect().top + window.scrollY;
                const startPosition = window.scrollY;
                const distance = targetPosition - startPosition - 80; // Account for navbar
                const duration = 1000;
                let start = null;

                function animation(currentTime) {
                    if (start === null) start = currentTime;
                    const timeElapsed = currentTime - start;
                    const progress = Math.min(timeElapsed / duration, 1);
                    
                    // Easing function (ease-out cubic)
                    const ease = 1 - Math.pow(1 - progress, 3);
                    
                    window.scrollTo(0, startPosition + distance * ease);
                    
                    if (timeElapsed < duration) {
                        requestAnimationFrame(animation);
                    }
                }

                requestAnimationFrame(animation);
            }
        });
    });

    // Back to top button
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopButton.className = 'back-to-top';
    backToTopButton.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white;
        border: none;
        cursor: pointer;
        opacity: 0;
        visibility: hidden;
        transform: translateY(20px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        z-index: 1000;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        font-size: 1.2rem;
    `;
    
    document.body.appendChild(backToTopButton);

    // Show/hide back to top button
    let ticking = false;
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                if (window.scrollY > 500) {
                    backToTopButton.style.opacity = '1';
                    backToTopButton.style.visibility = 'visible';
                    backToTopButton.style.transform = 'translateY(0)';
                } else {
                    backToTopButton.style.opacity = '0';
                    backToTopButton.style.visibility = 'hidden';
                    backToTopButton.style.transform = 'translateY(20px)';
                }
                ticking = false;
            });
            ticking = true;
        }
    }, { passive: true });

    // Back to top click handler
    backToTopButton.addEventListener('click', function() {
        const startPosition = window.scrollY;
        const duration = 800;
        let start = null;

        function animation(currentTime) {
            if (start === null) start = currentTime;
            const timeElapsed = currentTime - start;
            const progress = Math.min(timeElapsed / duration, 1);
            
            // Easing function (ease-out cubic)
            const ease = 1 - Math.pow(1 - progress, 3);
            
            window.scrollTo(0, startPosition * (1 - ease));
            
            if (timeElapsed < duration) {
                requestAnimationFrame(animation);
            }
        }

        requestAnimationFrame(animation);
    });

    // Smooth scroll to section on load (if hash in URL)
    if (window.location.hash) {
        const target = document.querySelector(window.location.hash);
        if (target) {
            setTimeout(() => {
                const targetPosition = target.getBoundingClientRect().top + window.scrollY;
                window.scrollTo({
                    top: targetPosition - 80,
                    behavior: 'smooth'
                });
            }, 100);
        }
    }
});
