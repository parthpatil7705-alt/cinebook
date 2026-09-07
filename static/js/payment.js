/**
 * CineBook Payment Integration
 * Razorpay Checkout.js integration with retry support
 */

class CineBookPayment {
    constructor(config) {
        this.bookingId = config.bookingId;
        this.initiateUrl = config.initiateUrl;
        this.callbackUrl = config.callbackUrl;
        this.retryUrl = config.retryUrl;
        this.successRedirect = config.successRedirect;
        this.csrfToken = config.csrfToken;
        this.userName = config.userName || '';
        this.userEmail = config.userEmail || '';
        this.userPhone = config.userPhone || '';
    }

    async initiatePayment() {
        const payBtn = document.getElementById('pay-btn');
        if (payBtn) {
            payBtn.disabled = true;
            payBtn.innerHTML = '<span class="spinner" style="width: 20px; height: 20px;"></span> Initiating...';
        }

        try {
            const response = await fetch(this.initiateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken,
                },
            });

            const data = await response.json();

            if (data.error) {
                showToast(data.error, 'error');
                return;
            }

            this.openRazorpayCheckout(data);
        } catch (err) {
            showToast('Failed to initiate payment. Please try again.', 'error');
            console.error('Payment initiation error:', err);
        } finally {
            if (payBtn) {
                payBtn.disabled = false;
                payBtn.innerHTML = '<i class="fas fa-lock"></i> Pay Securely';
            }
        }
    }

    openRazorpayCheckout(orderData) {
        const options = {
            key: orderData.key_id,
            amount: orderData.amount,
            currency: orderData.currency,
            name: orderData.name || 'CineBook',
            description: orderData.description || `Booking ${this.bookingId}`,
            order_id: orderData.order_id,
            prefill: {
                name: this.userName,
                email: this.userEmail,
                contact: this.userPhone,
            },
            theme: {
                color: '#6366f1',
                backdrop_color: 'rgba(10, 14, 26, 0.85)',
            },
            modal: {
                ondismiss: () => {
                    showToast('Payment cancelled. Your seats are still reserved.', 'warning');
                },
                confirm_close: true,
                animation: true,
            },
            handler: (response) => this.handlePaymentSuccess(response),
        };

        try {
            const rzp = new Razorpay(options);
            rzp.on('payment.failed', (response) => this.handlePaymentFailure(response));
            rzp.open();
        } catch (err) {
            showToast('Error loading payment gateway. Please try again.', 'error');
            console.error('Razorpay open error:', err);
        }
    }

    async handlePaymentSuccess(response) {
        const overlay = document.getElementById('payment-processing-overlay');
        if (overlay) overlay.classList.add('active');

        try {
            const callbackResponse = await fetch(this.callbackUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken,
                },
                body: JSON.stringify({
                    razorpay_order_id: response.razorpay_order_id,
                    razorpay_payment_id: response.razorpay_payment_id,
                    razorpay_signature: response.razorpay_signature,
                }),
            });

            const data = await callbackResponse.json();

            if (data.success) {
                showToast('Payment successful! Your booking is confirmed.', 'success');
                setTimeout(() => {
                    window.location.href = data.redirect_url || this.successRedirect;
                }, 1500);
            } else {
                showToast(data.error || 'Payment verification failed.', 'error');
                if (overlay) overlay.classList.remove('active');
            }
        } catch (err) {
            showToast('Error verifying payment. Please check your bookings.', 'error');
            console.error('Payment callback error:', err);
            if (overlay) overlay.classList.remove('active');
        }
    }

    handlePaymentFailure(response) {
        const errorDesc = response.error?.description || 'Payment failed';
        const errorCode = response.error?.code || '';
        
        showToast(`Payment failed: ${errorDesc}`, 'error');
        console.error('Payment failed:', response.error);

        // Show retry button
        const retryContainer = document.getElementById('retry-container');
        if (retryContainer) {
            retryContainer.classList.remove('hidden');
            retryContainer.innerHTML = `
                <div class="card" style="padding: var(--space-xl); text-align: center; border-color: var(--color-danger);">
                    <i class="fas fa-exclamation-circle" style="font-size: 2.5rem; color: var(--color-danger); margin-bottom: var(--space-md);"></i>
                    <h3 style="margin-bottom: var(--space-sm);">Payment Failed</h3>
                    <p style="color: var(--color-text-secondary); margin-bottom: var(--space-lg);">${errorDesc} ${errorCode ? `(${errorCode})` : ''}</p>
                    <button class="btn btn-primary btn-lg" onclick="window.cineBookPayment.retryPayment()">
                        <i class="fas fa-redo"></i> Retry Payment
                    </button>
                </div>
            `;
        }
    }

    async retryPayment() {
        try {
            const response = await fetch(this.retryUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken,
                },
            });

            const data = await response.json();

            if (data.error) {
                showToast(data.error, 'error');
                return;
            }

            this.openRazorpayCheckout(data);
        } catch (err) {
            showToast('Failed to retry payment. Please try again.', 'error');
            console.error('Payment retry error:', err);
        }
    }
}
