document.addEventListener('DOMContentLoaded', () => {
    // 1. Dark and Light Mode Toggle Logic
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const htmlElement = document.documentElement;

    // Check previously saved theme in localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        htmlElement.setAttribute('data-bs-theme', savedTheme);
        if (savedTheme === 'dark' && themeIcon) {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        }
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            htmlElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);

            if (themeIcon) {
                if (newTheme === 'dark') {
                    themeIcon.classList.remove('fa-moon');
                    themeIcon.classList.add('fa-sun');
                } else {
                    themeIcon.classList.remove('fa-sun');
                    themeIcon.classList.add('fa-moon');
                }
            }
        });
    }

    // 2. Screen Timeout Auto-Submit Feature during Exam
    document.addEventListener("visibilitychange", () => {
        if (document.hidden && window.location.pathname.includes('/student')) {
            console.log("Screen minimized or turned off during exam!");
            // ተጨማሪ አውቶ-ሰሚት ኮድ ማስገባት ከፈለጉ እዚህ ጋር ይጨመራል
        }
    });
});