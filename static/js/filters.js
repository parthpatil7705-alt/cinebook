/**
 * CineBook Movie Filters
 * Dynamic filtering with HTMX integration
 */

class MovieFilters {
    constructor(config) {
        this.filterForm = document.getElementById(config.formId || 'filter-form');
        this.resultsContainer = document.getElementById(config.resultsId || 'movie-results');
        this.countBadge = document.getElementById(config.countId || 'results-count');
        this.activeFiltersContainer = document.getElementById(config.activeFiltersId || 'active-filters');
        this.baseUrl = config.baseUrl || '/movies/';

        if (this.filterForm) {
            this.init();
        }
    }

    init() {
        // Bind change events to all filter inputs
        this.filterForm.querySelectorAll('input, select').forEach(input => {
            input.addEventListener('change', () => this.applyFilters());
        });

        // Bind sort dropdown
        const sortSelect = document.getElementById('sort-select');
        if (sortSelect) {
            sortSelect.addEventListener('change', () => this.applyFilters());
        }

        // Display active filters on load
        this.updateActiveFilters();
    }

    getFilterParams() {
        const formData = new FormData(this.filterForm);
        const params = new URLSearchParams();

        for (const [key, value] of formData.entries()) {
            if (value && value.trim()) {
                params.append(key, value.trim());
            }
        }

        // Add sort
        const sortSelect = document.getElementById('sort-select');
        if (sortSelect && sortSelect.value) {
            params.set('sort', sortSelect.value);
        }

        return params;
    }

    applyFilters() {
        const params = this.getFilterParams();
        const url = `${this.baseUrl}?${params.toString()}`;

        // Update URL without reload
        window.history.replaceState({}, '', url);

        // HTMX request for partial update
        if (this.resultsContainer) {
            htmx.ajax('GET', url, {
                target: '#movie-results',
                swap: 'innerHTML',
                headers: { 'HX-Request': 'true' },
            });
        }

        this.updateActiveFilters();
    }

    updateActiveFilters() {
        if (!this.activeFiltersContainer) return;

        const params = this.getFilterParams();
        let html = '';
        const filterLabels = {
            'genre': 'Genre',
            'language': 'Language',
            'city': 'City',
            'min_rating': 'Min Rating',
            'q': 'Search',
            'sort': 'Sort',
        };

        for (const [key, value] of params.entries()) {
            if (key === 'page') continue;
            const label = filterLabels[key] || key;

            // Get display value for selects
            let displayValue = value;
            const selectEl = this.filterForm.querySelector(`[name="${key}"]`);
            if (selectEl && selectEl.tagName === 'SELECT') {
                const option = selectEl.querySelector(`option[value="${value}"]`);
                if (option) displayValue = option.textContent;
            }
            // For checkboxes, get the label
            if (selectEl && selectEl.type === 'checkbox') {
                const labelEl = selectEl.closest('label') || document.querySelector(`label[for="${selectEl.id}"]`);
                if (labelEl) displayValue = labelEl.textContent.trim();
            }

            html += `
                <span class="badge badge-primary" style="cursor: pointer; padding: 6px 12px;" onclick="movieFilters.removeFilter('${key}', '${value}')">
                    ${label}: ${displayValue}
                    <i class="fas fa-times" style="margin-left: 4px; font-size: 0.65rem;"></i>
                </span>
            `;
        }

        if (html) {
            html += `<button class="btn btn-ghost btn-sm" onclick="movieFilters.clearAll()">Clear All</button>`;
        }

        this.activeFiltersContainer.innerHTML = html;
    }

    removeFilter(key, value) {
        const input = this.filterForm.querySelector(`[name="${key}"][value="${value}"]`);
        if (input) {
            if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = false;
            } else {
                input.value = '';
            }
        }

        // Handle sort separately
        if (key === 'sort') {
            const sortSelect = document.getElementById('sort-select');
            if (sortSelect) sortSelect.value = '';
        }

        this.applyFilters();
    }

    clearAll() {
        this.filterForm.reset();
        const sortSelect = document.getElementById('sort-select');
        if (sortSelect) sortSelect.value = '';
        this.applyFilters();
    }
}
