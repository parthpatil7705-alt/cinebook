import os
import json

base_dir = r"C:\Users\parth\.gemini\antigravity\scratch\cinebook"

accounts_models = '''from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    city = models.ForeignKey('theaters.City', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    total_bookings = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.get_full_name() or self.username
'''

accounts_forms = '''from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'city', 'avatar', 'date_of_birth')

class LoginForm(AuthenticationForm):
    pass
'''

accounts_views = '''from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView, UpdateView, ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, UserProfileForm, LoginForm
from apps.bookings.models import Booking  # Assuming Booking is in bookings app

class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('movies:home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Recent bookings (last 5)
        try:
            context['recent_bookings'] = Booking.objects.filter(user=self.request.user).order_by('-created_at')[:5]
        except Exception:
            context['recent_bookings'] = []
        return context

class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/profile_edit.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

class BookingHistoryView(LoginRequiredMixin, ListView):
    template_name = 'accounts/booking_history.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        try:
            return Booking.objects.filter(user=self.request.user).order_by('-created_at')
        except Exception:
            return []

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    
    def get_success_url(self):
        return super().get_success_url()

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')
'''

accounts_urls = '''from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('bookings/', views.BookingHistoryView.as_view(), name='bookings'),
]
'''

accounts_admin = '''from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'city', 'avatar', 'date_of_birth', 'total_bookings')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
'''

accounts_apps = '''from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    label = 'accounts'
'''

accounts_login_html = '''{% extends 'base.html' %}
{% load widget_tweaks %}

{% block title %}Login - CineBook{% endblock %}

{% block content %}
<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-slate-900">
    <div class="max-w-md w-full space-y-8 bg-slate-800/50 backdrop-blur-md p-8 rounded-2xl shadow-xl border border-slate-700">
        <div>
            <h2 class="mt-6 text-center text-3xl font-extrabold text-slate-100">Sign in to your account</h2>
        </div>
        <form class="mt-8 space-y-6" action="" method="POST">
            {% csrf_token %}
            <div class="rounded-md shadow-sm space-y-4">
                {% for field in form %}
                <div>
                    <label for="{{ field.id_for_label }}" class="sr-only">{{ field.label }}</label>
                    {% render_field field class="appearance-none rounded-lg relative block w-full px-3 py-2 border border-slate-600 placeholder-slate-400 text-slate-100 bg-slate-700 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm" placeholder=field.label %}
                    {% if field.errors %}
                        <p class="text-red-500 text-xs mt-1">{{ field.errors.0 }}</p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            <div>
                <button type="submit" class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 focus:ring-offset-slate-900 transition-all duration-200">
                    Sign in
                </button>
            </div>
            <div class="text-center text-sm text-slate-400">
                Don't have an account? <a href="{% url 'accounts:register' %}" class="font-medium text-indigo-400 hover:text-indigo-300">Sign up here</a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
'''

accounts_register_html = '''{% extends 'base.html' %}
{% load widget_tweaks %}

{% block title %}Register - CineBook{% endblock %}

{% block content %}
<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-slate-900">
    <div class="max-w-md w-full space-y-8 bg-slate-800/50 backdrop-blur-md p-8 rounded-2xl shadow-xl border border-slate-700">
        <div>
            <h2 class="mt-6 text-center text-3xl font-extrabold text-slate-100">Create an account</h2>
        </div>
        <form class="mt-8 space-y-6" action="" method="POST">
            {% csrf_token %}
            <div class="rounded-md shadow-sm space-y-4">
                {% for field in form %}
                <div>
                    <label for="{{ field.id_for_label }}" class="block text-sm font-medium text-slate-300 mb-1">{{ field.label }}</label>
                    {% render_field field class="appearance-none rounded-lg relative block w-full px-3 py-2 border border-slate-600 placeholder-slate-400 text-slate-100 bg-slate-700 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm" placeholder=field.label %}
                    {% if field.errors %}
                        <p class="text-red-500 text-xs mt-1">{{ field.errors.0 }}</p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            <div>
                <button type="submit" class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 focus:ring-offset-slate-900 transition-all duration-200">
                    Register
                </button>
            </div>
            <div class="text-center text-sm text-slate-400">
                Already have an account? <a href="{% url 'accounts:login' %}" class="font-medium text-indigo-400 hover:text-indigo-300">Sign in here</a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
'''

