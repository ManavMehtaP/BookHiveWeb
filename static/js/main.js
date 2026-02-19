document.addEventListener('DOMContentLoaded', function() {
    initScrollReveal();
    initNavbar();
    initSearch();
    initEventCards();
    initSmoothScroll();
    initLoader();
    initDropdowns();
    initModalFooterControl();
});

function initModalFooterControl() {
    document.addEventListener('show.bs.modal', function() {
        const footer = document.querySelector('footer');
        if (footer) {
            footer.style.display = 'none';
        }
    });
    
    document.addEventListener('hide.bs.modal', function() {
        const footer = document.querySelector('footer');
        if (footer) {
            footer.style.display = '';
        }
    });
}

function initDropdowns() {
    const dropdownToggles = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    dropdownToggles.forEach(toggle => {
        try {
            new bootstrap.Dropdown(toggle, {
                autoClose: true,
                reference: 'toggle'
            });
        } catch (e) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const dropdownMenu = this.nextElementSibling;
                if (dropdownMenu) {
                    const isShowing = dropdownMenu.classList.contains('show');
                    if (isShowing) {
                        dropdownMenu.classList.remove('show');
                    } else {
                        dropdownMenu.classList.add('show');
                    }
                }
            });
        }
    });
    
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
            openDropdowns.forEach(dropdown => {
                dropdown.classList.remove('show');
            });
        }
    });
}

function initScrollReveal() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, observerOptions);

    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
}

function initNavbar() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

function initSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchWrapper = document.querySelector('.search-wrapper');
    const findSeatsBtn = searchWrapper?.querySelector('button.btn-action');
    
    if (!searchInput) return;

    if (searchWrapper) {
        searchWrapper.addEventListener('click', function(e) {
            if (!e.target.closest('button')) {
                searchInput.focus();
            }
        });
    }

    if (findSeatsBtn) {
        findSeatsBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const searchEvent = new Event('input', { bubbles: true });
            searchInput.dispatchEvent(searchEvent);
            
            setTimeout(() => {
                const eventsSection = document.getElementById('events');
                if (eventsSection) {
                    eventsSection.scrollIntoView({ 
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }, 100);
        });
    }

    searchInput.addEventListener('input', debounce(function(e) {
        const term = e.target.value.toLowerCase().trim();
        const cards = document.querySelectorAll('.event-card');
        let hasResults = false;
        
        cards.forEach(card => {
            const location = card.querySelector('.card-info-line span')?.textContent.toLowerCase() || '';
            const date = card.querySelectorAll('.card-info-line span')[1]?.textContent.toLowerCase() || '';
            const description = card.querySelector('.card-description')?.textContent.toLowerCase() || '';
            const imageAlt = card.querySelector('img')?.alt.toLowerCase() || '';
            
            const parentDiv = card.closest('.event-item');
            const genre = parentDiv?.dataset.genre?.toLowerCase() || '';
            
            const searchableText = `${location} ${date} ${description} ${imageAlt} ${genre}`;
            
            const searchTerms = term.split(' ').filter(t => t.length > 0);
            let matches = false;
            
            if (searchTerms.length === 0) {
                matches = true;
            } else {
                matches = searchTerms.every(searchTerm => 
                    searchableText.includes(searchTerm)
                );
            }
            
            if (matches) {
                card.closest('.col-lg-4').style.display = 'block';
                hasResults = true;
            } else {
                card.closest('.col-lg-4').style.display = 'none';
            }
        });
        
        const noResults = document.getElementById('noResults');
        if (!noResults && !hasResults && term.length > 0) {
            const grid = document.getElementById('eventsGrid');
            const message = document.createElement('div');
            message.id = 'noResults';
            message.className = 'col-12 text-center py-5';
            message.innerHTML = `
                <div class="mb-4">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h4 class="mb-3">No events found</h4>
                    <p class="text-muted">Try adjusting your search or filter to find what you're looking for.</p>
                </div>
            `;
            grid.appendChild(message);
        } else if (noResults && hasResults) {
            noResults.remove();
        } else if (noResults && term.length === 0) {
            noResults.remove();
        }
        
        if (term.length === 0) {
            cards.forEach(card => {
                card.closest('.col-lg-4').style.display = 'block';
            });
        }
    }, 300));
}

function initEventCards() {
    const eventCards = document.querySelectorAll('.event-card');
    
    eventCards.forEach(card => {
        card.addEventListener('click', function(e) {
            if (e.target.closest('a, button, .btn-circle')) {
                return;
            }
            
            const eventId = this.querySelector('.btn-circle')?.dataset.eventId;
            if (eventId) {
                // Viewing event
            }
        });
        
        card.addEventListener('touchstart', function() {
            this.classList.add('hover');
        }, { passive: true });
    });
    
    document.querySelectorAll('.btn-circle').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const eventId = this.dataset.eventId;
            // View details for event
        });
    });
}

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                
                window.scrollTo({
                    top: target.offsetTop - 80,
                    behavior: 'smooth'
                });
                
                history.pushState(null, null, targetId);
            }
        });
    });
}

function initLoader() {
    const loader = document.getElementById('loader');
    if (!loader) return;
    
    window.addEventListener('load', function() {
        setTimeout(() => {
            loader.classList.add('fade-out');
            
            setTimeout(() => {
                loader.remove();
            }, 500);
        }, 500);
    });
    
    setTimeout(() => {
        if (document.readyState === 'complete' && loader) {
            loader.classList.add('fade-out');
            setTimeout(() => loader.remove(), 500);
        }
    }, 5000);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

window.BookHive = {
    initScrollReveal,
    initNavbar,
    initSearch,
    initEventCards,
    initSmoothScroll,
    initLoader,
    debounce
};
