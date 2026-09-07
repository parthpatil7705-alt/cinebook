from django.db import models
from django.urls import reverse
from django.utils import timezone

class City(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    state = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Theater(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='theaters')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='theaters/', blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['city', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.city.name}"

class Screen(models.Model):
    SCREEN_TYPES = [
        ('standard', 'Standard'),
        ('imax', 'IMAX'),
        ('4dx', '4DX'),
        ('dolby', 'Dolby Cinema'),
    ]
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='screens')
    name = models.CharField(max_length=50)
    screen_type = models.CharField(max_length=20, choices=SCREEN_TYPES, default='standard')
    total_seats = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.theater.name} - {self.name}"

class SeatCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color_code = models.CharField(max_length=7, default='#FFFFFF')
    price_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)

    def __str__(self):
        return self.name

class Seat(models.Model):
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='seats')
    category = models.ForeignKey(SeatCategory, on_delete=models.SET_NULL, null=True)
    row_label = models.CharField(max_length=5)
    seat_number = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('screen', 'row_label', 'seat_number')
        ordering = ['row_label', 'seat_number']

    @property
    def display_name(self):
        return f"{self.row_label}-{self.seat_number}"

    def __str__(self):
        return f"{self.screen.name} - {self.display_name}"

class Show(models.Model):
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE, related_name='shows')
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='shows')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    is_cancelled = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['movie', 'start_time']),
            models.Index(fields=['screen', 'start_time']),
            models.Index(fields=['start_time']),
            models.Index(fields=['is_active', 'start_time']),
        ]

    @property
    def is_past(self):
        return self.start_time < timezone.now()

    @property
    def is_housefull(self):
        return self.available_seats_count() == 0

    def available_seats_count(self):
        from apps.bookings.services import BookingService
        availability = BookingService.get_seat_availability(self)
        return sum(1 for status in availability.values() if status == 'available')

    def __str__(self):
        return f"{self.movie.title} - {self.screen.theater.name} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"

class ShowSeatPrice(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='seat_prices')
    category = models.ForeignKey(SeatCategory, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ('show', 'category')

    def __str__(self):
        return f"{self.show} - {self.category.name}: {self.price}"