accounts_profile_html = '''{% extends 'base.html' %}

{% block title %}Profile - CineBook{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
    <div class="bg-slate-800/50 backdrop-blur-md rounded-2xl p-8 border border-slate-700">
        <div class="flex items-center space-x-6">
            {% if user.avatar %}
                <img src="{{ user.avatar.url }}" alt="Avatar" class="h-24 w-24 rounded-full border-2 border-indigo-500 object-cover">
            {% else %}
                <div class="h-24 w-24 rounded-full border-2 border-indigo-500 bg-slate-700 flex items-center justify-center text-2xl font-bold text-slate-300">
                    {{ user.username|make_list|first|upper }}
                </div>
            {% endif %}
            <div>
                <h2 class="text-3xl font-bold text-slate-100">{{ user.get_full_name|default:user.username }}</h2>
                <p class="text-slate-400">{{ user.email }}</p>
                <div class="mt-2 flex space-x-4 text-sm text-slate-300">
                    <span><i class="fas fa-phone mr-2"></i>{{ user.phone|default:"N/A" }}</span>
                    <span><i class="fas fa-map-marker-alt mr-2"></i>{{ user.city|default:"No City" }}</span>
                </div>
            </div>
            <div class="ml-auto">
                <a href="{% url 'accounts:profile_edit' %}" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors">Edit Profile</a>
            </div>
        </div>

        <div class="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-slate-700/50 p-6 rounded-xl border border-slate-600 text-center">
                <p class="text-sm text-slate-400 uppercase tracking-wider">Total Bookings</p>
                <p class="text-3xl font-bold text-amber-500 mt-2">{{ user.total_bookings }}</p>
            </div>
            <div class="bg-slate-700/50 p-6 rounded-xl border border-slate-600 text-center">
                <p class="text-sm text-slate-400 uppercase tracking-wider">Member Since</p>
                <p class="text-xl font-bold text-slate-100 mt-2">{{ user.date_joined|date:"M Y" }}</p>
            </div>
        </div>

        <div class="mt-12">
            <div class="flex items-center justify-between mb-6">
                <h3 class="text-2xl font-bold text-slate-100">Recent Bookings</h3>
                <a href="{% url 'accounts:bookings' %}" class="text-indigo-400 hover:text-indigo-300 text-sm font-medium">View All &rarr;</a>
            </div>
            <div class="space-y-4">
                {% for booking in recent_bookings %}
                <div class="bg-slate-700/30 p-4 rounded-lg flex items-center justify-between border border-slate-600">
                    <div>
                        <h4 class="font-bold text-slate-100">{{ booking.show.movie.title }}</h4>
                        <p class="text-sm text-slate-400">{{ booking.show.date }} at {{ booking.show.time }} | {{ booking.show.screen.theater.name }}</p>
                    </div>
                    <div class="text-right">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {% if booking.status == 'CONFIRMED' %}bg-green-100 text-green-800{% else %}bg-slate-100 text-slate-800{% endif %}">
                            {{ booking.status }}
                        </span>
                        <p class="text-sm font-medium text-slate-200 mt-1">₹{{ booking.total_amount }}</p>
                    </div>
                </div>
                {% empty %}
                <p class="text-slate-400 text-center py-4">No recent bookings found.</p>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

accounts_profile_edit_html = '''{% extends 'base.html' %}
{% load widget_tweaks %}

{% block title %}Edit Profile - CineBook{% endblock %}

{% block content %}
<div class="max-w-2xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
    <div class="bg-slate-800/50 backdrop-blur-md rounded-2xl p-8 border border-slate-700 shadow-xl">
        <h2 class="text-2xl font-bold text-slate-100 mb-6">Edit Profile</h2>
        <form method="POST" enctype="multipart/form-data" class="space-y-6">
            {% csrf_token %}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                {% for field in form %}
                <div class="{% if field.name == 'avatar' or field.name == 'email' %}md:col-span-2{% endif %}">
                    <label for="{{ field.id_for_label }}" class="block text-sm font-medium text-slate-300 mb-1">{{ field.label }}</label>
                    {% render_field field class="appearance-none rounded-lg relative block w-full px-3 py-2 border border-slate-600 placeholder-slate-400 text-slate-100 bg-slate-700 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" %}
                    {% if field.errors %}
                        <p class="text-red-500 text-xs mt-1">{{ field.errors.0 }}</p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            <div class="flex justify-end space-x-4 pt-4">
                <a href="{% url 'accounts:profile' %}" class="px-4 py-2 border border-slate-600 rounded-lg text-slate-300 hover:bg-slate-700 transition-colors">Cancel</a>
                <button type="submit" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors shadow-lg shadow-indigo-500/30">Save Changes</button>
            </div>
        </form>
    </div>
</div>
{% endblock %}
'''

accounts_booking_history_html = '''{% extends 'base.html' %}

{% block title %}Booking History - CineBook{% endblock %}

