/**
 * CineBook Dashboard Charts
 * Chart.js initialization for analytics dashboard
 */

class DashboardCharts {
    constructor() {
        this.chartInstances = {};
        this.brandColors = {
            primary: '#6366f1',
            primaryLight: '#818cf8',
            purple: '#8b5cf6',
            purpleLight: '#a78bfa',
            success: '#10b981',
            warning: '#f59e0b',
            danger: '#ef4444',
            info: '#3b82f6',
            text: '#94a3b8',
            textMuted: '#64748b',
            grid: 'rgba(148, 163, 184, 0.1)',
        };
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: this.brandColors.text,
                        font: { family: 'Inter', size: 12 },
                        padding: 16,
                    },
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleColor: '#f8fafc',
                    bodyColor: '#94a3b8',
                    borderColor: 'rgba(148, 163, 184, 0.2)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                    titleFont: { family: 'Inter', weight: '600' },
                    bodyFont: { family: 'Inter' },
                },
            },
            scales: {
                x: {
                    grid: { color: this.brandColors.grid },
                    ticks: { color: this.brandColors.text, font: { family: 'Inter', size: 11 } },
                },
                y: {
                    grid: { color: this.brandColors.grid },
                    ticks: { color: this.brandColors.text, font: { family: 'Inter', size: 11 } },
                },
            },
        };
    }

    initRevenueChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !data) return;

        this.chartInstances.revenue = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Revenue (₹)',
                    data: data.values,
                    borderColor: this.brandColors.primary,
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: this.brandColors.primary,
                    pointBorderColor: '#0f172a',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                }],
            },
            options: {
                ...this.defaultOptions,
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        ticks: {
                            ...this.defaultOptions.scales.y.ticks,
                            callback: (value) => '₹' + (value >= 1000 ? (value / 1000).toFixed(0) + 'K' : value),
                        },
                    },
                },
            },
        });
    }

    initBookingTrendsChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !data) return;

        this.chartInstances.bookingTrends = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Bookings',
                    data: data.values,
                    backgroundColor: 'rgba(139, 92, 246, 0.6)',
                    borderColor: this.brandColors.purple,
                    borderWidth: 1,
                    borderRadius: 6,
                    maxBarThickness: 40,
                }],
            },
            options: this.defaultOptions,
        });
    }

    initTopMoviesChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !data) return;

        this.chartInstances.topMovies = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Bookings',
                    data: data.values,
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.7)',
                        'rgba(139, 92, 246, 0.7)',
                        'rgba(59, 130, 246, 0.7)',
                        'rgba(16, 185, 129, 0.7)',
                        'rgba(245, 158, 11, 0.7)',
                        'rgba(239, 68, 68, 0.7)',
                        'rgba(168, 85, 247, 0.7)',
                        'rgba(20, 184, 166, 0.7)',
                        'rgba(249, 115, 22, 0.7)',
                        'rgba(236, 72, 153, 0.7)',
                    ],
                    borderRadius: 6,
                    maxBarThickness: 30,
                }],
            },
            options: {
                ...this.defaultOptions,
                indexAxis: 'y',
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: { display: false },
                },
            },
        });
    }

    initOccupancyChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !data) return;

        this.chartInstances.occupancy = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.8)',
                        'rgba(139, 92, 246, 0.8)',
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                    ],
                    borderColor: '#0f172a',
                    borderWidth: 3,
                    hoverOffset: 8,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: this.brandColors.text,
                            font: { family: 'Inter', size: 11 },
                            padding: 12,
                            usePointStyle: true,
                            pointStyleWidth: 10,
                        },
                    },
                    tooltip: this.defaultOptions.plugins.tooltip,
                },
            },
        });
    }

    initPeakHoursChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !data) return;

        const colors = data.values.map(val => {
            const max = Math.max(...data.values);
            const intensity = val / max;
            if (intensity > 0.75) return 'rgba(239, 68, 68, 0.8)';
            if (intensity > 0.5) return 'rgba(245, 158, 11, 0.8)';
            if (intensity > 0.25) return 'rgba(99, 102, 241, 0.6)';
            return 'rgba(99, 102, 241, 0.3)';
        });

        this.chartInstances.peakHours = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Bookings',
                    data: data.values,
                    backgroundColor: colors,
                    borderRadius: 4,
                    maxBarThickness: 24,
                }],
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: { display: false },
                },
            },
        });
    }

    initUserGrowthChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !data) return;

        this.chartInstances.userGrowth = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'New Users',
                    data: data.values,
                    borderColor: this.brandColors.success,
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                }],
            },
            options: this.defaultOptions,
        });
    }

    destroyAll() {
        Object.values(this.chartInstances).forEach(chart => chart?.destroy());
        this.chartInstances = {};
    }
}
