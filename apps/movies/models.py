from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Genre(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome class e.g. 'fas fa-ghost'")

    def __str__(self):
        return self.name

class Language(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.name

class CastMember(models.Model):
    ROLE_CHOICES = [
        ('actor', 'Actor'),
        ('director', 'Director'),
        ('producer', 'Producer'),
        ('writer', 'Writer'),
    ]
    name = models.CharField(max_length=255)
    role_type = models.CharField(max_length=20, choices=ROLE_CHOICES)
    photo = models.ImageField(upload_to='cast_photos/', blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Movie(models.Model):
    CERTIFICATION_CHOICES = [
        ('U', 'U'),
        ('UA', 'UA'),
        ('A', 'A'),
        ('S', 'S'),
    ]
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField()
    genres = models.ManyToManyField(Genre, related_name='movies')
    languages = models.ManyToManyField(Language, related_name='movies')
    cast = models.ManyToManyField(CastMember, through='MovieCast', related_name='movies')
    duration = models.DurationField(help_text="Duration of the movie")
    release_date = models.DateField()
    age_certification = models.CharField(max_length=2, choices=CERTIFICATION_CHOICES)
    trailer_youtube_id = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['release_date']),
            models.Index(fields=['avg_rating']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active', 'release_date']),
        ]

    def __str__(self):
        return self.title

    @property
    def primary_poster(self):
        poster = self.posters.filter(is_primary=True).first()
        return poster if poster else self.posters.first()

    @property
    def youtube_embed_url(self):
        if self.trailer_youtube_id:
            return f"https://www.youtube-nocookie.com/embed/{self.trailer_youtube_id}"
        return ""

class MovieCast(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    cast_member = models.ForeignKey(CastMember, on_delete=models.CASCADE)
    character_name = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

class MoviePoster(models.Model):
    movie = models.ForeignKey(Movie, related_name='posters', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='movie_posters/')
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.movie.title} Poster"

class Review(models.Model):
    movie = models.ForeignKey(Movie, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_verified = models.BooleanField(default=False)
    is_reported = models.BooleanField(default=False)
    report_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('movie', 'user')
        indexes = [
            models.Index(fields=['movie', '-created_at']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user} - {self.movie.title} ({self.rating}/5)"