{% block content %}
<div class="max-w-5xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
    <h2 class="text-3xl font-bold text-slate-100 mb-8">Booking History</h2>
    
    <div class="space-y-6">
        {% for booking in bookings %}
        <div class="bg-slate-800/50 rounded-xl p-6 border border-slate-700 flex flex-col md:flex-row items-center justify-between gap-6 hover:border-indigo-500/50 transition-colors">
            <div class="flex items-center space-x-6 w-full md:w-auto">
                {% if booking.show.movie.primary_poster %}
                    <img src="{{ booking.show.movie.primary_poster.image.url }}" alt="{{ booking.show.movie.title }}" class="w-20 h-28 object-cover rounded-lg shadow-lg">
                {% else %}
                    <div class="w-20 h-28 bg-slate-700 rounded-lg flex items-center justify-center"><i class="fas fa-film text-slate-500 text-2xl"></i></div>
                {% endif %}
                <div>
                    <h3 class="text-xl font-bold text-slate-100">{{ booking.show.movie.title }}</h3>
                    <p class="text-slate-400 mt-1"><i class="far fa-calendar-alt mr-2"></i>{{ booking.show.date|date:"D, d M Y" }} at {{ booking.show.time|time:"h:i A" }}</p>
                    <p class="text-slate-400"><i class="fas fa-map-marker-alt mr-2"></i>{{ booking.show.screen.theater.name }}, {{ booking.show.screen.name }}</p>
                    <p class="text-sm text-slate-500 mt-2">Seats: {{ booking.seat_numbers }}</p>
                </div>
            </div>
            
            <div class="flex flex-row md:flex-col items-center md:items-end justify-between w-full md:w-auto mt-4 md:mt-0 pt-4 md:pt-0 border-t md:border-t-0 border-slate-700">
                <div class="text-left md:text-right">
                    <p class="text-sm text-slate-400">Total Amount</p>
                    <p class="text-xl font-bold text-amber-500">₹{{ booking.total_amount }}</p>
                </div>
                <div class="mt-0 md:mt-3">
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium {% if booking.status == 'CONFIRMED' %}bg-green-500/20 text-green-400 border border-green-500/30{% elif booking.status == 'CANCELLED' %}bg-red-500/20 text-red-400 border border-red-500/30{% else %}bg-amber-500/20 text-amber-400 border border-amber-500/30{% endif %}">
                        {{ booking.status }}
                    </span>
                </div>
            </div>
        </div>
        {% empty %}
        <div class="text-center py-12 bg-slate-800/30 rounded-2xl border border-slate-700 border-dashed">
            <i class="fas fa-ticket-alt text-4xl text-slate-500 mb-4"></i>
            <h3 class="text-lg font-medium text-slate-300">No bookings yet</h3>
            <p class="text-slate-500 mt-1">When you book tickets, they will appear here.</p>
            <a href="{% url 'movies:list' %}" class="mt-4 inline-block px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors">Browse Movies</a>
        </div>
        {% endfor %}
    </div>

    <!-- Pagination -->
    {% if is_paginated %}
    <div class="mt-10 flex justify-center">
        <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
            {% if page_obj.has_previous %}
            <a href="?page={{ page_obj.previous_page_number }}" class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-slate-600 bg-slate-800 text-sm font-medium text-slate-300 hover:bg-slate-700">
                <span class="sr-only">Previous</span>
                <i class="fas fa-chevron-left"></i>
            </a>
            {% endif %}
            
            {% for i in paginator.page_range %}
                {% if page_obj.number == i %}
                <span class="relative inline-flex items-center px-4 py-2 border border-indigo-500 bg-indigo-600 text-sm font-medium text-white">{{ i }}</span>
                {% else %}
                <a href="?page={{ i }}" class="relative inline-flex items-center px-4 py-2 border border-slate-600 bg-slate-800 text-sm font-medium text-slate-300 hover:bg-slate-700">{{ i }}</a>
                {% endif %}
            {% endfor %}

            {% if page_obj.has_next %}
            <a href="?page={{ page_obj.next_page_number }}" class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-slate-600 bg-slate-800 text-sm font-medium text-slate-300 hover:bg-slate-700">
                <span class="sr-only">Next</span>
                <i class="fas fa-chevron-right"></i>
            </a>
            {% endif %}
        </nav>
    </div>
    {% endif %}
</div>
{% endblock %}
'''

movies_apps = '''from django.apps import AppConfig

class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.movies'
    label = 'movies'

    def ready(self):
        import apps.movies.signals
'''

movies_models = '''from django.db import models
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
'''

movies_signals = '''from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from .models import Review, Movie

@receiver([post_save, post_delete], sender=Review)
def update_movie_rating(sender, instance, **kwargs):
    movie = instance.movie
    agg = Review.objects.filter(movie=movie).aggregate(
        avg_rating=Avg('rating'),
        total_ratings=Count('id')
    )
    movie.avg_rating = agg['avg_rating'] or 0.00
    movie.total_ratings = agg['total_ratings'] or 0
    movie.save(update_fields=['avg_rating', 'total_ratings'])
'''

movies_context_processors = '''from .models import Genre, Language

def global_context(request):
    try:
        from apps.theaters.models import City
        cities = City.objects.all()
    except Exception:
        cities = []
    
    try:
        genres = Genre.objects.all()
        languages = Language.objects.all()
    except Exception:
        genres = []
        languages = []
        
    return {
        'genres': genres,
        'languages': languages,
        'cities': cities,
    }
'''

movies_forms = '''from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'content']

class MovieSearchForm(forms.Form):
    SORT_CHOICES = [
        ('popularity', 'Popularity'),
        ('newest', 'Newest First'),
        ('rating', 'Top Rated'),
        ('price', 'Price: Low to High'),
    ]
    q = forms.CharField(required=False)
    genre = forms.CharField(required=False)
    language = forms.CharField(required=False)
    city = forms.CharField(required=False)
    min_rating = forms.DecimalField(required=False, max_digits=3, decimal_places=1)
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False)
'''

movies_views = '''from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from .models import Movie, Review
from .forms import ReviewForm, MovieSearchForm

