/* ============================================
   DASHBOARD UTILITIES - ANIMATED COUNTERS & CHARTS
   Premium 60fps animations using transform/opacity only
   ============================================ */
(function() {
    'use strict';

    // Animated Counter - Count up animation
    function animateCounter(element, target, duration = 2000, prefix = '', suffix = '') {
        const start = 0;
        const startTime = performance.now();
        
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = start + (target - start) * easeOutQuart;
            
            // Format number with commas
            const formatted = Math.floor(current).toLocaleString();
            element.textContent = prefix + formatted + suffix;
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        
        requestAnimationFrame(update);
    }

    // Initialize all counters on page load
    function initCounters() {
        const counters = document.querySelectorAll('[data-counter]');
        counters.forEach(counter => {
            const target = parseFloat(counter.getAttribute('data-counter'));
            const duration = parseInt(counter.getAttribute('data-duration')) || 2000;
            const prefix = counter.getAttribute('data-prefix') || '';
            const suffix = counter.getAttribute('data-suffix') || '';
            
            // Start animation when element is visible
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        animateCounter(entry.target, target, duration, prefix, suffix);
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.1 });
            
            observer.observe(counter);
        });
    }

    // Initialize Chart.js charts
    function initCharts() {
        // Revenue Trend Chart
        const revenueCtx = document.getElementById('revenueChart');
        if (revenueCtx) {
            new Chart(revenueCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Revenue',
                        data: [120000, 190000, 150000, 250000, 220000, 300000],
                        borderColor: '#2563EB',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        fill: true,
                        tension: 0.4,
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: '#E5E7EB'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeOutQuart'
                    }
                }
            });
        }

        // Payment Methods Chart
        const paymentCtx = document.getElementById('paymentChart');
        if (paymentCtx) {
            new Chart(paymentCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Cash', 'Online', 'Insurance', 'UPI'],
                    datasets: [{
                        data: [35, 30, 25, 10],
                        backgroundColor: ['#22C55E', '#2563EB', '#F59E0B', '#EF4444'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        }
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeOutQuart'
                    }
                }
            });
        }

        // Patient Gender Ratio Chart
        const genderCtx = document.getElementById('genderChart');
        if (genderCtx) {
            new Chart(genderCtx, {
                type: 'pie',
                data: {
                    labels: ['Male', 'Female'],
                    datasets: [{
                        data: [55, 45],
                        backgroundColor: ['#2563EB', '#EC4899'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        }
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeOutQuart'
                    }
                }
            });
        }

        // Stock In vs Stock Out Chart
        const stockCtx = document.getElementById('stockChart');
        if (stockCtx) {
            new Chart(stockCtx, {
                type: 'bar',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Stock In',
                        data: [120, 190, 150, 250, 220, 300],
                        backgroundColor: '#22C55E',
                        borderRadius: 4
                    }, {
                        label: 'Stock Out',
                        data: [80, 140, 110, 180, 160, 220],
                        backgroundColor: '#EF4444',
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: '#E5E7EB'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeOutQuart'
                    }
                }
            });
        }

        // Department Distribution Chart
        const deptCtx = document.getElementById('deptChart');
        if (deptCtx) {
            new Chart(deptCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Cardiology', 'Orthopedics', 'Neurology', 'Pediatrics', 'General'],
                    datasets: [{
                        data: [25, 20, 15, 25, 15],
                        backgroundColor: ['#2563EB', '#22C55E', '#F59E0B', '#EF4444', '#8B5CF6'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        }
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeOutQuart'
                    }
                }
            });
        }

        // Category Distribution Chart
        const categoryCtx = document.getElementById('categoryChart');
        if (categoryCtx) {
            new Chart(categoryCtx, {
                type: 'bar',
                data: {
                    labels: ['Medicines', 'Equipment', 'Consumables', 'Lab Supplies'],
                    datasets: [{
                        label: 'Purchases',
                        data: [45, 25, 20, 10],
                        backgroundColor: ['#2563EB', '#22C55E', '#F59E0B', '#EF4444'],
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            grid: {
                                color: '#E5E7EB'
                            }
                        },
                        y: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeOutQuart'
                    }
                }
            });
        }

        // Patient Registrations Chart
        const registrationCtx = document.getElementById('registrationChart');
        if (registrationCtx) {
            new Chart(registrationCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Registrations',
                        data: [150, 200, 180, 250, 220, 300],
                        borderColor: '#22C55E',
                        backgroundColor: 'rgba(34, 197, 94, 0.1)',
                        fill: true,
                        tension: 0.4,
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: '#E5E7EB'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeOutQuart'
                    }
                }
            });
        }
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initCounters();
            initCharts();
        });
    } else {
        initCounters();
        initCharts();
    }

})();
