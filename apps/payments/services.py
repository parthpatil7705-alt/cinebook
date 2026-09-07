import razorpay
from django.conf import settings
from django.db import transaction
from decimal import Decimal
from .models import Payment

class RazorpayService:
    def __init__(self):
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    def create_order(self, booking):
        """Create Razorpay order. Returns order data dict with id, amount, currency, key_id."""
        amount_paise = int(booking.total_amount * 100)
        order_data = self.client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'receipt': str(booking.booking_id),
            'notes': {'booking_id': str(booking.booking_id), 'user_id': str(booking.user_id)}
        })
        # Create Payment record
        Payment.objects.create(
            booking=booking,
            razorpay_order_id=order_data['id'],
            amount=booking.total_amount,
        )
        return {
            'order_id': order_data['id'],
            'amount': amount_paise,
            'currency': 'INR',
            'key_id': settings.RAZORPAY_KEY_ID,
            'booking_id': str(booking.booking_id),
            'name': 'CineBook',
            'description': f'Booking {booking.booking_id}',
        }

    def verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """Verify payment signature. Returns True/False."""
        try:
            self.client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            })
            return True
        except razorpay.errors.SignatureVerificationError:
            return False

    def process_refund(self, payment, amount=None):
        """Issue refund. amount in Decimal or None for full refund."""
        refund_amount = int((amount or payment.amount) * 100)
        refund = self.client.payment.refund(payment.razorpay_payment_id, refund_amount)
        payment.status = 'refunded'
        payment.save(update_fields=['status', 'updated_at'])
        return refund

    def verify_webhook_signature(self, body, signature):
        """Verify webhook signature."""
        try:
            self.client.utility.verify_webhook_signature(body, signature, settings.RAZORPAY_WEBHOOK_SECRET)
            return True
        except razorpay.errors.SignatureVerificationError:
            return False