class HomeView(TemplateView):
    template_name = 'movies/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        
        context['now_showing'] = Movie.objects.filter(is_active=True).distinct()[:8]
        context['trending'] = Movie.objects.filter(is_active=True).order_by('-total_ratings')[:8]
        
        thirty_days_ago = now.date() - timedelta(days=30)
        context['recently_released'] = Movie.objects.filter(release_date__gte=thirty_days_ago, is_active=True).order_by('-release_date')[:8]
        
        context['recommended'] = Movie.objects.filter(is_active=True).order_by('?')[:4]
        return context

class MovieListView(ListView):
    model = Movie
    template_name = 'movies/movie_list.html'
    context_object_name = 'movies'
    paginate_by = 12

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['movies/partials/movie_list_results.html']
        return ['movies/movie_list.html']

    def get_queryset(self):
        qs = Movie.objects.filter(is_active=True)
        form = MovieSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            genre = form.cleaned_data.get('genre')
            language = form.cleaned_data.get('language')
            min_rating = form.cleaned_data.get('min_rating')
            sort_by = form.cleaned_data.get('sort_by')
            
            if q:
                qs = qs.filter(title__icontains=q)
            if genre:
                qs = qs.filter(genres__slug=genre)
            if language:
                qs = qs.filter(languages__code=language)
            if min_rating:
                qs = qs.filter(avg_rating__gte=min_rating)
                
            if sort_by == 'newest':
                qs = qs.order_by('-release_date')
            elif sort_by == 'rating':
                qs = qs.order_by('-avg_rating')
            else:
                qs = qs.order_by('-total_ratings')
                
        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MovieSearchForm(self.request.GET)
        return context

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()
        context['reviews'] = movie.reviews.all().order_by('-created_at')[:10]
        context['similar_movies'] = Movie.objects.filter(genres__in=movie.genres.all()).exclude(id=movie.id).distinct()[:6]
        
        context['show_dates'] = []
        
        context['user_can_review'] = False
        if self.request.user.is_authenticated:
            try:
                from apps.bookings.models import Booking
                context['user_can_review'] = Booking.objects.filter(user=self.request.user, show__movie=movie, status='CONFIRMED').exists()
            except Exception:
                pass
            
        return context

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'movies/review_form.html'

    def form_valid(self, form):
        movie = get_object_or_404(Movie, slug=self.kwargs['slug'])
        form.instance.movie = movie
        form.instance.user = self.request.user
        form.instance.is_verified = True
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('movies:detail', kwargs={'slug': self.kwargs['slug']})

class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'movies/review_form.html'

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
        
    def get_success_url(self):
        return reverse_lazy('movies:detail', kwargs={'slug': self.object.movie.slug})

class ReviewReportView(LoginRequiredMixin, View):
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        review.is_reported = True
        review.report_reason = request.POST.get('reason', 'Reported by user')
        review.save()
        return redirect('movies:detail', slug=review.movie.slug)

class MovieSeatAvailabilityView(View):
    def get(self, request, show_id):
        return JsonResponse({'status': 'ok', 'available_seats': 50})
'''

movies_urls = '''from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('list/', views.MovieListView.as_view(), name='list'),
    path('<slug:slug>/', views.MovieDetailView.as_view(), name='detail'),
    path('<slug:slug>/review/', views.ReviewCreateView.as_view(), name='review_create'),
    path('review/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='review_edit'),
    path('review/<int:pk>/report/', views.ReviewReportView.as_view(), name='review_report'),
    path('seats/show/<int:show_id>/', views.MovieSeatAvailabilityView.as_view(), name='seat_availability'),
]
'''

movies_admin = '''from django.contrib import admin
from .models import Genre, Language, CastMember, Movie, MovieCast, MoviePoster, Review

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']

@admin.register(CastMember)
class CastMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'role_type']
    list_filter = ['role_type']
    search_fields = ['name']

class MoviePosterInline(admin.TabularInline):
    model = MoviePoster
    extra = 1

class MovieCastInline(admin.TabularInline):
    model = MovieCast
    extra = 1
    ordering = ['order']

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_date', 'avg_rating', 'is_active']
    list_filter = ['is_active', 'genres', 'age_certification']
    search_fields = ['title']
    inlines = [MoviePosterInline, MovieCastInline]
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'rating', 'is_verified', 'is_reported']
    list_filter = ['is_reported', 'is_verified']
    actions = ['approve_reviews', 'mark_reported']

    @admin.action(description='Approve selected reviews')
    def approve_reviews(self, request, queryset):
        queryset.update(is_verified=True, is_reported=False)

    @admin.action(description='Mark selected reviews as reported')
    def mark_reported(self, request, queryset):
        queryset.update(is_reported=True)
'''

movies_movie_list_html = '''{% extends 'base.html' %}
{% load widget_tweaks %}

