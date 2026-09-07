from django.db import models
from django.conf import settings
from django.utils import timezone
import random
import string

class SeatReservation(models.Model):
    STATUS_CHOICES = [
        ('held', 'Held'),
        ('confirmed', 'Confirmed'),
        ('expired', 'Expired'),
        ('released', 'Released'),
    ]
    show = models.ForeignKey('theaters.Show', on_delete=models.CASCADE, related_name='reservations')
    seat = models.ForeignKey('theaters.Seat', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reserved_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='held')

    class Meta:
        indexes = [
            models.Index(fields=['show', 'seat', 'status']),
            models.Index(fields=['expires_at', 'status']),
            models.Index(fields=['user', 'status']),
        ]

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def release(self):
        self.status = 'released'
        self.save(update_fields=['status'])

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    show = models.ForeignKey('theaters.Show', on_delete=models.CASCADE, related_name='bookings')
    seats = models.ManyToManyField('theaters.Seat', through='BookedSeat')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    booking_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    booking_id = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['booking_id']),
            models.Index(fields=['status']),
            models.Index(fields=['show']),
            models.Index(fields=['status', 'confirmed_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = self.generate_booking_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_booking_id():
        return f"CB-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"

    @property
    def total_seats_count(self):
        return self.seats.count()

    @property
    def seats_display(self):
        return ", ".join([bs.seat.display_name for bs in self.booked_seats.all()])

class BookedSeat(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booked_seats')
    seat = models.ForeignKey('theaters.Seat', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
