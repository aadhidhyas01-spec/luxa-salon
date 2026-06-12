// Global interactions for Salon Lux

document.addEventListener('DOMContentLoaded', () => {
    console.log('Salon Lux: Luxury Finder initialized.');

    // Custom UI Micro-animations: Add scroll-shadow class to navbar on scroll
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 5px 20px rgba(0, 0, 0, 0.4)';
            navbar.style.borderBottomColor = 'var(--primary)';
        } else {
            navbar.style.boxShadow = 'none';
            navbar.style.borderBottomColor = 'var(--border-light)';
        }
    });
});
