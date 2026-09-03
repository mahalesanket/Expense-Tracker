document.addEventListener('DOMContentLoaded', () => {
    // Theme Toggle Routine
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.body.getAttribute('data-theme');
            const targetTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.body.setAttribute('data-theme', targetTheme);
            localStorage.setItem('theme', targetTheme);
        });
        
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.body.setAttribute('data-theme', savedTheme);
    }

    // Global Event Listener for Modal Backdrop Clicking
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-overlay')) {
            e.target.classList.remove('active');
        }
    });

    // Keyboard Shortcuts (Close modal on Escape)
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal-overlay.active');
            if (activeModal) activeModal.classList.remove('active');
        }
    });
});

// Modal Control System
function openModal(id) {
    const targetModal = document.getElementById(id);
    if (targetModal) {
        targetModal.classList.add('active');
    }
}

function closeModal(id) {
    const targetModal = document.getElementById(id);
    if (targetModal) {
        targetModal.classList.remove('active');
    }
}

function filterSidebarNav() {
    const queryInput = document.getElementById('sidebarSearchInput');
    if (!queryInput) return;
    
    const query = queryInput.value.toLowerCase();
    const navItems = document.querySelectorAll('#sidebarNav .nav-item');

    navItems.forEach(item => {
        const labelEl = item.querySelector('.nav-label');
        if (labelEl) {
            const label = labelEl.textContent.toLowerCase();
            if (label.includes(query)) {
                item.style.display = 'flex';
                item.style.opacity = '1';
            } else {
                item.style.display = 'none';
                item.style.opacity = '0';
            }
        }
    });
}