{% block title %}Movies - CineBook{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row gap-8">
    
    <aside class="w-full md:w-64 flex-shrink-0">
        <div class="bg-slate-800/50 backdrop-blur-md rounded-2xl p-6 border border-slate-700 sticky top-24">
            <h3 class="text-xl font-bold text-slate-100 mb-6 flex items-center"><i class="fas fa-filter mr-2 text-indigo-400"></i> Filters</h3>
            
            <form id="filter-form" 
                  hx-get="{% url 'movies:list' %}" 
                  hx-target="#movie-grid" 
                  hx-trigger="change, submit" 
                  hx-indicator="#loading"
                  class="space-y-6">
                  
                <div>
                    <label class="block text-sm font-medium text-slate-300 mb-2">Search</label>
                    {% render_field form.q class="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg text-sm text-slate-200 focus:ring-indigo-500 focus:border-indigo-500" placeholder="Movie title..." %}
                </div>

                <div>
                    <label class="block text-sm font-medium text-slate-300 mb-2">Genre</label>
                    <div class="space-y-2 max-h-48 overflow-y-auto custom-scrollbar pr-2">
                        {% for genre in genres %}
                        <div class="flex items-center">
                            <input type="radio" id="genre_{{ genre.slug }}" name="genre" value="{{ genre.slug }}" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-slate-600 bg-slate-700">
                            <label for="genre_{{ genre.slug }}" class="ml-2 block text-sm text-slate-400 hover:text-slate-200 cursor-pointer">{{ genre.name }}</label>
                        </div>
                        {% endfor %}
                    </div>
                </div>

                <div>
                    <label class="block text-sm font-medium text-slate-300 mb-2">Language</label>
                    {% render_field form.language class="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg text-sm text-slate-200 focus:ring-indigo-500 focus:border-indigo-500" %}
                </div>

                <div>
                    <label class="block text-sm font-medium text-slate-300 mb-2">Sort By</label>
                    {% render_field form.sort_by class="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg text-sm text-slate-200 focus:ring-indigo-500 focus:border-indigo-500" %}
                </div>
            </form>
        </div>
    </aside>

    <main class="flex-1">
        <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold text-slate-100">Browse Movies</h2>
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-slate-800 text-slate-300 border border-slate-700">
                <span id="results-count">{{ page_obj.paginator.count }}</span>&nbsp;Results
            </span>
        </div>

        <div id="movie-grid" class="relative min-h-[400px]">
            {% include 'movies/partials/movie_list_results.html' %}
        </div>
    </main>
</div>
{% endblock %}
'''

movies_movie_detail_html = '''{% extends 'base.html' %}
{% load humanize %}

{% block title %}{{ movie.title }} - CineBook{% endblock %}

{% block content %}
<div class="relative min-h-[60vh] flex items-center">
    <div class="absolute inset-0 bg-slate-900">
        {% if movie.primary_poster %}
        <div class="absolute inset-0 bg-cover bg-center opacity-30 blur-sm" style="background-image: url('{{ movie.primary_poster.image.url }}');"></div>
        {% endif %}
        <div class="absolute inset-0 bg-gradient-to-t from-[#0f172a] via-[#0f172a]/80 to-transparent"></div>
    </div>

    <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 w-full flex flex-col md:flex-row gap-8 items-center md:items-end">
        <div class="w-48 md:w-64 flex-shrink-0 group relative rounded-xl overflow-hidden shadow-2xl shadow-indigo-500/20">
            {% if movie.primary_poster %}
            <img src="{{ movie.primary_poster.image.url }}" alt="{{ movie.title }}" class="w-full h-auto object-cover transform group-hover:scale-105 transition-transform duration-500">
            {% else %}
            <div class="w-full aspect-[2/3] bg-slate-800 flex items-center justify-center"><i class="fas fa-film text-4xl text-slate-600"></i></div>
            {% endif %}
            
            {% if movie.youtube_embed_url %}
            <div class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 cursor-pointer" onclick="document.getElementById('trailer-modal').classList.remove('hidden')">
                <i class="fas fa-play-circle text-6xl text-white/90 drop-shadow-lg hover:scale-110 transition-transform"></i>
            </div>
            {% endif %}
        </div>

        <div class="flex-1 text-center md:text-left">
            <h1 class="text-4xl md:text-5xl font-bold text-white mb-2 drop-shadow-md">{{ movie.title }}</h1>
            
            <div class="flex flex-wrap items-center justify-center md:justify-start gap-4 text-sm font-medium text-slate-300 mb-6">
                <span class="flex items-center text-amber-400 bg-amber-400/10 px-2 py-1 rounded-md border border-amber-400/20"><i class="fas fa-star mr-1"></i> {{ movie.avg_rating }} ({{ movie.total_ratings|intcomma }})</span>
                <span class="px-2 py-1 border border-slate-600 rounded-md bg-slate-800/50">{{ movie.age_certification }}</span>
                <span>{{ movie.duration }}</span>
                <span>{{ movie.release_date|date:"d M Y" }}</span>
                <div class="flex gap-2">
                    {% for lang in movie.languages.all %}
                    <span class="px-2 py-1 bg-indigo-500/20 text-indigo-300 rounded-md">{{ lang.name }}</span>
                    {% endfor %}
                </div>
            </div>

            <div class="flex flex-wrap gap-2 justify-center md:justify-start mb-6">
                {% for genre in movie.genres.all %}
                <span class="px-3 py-1 bg-slate-800 border border-slate-700 rounded-full text-sm text-slate-300 hover:border-indigo-500 hover:text-indigo-400 transition-colors">
                    {% if genre.icon %}<i class="{{ genre.icon }} mr-1"></i>{% endif %}{{ genre.name }}
                </span>
                {% endfor %}
            </div>

            <p class="text-slate-300 text-lg leading-relaxed max-w-3xl mb-8">{{ movie.description }}</p>
            
            <div class="flex gap-4 justify-center md:justify-start">
                <a href="#shows" class="px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold rounded-lg shadow-lg shadow-indigo-500/30 transition-all transform hover:-translate-y-1">Book Tickets</a>
                {% if movie.youtube_embed_url %}
                <button onclick="document.getElementById('trailer-modal').classList.remove('hidden')" class="px-8 py-3 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-lg border border-slate-600 transition-colors flex items-center">
                    <i class="fas fa-play mr-2"></i> Trailer
                </button>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 border-b border-slate-800">
    <h2 class="text-2xl font-bold text-slate-100 mb-6">Cast & Crew</h2>
    <div class="flex overflow-x-auto pb-4 gap-6 custom-scrollbar snap-x">
        {% for mcast in movie.moviecast_set.all %}
        <div class="w-32 flex-shrink-0 snap-start text-center group">
            <div class="w-24 h-24 mx-auto rounded-full overflow-hidden border-2 border-slate-700 group-hover:border-indigo-500 transition-colors mb-3">
                {% if mcast.cast_member.photo %}
                <img src="{{ mcast.cast_member.photo.url }}" class="w-full h-full object-cover">
                {% else %}
                <div class="w-full h-full bg-slate-800 flex items-center justify-center"><i class="fas fa-user text-slate-500 text-2xl"></i></div>
                {% endif %}
            </div>
            <h4 class="text-sm font-bold text-slate-200 truncate">{{ mcast.cast_member.name }}</h4>
            <p class="text-xs text-slate-400 truncate">{{ mcast.character_name|default:mcast.cast_member.get_role_type_display }}</p>
        </div>
        {% endfor %}
    </div>
</div>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <div class="flex justify-between items-end mb-8">
        <div>
            <h2 class="text-2xl font-bold text-slate-100">Reviews</h2>
            <p class="text-slate-400">Based on {{ movie.total_ratings }} ratings</p>
        </div>
        {% if user_can_review %}
        <a href="{% url 'movies:review_create' movie.slug %}" class="px-4 py-2 bg-indigo-600/20 text-indigo-400 border border-indigo-600/30 rounded-lg hover:bg-indigo-600/30 transition-colors">Write a Review</a>
        {% endif %}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        {% for review in reviews %}
        <div class="bg-slate-800/40 p-6 rounded-xl border border-slate-700 relative group">
            <div class="flex justify-between items-start mb-4">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-slate-300 font-bold">
                        {{ review.user.username.0|upper }}
                    </div>
                    <div>
                        <h4 class="text-slate-200 font-medium flex items-center">
                            {{ review.user.get_full_name|default:review.user.username }}
                            {% if review.is_verified %}<i class="fas fa-check-circle text-blue-400 ml-2 text-xs" title="Verified Ticket"></i>{% endif %}
                        </h4>
                        <p class="text-xs text-slate-500">{{ review.created_at|date:"d M Y" }}</p>
                    </div>
                </div>
                <div class="flex text-amber-400 text-sm">
                    {% for i in "12345" %}
                        <i class="fas fa-star {% if forloop.counter > review.rating %}text-slate-600{% endif %}"></i>
                    {% endfor %}
                </div>
            </div>
            <h5 class="text-slate-100 font-bold mb-2">{{ review.title }}</h5>
            <p class="text-slate-400 text-sm line-clamp-3">{{ review.content }}</p>
            
            {% if request.user.is_authenticated and request.user != review.user %}
            <form action="{% url 'movies:review_report' review.id %}" method="POST" class="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                {% csrf_token %}
                <button type="submit" class="text-xs text-slate-500 hover:text-red-400 flex items-center" onclick="return confirm('Report this review?');"><i class="fas fa-flag mr-1"></i> Report</button>
            </form>
            {% endif %}
        </div>
        {% empty %}
        <p class="text-slate-500 italic col-span-full">No reviews yet. Be the first to review!</p>
        {% endfor %}
    </div>
</div>

{% if movie.youtube_embed_url %}
<div id="trailer-modal" class="fixed inset-0 z-50 hidden bg-black/90 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="relative w-full max-w-5xl aspect-video bg-black rounded-xl overflow-hidden shadow-2xl border border-slate-700">
        <button onclick="document.getElementById('trailer-modal').classList.add('hidden')" class="absolute -top-12 right-0 text-white hover:text-indigo-400 z-50 text-3xl"><i class="fas fa-times"></i></button>
        <iframe class="w-full h-full" src="{{ movie.youtube_embed_url }}?autoplay=0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" sandbox="allow-scripts allow-same-origin allow-presentation" allowfullscreen></iframe>
    </div>
</div>
{% endif %}
{% endblock %}
'''

movies_review_form_html = '''{% extends 'base.html' %}
{% load widget_tweaks %}

{% block title %}Review {{ form.instance.movie.title|default:"Movie" }} - CineBook{% endblock %}

{% block content %}
<div class="max-w-2xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
    <div class="bg-slate-800/80 backdrop-blur-md rounded-2xl p-8 border border-slate-700 shadow-xl">
        <h2 class="text-2xl font-bold text-slate-100 mb-6">Write a Review</h2>
        <form method="POST" class="space-y-6">
            {% csrf_token %}
            
            <div class="rating-stars mb-6 flex space-x-2 text-3xl text-slate-600 cursor-pointer">
                {% for i in "12345" %}
                <i class="fas fa-star star hover:text-amber-400 transition-colors" data-value="{{ forloop.counter }}"></i>
                {% endfor %}
            </div>
            <input type="hidden" name="rating" id="id_rating" value="{{ form.rating.value|default:5 }}">
            {% if form.rating.errors %}<p class="text-red-500 text-xs mt-1">{{ form.rating.errors.0 }}</p>{% endif %}

            <div>
                <label for="{{ form.title.id_for_label }}" class="block text-sm font-medium text-slate-300 mb-1">Headline</label>
                {% render_field form.title class="appearance-none rounded-lg relative block w-full px-3 py-2 border border-slate-600 placeholder-slate-400 text-slate-100 bg-slate-700 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" placeholder="Summarize your experience" %}
                {% if form.title.errors %}<p class="text-red-500 text-xs mt-1">{{ form.title.errors.0 }}</p>{% endif %}
            </div>

            <div>
                <label for="{{ form.content.id_for_label }}" class="block text-sm font-medium text-slate-300 mb-1">Detailed Review</label>
                {% render_field form.content rows="5" class="appearance-none rounded-lg relative block w-full px-3 py-2 border border-slate-600 placeholder-slate-400 text-slate-100 bg-slate-700 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" placeholder="What did you like or dislike?" %}
                {% if form.content.errors %}<p class="text-red-500 text-xs mt-1">{{ form.content.errors.0 }}</p>{% endif %}
            </div>

            <div class="flex justify-end space-x-4 pt-4">
                <button type="button" onclick="history.back()" class="px-4 py-2 border border-slate-600 rounded-lg text-slate-300 hover:bg-slate-700 transition-colors">Cancel</button>
                <button type="submit" class="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors shadow-lg shadow-indigo-500/30 font-medium">Submit Review</button>
            </div>
        </form>
    </div>
</div>

<script>
    document.addEventListener('DOMContentLoaded', function() {
        const stars = document.querySelectorAll('.star');
        const ratingInput = document.getElementById('id_rating');
        
        function updateStars(value) {
            stars.forEach(star => {
                if (star.dataset.value <= value) {
                    star.classList.remove('text-slate-600');
                    star.classList.add('text-amber-400');
                } else {
                    star.classList.add('text-slate-600');
                    star.classList.remove('text-amber-400');
                }
            });
        }
        
        updateStars(ratingInput.value);

        stars.forEach(star => {
            star.addEventListener('mouseover', function() {
                updateStars(this.dataset.value);
            });
            
            star.addEventListener('click', function() {
                ratingInput.value = this.dataset.value;
                updateStars(this.dataset.value);
            });
        });
        
        document.querySelector('.rating-stars').addEventListener('mouseleave', function() {
            updateStars(ratingInput.value);
        });
    });
</script>
{% endblock %}
'''

movies_movie_card_html = '''{% load humanize %}
<a href="{% url 'movies:detail' movie.slug %}" class="block group">
    <div class="bg-slate-800 rounded-xl overflow-hidden border border-slate-700 hover:border-indigo-500/50 transition-all duration-300 shadow-lg hover:shadow-indigo-500/10 h-full flex flex-col">
        <div class="relative aspect-[2/3] overflow-hidden">
            {% if movie.primary_poster %}
            <img src="{{ movie.primary_poster.image.url }}" alt="{{ movie.title }}" class="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700">
            {% else %}
            <div class="w-full h-full bg-slate-700 flex items-center justify-center group-hover:scale-105 transition-transform duration-700"><i class="fas fa-film text-4xl text-slate-500"></i></div>
            {% endif %}
            <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/20 to-transparent opacity-80"></div>
            
            <div class="absolute bottom-0 left-0 right-0 p-4">
                <div class="flex justify-between items-end">
                    <div class="flex items-center space-x-1 text-amber-400 font-bold bg-slate-900/60 backdrop-blur-sm px-2 py-1 rounded-md text-sm border border-slate-700/50">
                        <i class="fas fa-star text-xs"></i> <span>{{ movie.avg_rating }}</span>
                    </div>
                    <span class="text-xs font-medium bg-indigo-600 text-white px-2 py-1 rounded shadow-sm">{{ movie.age_certification }}</span>
                </div>
            </div>
        </div>
        <div class="p-4 flex-1 flex flex-col">
            <h3 class="text-lg font-bold text-slate-100 truncate mb-1 group-hover:text-indigo-400 transition-colors">{{ movie.title }}</h3>
            <p class="text-xs text-slate-400 mb-3 truncate">
                {{ movie.languages.all|join:", " }} &bull; {{ movie.duration }}
            </p>
            <div class="mt-auto flex flex-wrap gap-1">
                {% for genre in movie.genres.all|slice:":3" %}
                <span class="text-[10px] uppercase tracking-wider font-semibold text-slate-400 bg-slate-700/50 px-2 py-0.5 rounded-sm">{{ genre.name }}</span>
                {% endfor %}
            </div>
        </div>
    </div>
</a>
'''

movies_movie_list_results_html = '''{% if movies %}
<div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-6 fade-in">
    {% for movie in movies %}
        {% include 'movies/partials/movie_card.html' %}
    {% endfor %}
</div>

{% if is_paginated %}
<div class="mt-10 flex justify-center fade-in">
    <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
        {% if page_obj.has_previous %}
        <button hx-get="?page={{ page_obj.previous_page_number }}{% for key,value in request.GET.items %}{% if key != 'page' %}&{{ key }}={{ value }}{% endif %}{% endfor %}" hx-target="#movie-grid" class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-slate-600 bg-slate-800 text-sm font-medium text-slate-300 hover:bg-slate-700">
            <span class="sr-only">Previous</span>
            <i class="fas fa-chevron-left"></i>
        </button>
        {% endif %}
        
        <span class="relative inline-flex items-center px-4 py-2 border border-slate-600 bg-slate-800 text-sm font-medium text-slate-300">
            Page {{ page_obj.number }} of {{ paginator.num_pages }}
        </span>

        {% if page_obj.has_next %}
        <button hx-get="?page={{ page_obj.next_page_number }}{% for key,value in request.GET.items %}{% if key != 'page' %}&{{ key }}={{ value }}{% endif %}{% endfor %}" hx-target="#movie-grid" class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-slate-600 bg-slate-800 text-sm font-medium text-slate-300 hover:bg-slate-700">
            <span class="sr-only">Next</span>
            <i class="fas fa-chevron-right"></i>
        </button>
        {% endif %}
    </nav>
</div>
{% endif %}
{% else %}
<div class="flex flex-col items-center justify-center py-20 text-center fade-in bg-slate-800/30 rounded-2xl border border-slate-700 border-dashed h-full">
    <i class="fas fa-search text-5xl text-slate-600 mb-4"></i>
    <h3 class="text-xl font-medium text-slate-300">No movies found</h3>
    <p class="text-slate-500 mt-2 max-w-md">Try adjusting your filters or search terms to find what you're looking for.</p>
    <button onclick="document.getElementById('filter-form').reset(); htmx.trigger('#filter-form', 'change')" class="mt-6 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors">Clear Filters</button>
</div>
{% endif %}

<style>
.fade-in { animation: fadeIn 0.3s ease-in; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
</style>
'''

files_to_create = {
    # Accounts app
    os.path.join(base_dir, "apps/accounts/__init__.py"): "",
    os.path.join(base_dir, "apps/accounts/apps.py"): accounts_apps,
    os.path.join(base_dir, "apps/accounts/models.py"): accounts_models,
    os.path.join(base_dir, "apps/accounts/forms.py"): accounts_forms,
    os.path.join(base_dir, "apps/accounts/views.py"): accounts_views,
    os.path.join(base_dir, "apps/accounts/urls.py"): accounts_urls,
    os.path.join(base_dir, "apps/accounts/admin.py"): accounts_admin,
    os.path.join(base_dir, "apps/accounts/templates/accounts/login.html"): accounts_login_html,
    os.path.join(base_dir, "apps/accounts/templates/accounts/register.html"): accounts_register_html,
    os.path.join(base_dir, "apps/accounts/templates/accounts/profile.html"): accounts_profile_html,
    os.path.join(base_dir, "apps/accounts/templates/accounts/profile_edit.html"): accounts_profile_edit_html,
    os.path.join(base_dir, "apps/accounts/templates/accounts/booking_history.html"): accounts_booking_history_html,
    # Movies app
    os.path.join(base_dir, "apps/movies/__init__.py"): "",
    os.path.join(base_dir, "apps/movies/apps.py"): movies_apps,
    os.path.join(base_dir, "apps/movies/models.py"): movies_models,
    os.path.join(base_dir, "apps/movies/signals.py"): movies_signals,
    os.path.join(base_dir, "apps/movies/context_processors.py"): movies_context_processors,
    os.path.join(base_dir, "apps/movies/forms.py"): movies_forms,
    os.path.join(base_dir, "apps/movies/views.py"): movies_views,
    os.path.join(base_dir, "apps/movies/urls.py"): movies_urls,
    os.path.join(base_dir, "apps/movies/admin.py"): movies_admin,
    os.path.join(base_dir, "apps/movies/templates/movies/movie_list.html"): movies_movie_list_html,
    os.path.join(base_dir, "apps/movies/templates/movies/movie_detail.html"): movies_movie_detail_html,
    os.path.join(base_dir, "apps/movies/templates/movies/review_form.html"): movies_review_form_html,
    os.path.join(base_dir, "apps/movies/templates/movies/partials/movie_card.html"): movies_movie_card_html,
    os.path.join(base_dir, "apps/movies/templates/movies/partials/movie_list_results.html"): movies_movie_list_results_html,
}

for filepath, content in files_to_create.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Created all files successfully.")
