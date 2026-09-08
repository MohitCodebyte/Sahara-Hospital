/* ============================================
   PREMIUM ANIMATED CURSOR SYSTEM
   Lightweight, touch-friendly cursor effects
   ============================================ */

(function() {
    'use strict';

    // Check if device is touch-enabled
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    
    if (isTouchDevice) {
        return; // Disable cursor effects on touch devices
    }

    // Create cursor elements
    const cursor = document.createElement('div');
    const cursorDot = document.createElement('div');
    
    cursor.className = 'glass-cursor';
    cursorDot.className = 'glass-cursor-dot';
    
    document.body.appendChild(cursor);
    document.body.appendChild(cursorDot);

    // Cursor styles
    const cursorStyles = `
        .glass-cursor {
            position: fixed;
            width: 32px;
            height: 32px;
            border: 2px solid rgba(59, 130, 246, 0.5);
            border-radius: 50%;
            pointer-events: none;
            z-index: 99999;
            transition: transform 0.15s ease-out, width 0.2s ease, height 0.2s ease, border-color 0.2s ease;
            transform: translate(-50%, -50%);
        }
        
        .glass-cursor-dot {
            position: fixed;
            width: 8px;
            height: 8px;
            background: rgba(59, 130, 246, 0.8);
            border-radius: 50%;
            pointer-events: none;
            z-index: 99999;
            transform: translate(-50%, -50%);
            transition: transform 0.05s ease-out;
        }
        
        .glass-cursor.hover {
            width: 48px;
            height: 48px;
            border-color: rgba(59, 130, 246, 0.8);
            background: rgba(59, 130, 246, 0.1);
        }
        
        .glass-cursor.click {
            width: 24px;
            height: 24px;
            border-color: rgba(16, 185, 129, 0.8);
            background: rgba(16, 185, 129, 0.1);
        }
        
        .glass-cursor.magnetic {
            transition: transform 0.3s cubic-bezier(0.23, 1, 0.32, 1);
        }
    `;
    
    const styleSheet = document.createElement('style');
    styleSheet.textContent = cursorStyles;
    document.head.appendChild(styleSheet);

    // Cursor position tracking
    let mouseX = 0;
    let mouseY = 0;
    let cursorX = 0;
    let cursorY = 0;
    let dotX = 0;
    let dotY = 0;

    // Update mouse position
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    // Smooth cursor animation
    function animateCursor() {
        // Smooth follow for outer cursor
        cursorX += (mouseX - cursorX) * 0.15;
        cursorY += (mouseY - cursorY) * 0.15;
        
        // Faster follow for inner dot
        dotX += (mouseX - dotX) * 0.5;
        dotY += (mouseY - dotY) * 0.5;
        
        cursor.style.left = cursorX + 'px';
        cursor.style.top = cursorY + 'px';
        cursorDot.style.left = dotX + 'px';
        cursorDot.style.top = dotY + 'px';
        
        requestAnimationFrame(animateCursor);
    }
    
    animateCursor();

    // Hover effects for interactive elements
    const interactiveElements = 'a, button, .glass-btn, input, select, textarea, .glass-nav-item, .glass-dropdown-item, .glass-card';
    
    document.querySelectorAll(interactiveElements).forEach(el => {
        el.addEventListener('mouseenter', () => {
            cursor.classList.add('hover');
        });
        
        el.addEventListener('mouseleave', () => {
            cursor.classList.remove('hover');
            cursor.classList.remove('magnetic');
        });
        
        el.addEventListener('mousedown', () => {
            cursor.classList.add('click');
        });
        
        el.addEventListener('mouseup', () => {
            cursor.classList.remove('click');
        });
    });

    // Magnetic effect for buttons
    const magneticElements = document.querySelectorAll('.glass-btn, button');
    
    magneticElements.forEach(el => {
        el.addEventListener('mousemove', (e) => {
            const rect = el.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            
            const moveX = x * 0.3;
            const moveY = y * 0.3;
            
            cursor.classList.add('magnetic');
            cursor.style.transform = `translate(calc(-50% + ${moveX}px), calc(-50% + ${moveY}px))`;
        });
        
        el.addEventListener('mouseleave', () => {
            cursor.classList.remove('magnetic');
            cursor.style.transform = 'translate(-50%, -50%)';
        });
    });

    // Hide cursor when leaving window
    document.addEventListener('mouseleave', () => {
        cursor.style.opacity = '0';
        cursorDot.style.opacity = '0';
    });
    
    document.addEventListener('mouseenter', () => {
        cursor.style.opacity = '1';
        cursorDot.style.opacity = '1';
    });

    // Hide cursor on click
    document.addEventListener('mousedown', () => {
        cursor.classList.add('click');
    });
    
    document.addEventListener('mouseup', () => {
        cursor.classList.remove('click');
    });

})();
