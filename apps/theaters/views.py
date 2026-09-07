from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Theater, Show, City
from apps.movies.models import Movie
from collections import defaultdict
import datetime

class TheaterListView(ListView):
    model = Theater
    template_name = 'theaters/theater_list.html'
    context_object_name = 'theaters'
    
    def get_queryset(self):
        qs = super().get_queryset().filter(is_active=True)
        city_slug = self.request.GET.get('city')
        if city_slug:
            qs = qs.filter(city__slug=city_slug)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cities'] = City.objects.filter(is_active=True)
        context['selected_city'] = self.request.GET.get('city', '')
        return context

class TheaterDetailView(DetailView):
    model = Theater
    template_name = 'theaters/theater_detail.html'
    context_object_name = 'theater'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context['upcoming_shows'] = Show.objects.filter(
            screen__theater=self.object,
            start_time__gte=now,
            is_active=True,
            is_cancelled=False
        ).order_by('start_time')
        return context

class ShowListView(ListView):
    template_name = 'theaters/show_list.html'
    context_object_name = 'shows_by_theater'
    
    def get_queryset(self):
        self.movie = get_object_or_404(Movie, slug=self.kwargs.get('movie_slug'))
        
        date_str = self.request.GET.get('date')
        if date_str:
            target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = timezone.now().date()
            
        city_slug = self.request.GET.get('city')
        
        qs = Show.objects.filter(
            movie=self.movie,
            start_time__date=target_date,
            is_active=True,
            is_cancelled=False
        ).order_by('start_time')
        
        if city_slug:
            qs = qs.filter(screen__theater__city__slug=city_slug)
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shows = self.get_queryset()
        
        grouped_shows = defaultdict(list)
        for show in shows:
            grouped_shows[show.screen.theater].append(show)
            
        context['grouped_shows'] = dict(grouped_shows)
        context['movie'] = self.movie
        context['cities'] = City.objects.filter(is_active=True)
        context['selected_city'] = self.request.GET.get('city', '')
        
        date_str = self.request.GET.get('date')
        if date_str:
            context['selected_date'] = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            context['selected_date'] = timezone.now().date()
            
        # Generate next 7 days for tabs
        today = timezone.now().date()
        context['date_tabs'] = [today + datetime.timedelta(days=i) for i in range(7)]
        
        if self.request.headers.get('HX-Request'):
            self.template_name = 'theaters/partials/show_list_content.html'
            
        return context

class ShowDetailView(DetailView):
    model = Show
    template_name = 'theaters/show_detail.html'
    context_object_name = 'show'

class CityShowsView(ListView):
    template_name = 'theaters/city_shows.html'
    context_object_name = 'shows'
    
    def get_queryset(self):
        self.city = get_object_or_404(City, slug=self.kwargs.get('slug'))
        target_date = timezone.now().date()
        return Show.objects.filter(
            screen__theater__city=self.city,
            start_time__date=target_date,
            is_active=True,
            is_cancelled=False
        ).order_by('movie', 'start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['city'] = self.city
        return context
