/**
 * CineBook Seat Selector
 * Interactive seat selection with real-time availability polling
 */

class SeatSelector {
    constructor(config) {
        this.showId = config.showId;
        this.reserveUrl = config.reserveUrl;
        this.availabilityUrl = config.availabilityUrl;
        this.summaryUrl = config.summaryUrl;
        this.csrfToken = config.csrfToken;
        this.selectedSeats = new Map(); // seat_id -> {row, number, category, price}
        this.seatStatuses = {};
        this.reservationExpiry = null;
        this.countdownInterval = null;
        this.pollingInterval = null;
        this.maxSeats = 10;

        this.init();
    }

    init() {
        this.bindSeatEvents();
        this.startPolling();
        this.updateSummary();
    }

    bindSeatEvents() {
        document.querySelectorAll('.seat.available').forEach(seat => {
            seat.addEventListener('click', (e) => this.toggleSeat(e.currentTarget));
        });
    }

    toggleSeat(seatEl) {
        const seatId = seatEl.dataset.seatId;
        const status = seatEl.dataset.status;

        if (status === 'booked' || status === 'held') return;

        if (this.selectedSeats.has(seatId)) {
            // Deselect
            this.selectedSeats.delete(seatId);
            seatEl.classList.remove('selected');
            seatEl.classList.add('available');
            seatEl.dataset.status = 'available';
        } else {
            // Select
            if (this.selectedSeats.size >= this.maxSeats) {
                showToast(`Maximum ${this.maxSeats} seats allowed`, 'warning');
                return;
            }
            this.selectedSeats.set(seatId, {
                row: seatEl.dataset.row,
                number: seatEl.dataset.number,
                category: seatEl.dataset.category,
                price: parseFloat(seatEl.dataset.price),
                display: seatEl.dataset.display
            });
            seatEl.classList.remove('available');
            seatEl.classList.add('selected');
            seatEl.dataset.status = 'selected';
        }

        this.updateSummary();
    }

    updateSummary() {
        const summaryContainer = document.getElementById('selected-seats-summary');
        const totalEl = document.getElementById('total-amount');
        const proceedBtn = document.getElementById('proceed-btn');
        const seatCountEl = document.getElementById('selected-count');

        if (!summaryContainer) return;

        if (this.selectedSeats.size === 0) {
            summaryContainer.innerHTML = `
                <div class="empty-state" style="padding: var(--space-xl);">
                    <i class="fas fa-hand-pointer empty-icon" style="font-size: 2rem;"></i>
                    <p class="empty-text">Select seats from the map</p>
                </div>
            `;
            if (totalEl) totalEl.textContent = '₹0';
            if (proceedBtn) proceedBtn.disabled = true;
            if (seatCountEl) seatCountEl.textContent = '0';
            return;
        }

        let total = 0;
        let html = '';

        this.selectedSeats.forEach((info, seatId) => {
            total += info.price;
            html += `
                <div class="flex items-center justify-between" style="padding: 8px 0; border-bottom: 1px solid var(--glass-border);">
                    <div>
                        <span style="font-weight: 600;">${info.display}</span>
                        <span class="badge badge-${info.category.toLowerCase() === 'platinum' ? 'primary' : info.category.toLowerCase() === 'gold' ? 'warning' : 'info'}" style="margin-left: 8px; font-size: 0.65rem;">
                            ${info.category}
                        </span>
                    </div>
                    <span style="color: var(--color-text-secondary);">₹${info.price}</span>
                </div>
            `;
        });

        summaryContainer.innerHTML = html;
        if (totalEl) totalEl.textContent = formatCurrency(total);
        if (proceedBtn) proceedBtn.disabled = false;
        if (seatCountEl) seatCountEl.textContent = this.selectedSeats.size.toString();
    }

