from django.db import models

class Ticket(models.Model):
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='ticket')
    pdf_file = models.FileField(upload_to='tickets/%Y/%m/', blank=True)
    qr_data = models.TextField(help_text='Signed QR code data for verification')
    generated_at = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False)
    email_attempts = models.PositiveIntegerField(default=0)
    last_email_attempt = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'

    def __str__(self):
        return f'Ticket for {self.booking.booking_id}'
