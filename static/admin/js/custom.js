/* custom.js - Premium SaaS Enterprise Admin Panel Scripting */

document.addEventListener('DOMContentLoaded', function() {
    // 1. Initialize Lucide Icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // 2. Dark/Light Theme System
    const themeToggleBtn = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function() {
            let theme = document.documentElement.getAttribute('data-theme');
            let newTheme = theme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
            if (window.renderDonationCharts) {
                window.renderDonationCharts();
            }
        });
    }

    function updateThemeIcon(theme) {
        const icon = document.getElementById('theme-toggle-icon');
        if (!icon) return;
        if (theme === 'dark') {
            icon.innerHTML = '<i data-lucide="sun" style="width: 20px; height: 20px;"></i>';
        } else {
            icon.innerHTML = '<i data-lucide="moon" style="width: 20px; height: 20px;"></i>';
        }
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    // 3. Sidebar Collapsible Desktop & Mobile Drawer toggles
    const toggleSidebarBtn = document.getElementById('toggle-sidebar');
    const sidebar = document.getElementById('sidebar');

    if (toggleSidebarBtn && sidebar) {
        toggleSidebarBtn.addEventListener('click', function() {
            if (window.innerWidth > 768) {
                sidebar.classList.toggle('collapsed');
                localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));
            } else {
                sidebar.classList.toggle('open');
            }
        });
    }

    // Restore desktop sidebar collapsed state
    if (window.innerWidth > 768 && sidebar) {
        const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
        if (isCollapsed) {
            sidebar.classList.add('collapsed');
        }
    }

    // 4. Nested Menu Accordions
    const sidebarLinks = document.querySelectorAll('.sidebar-link[data-toggle="submenu"]');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const submenu = this.nextElementSibling;
            if (submenu) {
                submenu.classList.toggle('active');
                const icon = this.querySelector('.submenu-arrow');
                if (icon) {
                    icon.style.transform = submenu.classList.contains('active') ? 'rotate(90deg)' : 'rotate(0deg)';
                }
            }
        });
    });

    // 5. Stat Counter Increment Animation
    const counterElements = document.querySelectorAll('.stat-value[data-target]');
    counterElements.forEach(counter => {
        const target = parseFloat(counter.getAttribute('data-target').replace(/,/g, ''));
        const prefix = counter.getAttribute('data-prefix') || '';
        let start = 0;
        const duration = 1200; // ms
        const stepTime = 20; // ms
        const steps = duration / stepTime;
        const increment = target / steps;
        
        const timer = setInterval(() => {
            start += increment;
            if (start >= target) {
                clearInterval(timer);
                counter.innerText = prefix + target.toLocaleString(undefined, { minimumFractionDigits: target % 1 === 0 ? 0 : 2 });
            } else {
                counter.innerText = prefix + Math.floor(start).toLocaleString();
            }
        }, stepTime);
    });

    // 6. Keyboard Shortcut for the global admin search
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
            const searchInput = document.querySelector('.global-search input');
            if (searchInput) {
                e.preventDefault();
                searchInput.focus();
                searchInput.select();
            }
        }
    });

    // 7. User Profile Dropdown toggles
    const userDropdownTrigger = document.getElementById('user-dropdown-trigger');
    const userDropdownMenu = document.getElementById('user-dropdown-menu');

    if (userDropdownTrigger && userDropdownMenu) {
        userDropdownTrigger.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdownMenu.classList.toggle('active');
        });
        document.addEventListener('click', function() {
            userDropdownMenu.classList.remove('active');
        });
    }

    // 7. Dynamic Mini Sparkline and Charts Integration
    if (document.getElementById('donationsLineChart')) {
        loadChartJsAndInitialize();
    }
});

function loadChartJsAndInitialize() {
    if (typeof Chart === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
        script.onload = renderEnterpriseCharts;
        document.head.appendChild(script);
    } else {
        renderEnterpriseCharts();
    }
}

function renderEnterpriseCharts() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#94a3b8' : '#475569';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';

    // Multi-axis line chart for Donation Revenue & Volume Trends
    const lineCtx = document.getElementById('donationsLineChart').getContext('2d');
    if (window.donationLineChartInstance) {
        window.donationLineChartInstance.destroy();
    }
    
    // Gradient fill setup
    const gradient = lineCtx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(37, 99, 235, 0.25)');
    gradient.addColorStop(1, 'rgba(37, 99, 235, 0.00)');

    window.donationLineChartInstance = new Chart(lineCtx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
            datasets: [{
                label: 'Revenue Trend',
                data: [3500, 5200, 4800, 7200, 6900, 8800, 11500],
                borderColor: '#2563eb',
                backgroundColor: gradient,
                tension: 0.4,
                fill: true,
                borderWidth: 3,
                pointBackgroundColor: '#2563eb',
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: gridColor },
                    ticks: { color: textColor, font: { family: 'Plus Jakarta Sans' } }
                },
                y: {
                    grid: { color: gridColor },
                    ticks: { color: textColor, font: { family: 'Plus Jakarta Sans' } }
                }
            }
        }
    });

    // Doughnut breakdown for providers
    const pieCtx = document.getElementById('providerPieChart').getContext('2d');
    if (window.providerPieChartInstance) {
        window.providerPieChartInstance.destroy();
    }
    window.providerPieChartInstance = new Chart(pieCtx, {
        type: 'doughnut',
        data: {
            labels: ['Mpesa', 'TigoPesa', 'AirtelMoney', 'Halopesa'],
            datasets: [{
                data: [48, 24, 18, 10],
                backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 0,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: textColor, font: { family: 'Plus Jakarta Sans', size: 12 } }
                }
            }
        }
    });
}

// Bind chart logic globally
window.renderDonationCharts = renderEnterpriseCharts;
