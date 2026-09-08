/* ============================================
   SIDEBAR SCROLL POSITION PERSISTENCE
   Saves and restores sidebar scroll position
   ============================================ */
(function() {
    'use strict';

    const STORAGE_KEY = 'sidebarScrollPosition';
    const SIDEBAR_SELECTOR = '.glass-sidebar';

    // Save scroll position before page unload
    function saveScrollPosition() {
        const sidebar = document.querySelector(SIDEBAR_SELECTOR);
        if (sidebar) {
            const scrollPosition = sidebar.scrollTop;
            localStorage.setItem(STORAGE_KEY, scrollPosition);
        }
    }

    // Restore scroll position on page load
    function restoreScrollPosition() {
        const sidebar = document.querySelector(SIDEBAR_SELECTOR);
        if (sidebar) {
            const savedPosition = localStorage.getItem(STORAGE_KEY);
            if (savedPosition !== null) {
                // Use multiple setTimeout to ensure DOM is fully loaded and rendered
                setTimeout(() => {
                    sidebar.scrollTop = parseInt(savedPosition, 10);
                }, 50);
                setTimeout(() => {
                    sidebar.scrollTop = parseInt(savedPosition, 10);
                }, 200);
                setTimeout(() => {
                    sidebar.scrollTop = parseInt(savedPosition, 10);
                }, 500);
            }
        }
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', restoreScrollPosition);
    } else {
        restoreScrollPosition();
    }

    // Save scroll position on scroll (debounced)
    let scrollTimeout;
    const sidebar = document.querySelector(SIDEBAR_SELECTOR);
    if (sidebar) {
        sidebar.addEventListener('scroll', function() {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(saveScrollPosition, 100);
        });
    }

    // Save before page unload
    window.addEventListener('beforeunload', saveScrollPosition);

    // Also save on navigation (for SPA-like behavior)
    document.querySelectorAll('a[href]').forEach(link => {
        link.addEventListener('click', function() {
            saveScrollPosition();
        });
    });

    // Save on form submission
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            saveScrollPosition();
        });
    });

})();