    async reserveSeats() {
        const seatIds = Array.from(this.selectedSeats.keys());
        if (seatIds.length === 0) {
            showToast('Please select at least one seat', 'warning');
            return;
        }

        const proceedBtn = document.getElementById('proceed-btn');
        if (proceedBtn) {
            proceedBtn.disabled = true;
            proceedBtn.innerHTML = '<span class="spinner" style="width: 20px; height: 20px;"></span> Reserving...';
        }

        try {
            const response = await fetch(this.reserveUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken,
                },
                body: JSON.stringify({ seat_ids: seatIds })
            });

            const data = await response.json();

            if (data.success) {
                showToast('Seats reserved! Complete payment within 2 minutes.', 'success');
                this.reservationExpiry = new Date(data.expires_at);
                this.startCountdown();
                
                // Redirect to booking summary
                setTimeout(() => {
                    window.location.href = data.redirect_url || this.summaryUrl;
                }, 1000);
            } else {
                showToast(data.error || 'Failed to reserve seats', 'error');
                // Refresh seat availability
                this.fetchAvailability();
            }
        } catch (err) {
            showToast('Network error. Please try again.', 'error');
            console.error('Reserve seats error:', err);
        } finally {
            if (proceedBtn) {
                proceedBtn.disabled = false;
                proceedBtn.innerHTML = '<i class="fas fa-arrow-right"></i> Proceed to Payment';
            }
        }
    }

    startCountdown() {
        const timerEl = document.getElementById('countdown-timer');
        if (!timerEl || !this.reservationExpiry) return;

        timerEl.classList.remove('hidden');

        if (this.countdownInterval) clearInterval(this.countdownInterval);

        this.countdownInterval = setInterval(() => {
            const now = new Date();
            const diff = this.reservationExpiry - now;

            if (diff <= 0) {
                clearInterval(this.countdownInterval);
                timerEl.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Reservation expired!';
                timerEl.classList.add('urgent');
                showToast('Your seat reservation has expired. Please select seats again.', 'error');
                this.resetSelection();
                return;
            }

            const minutes = Math.floor(diff / 60000);
            const seconds = Math.floor((diff % 60000) / 1000);
            const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;

            timerEl.innerHTML = `<i class="fas fa-clock"></i> Reservation expires in: <strong>${timeStr}</strong>`;

            if (diff <= 30000) {
                timerEl.classList.add('urgent');
            }
        }, 1000);
    }

    resetSelection() {
        this.selectedSeats.clear();
        document.querySelectorAll('.seat.selected').forEach(seat => {
            seat.classList.remove('selected');
            seat.classList.add('available');
            seat.dataset.status = 'available';
        });
        this.updateSummary();
        this.fetchAvailability();
    }

    async fetchAvailability() {
        try {
            const response = await fetch(this.availabilityUrl, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            const data = await response.json();

            if (data.seats) {
                Object.entries(data.seats).forEach(([seatId, status]) => {
                    const seatEl = document.querySelector(`[data-seat-id="${seatId}"]`);
                    if (!seatEl) return;

                    // Don't override our own selection
                    if (this.selectedSeats.has(seatId)) return;

                    // Update status
                    seatEl.className = `seat ${status}`;
                    seatEl.dataset.status = status;

                    if (status === 'booked' || status === 'held') {
                        seatEl.style.cursor = 'not-allowed';
                    }
                });
            }
        } catch (err) {
            console.error('Availability fetch error:', err);
        }
    }

    startPolling() {
        // Poll every 5 seconds for availability updates
        this.pollingInterval = setInterval(() => this.fetchAvailability(), 5000);
    }

    stopPolling() {
        if (this.pollingInterval) clearInterval(this.pollingInterval);
    }

    destroy() {
        this.stopPolling();
        if (this.countdownInterval) clearInterval(this.countdownInterval);
    }
}

// Clean up on page leave
window.addEventListener('beforeunload', () => {
    if (window.seatSelector) {
        window.seatSelector.destroy();
    }
});
