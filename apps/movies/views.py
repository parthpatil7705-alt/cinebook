from django.shortcuts import render, get_object_or_404, redirect
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
    template_name = 'home.html'

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
                context['user_can_review'] = Booking.objects.filter(user=self.request.user, show__movie=movie, status='confirmed').exists()
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
        return reverse_lazy('movies:movie_detail', kwargs={'slug': self.kwargs['slug']})

class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'movies/review_form.html'

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
        
    def get_success_url(self):
        return reverse_lazy('movies:movie_detail', kwargs={'slug': self.object.movie.slug})

class ReviewReportView(LoginRequiredMixin, View):
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        review.is_reported = True
        review.report_reason = request.POST.get('reason', 'Reported by user')
        review.save()
        return redirect('movies:movie_detail', slug=review.movie.slug)

class MovieSeatAvailabilityView(View):
    def get(self, request, show_id):
        return JsonResponse({'status': 'ok', 'available_seats': 50})
