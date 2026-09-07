from django.db.models import Count, Q, ExpressionWrapper, IntegerField
from django.utils import timezone
from datetime import timedelta
from apps.movies.models import Movie
from apps.bookings.models import Booking

class RecommendationService:
    @staticmethod
    def similar_movies(movie, limit=8):
        """Movies sharing genres/language. Scored by matching genre count."""
        genres = movie.genres.all()
        return Movie.objects.filter(
            Q(genres__in=genres) | Q(language=movie.language)
        ).exclude(
            id=movie.id
        ).annotate(
            match_score=Count('genres', filter=Q(genres__in=genres))
        ).order_by('-match_score', '-release_date').distinct()[:limit]
    
    @staticmethod
    def trending_movies(limit=10):
        """Most booked in last 7 days."""
        week_ago = timezone.now() - timedelta(days=7)
        return Movie.objects.filter(
            shows__bookings__created_at__gte=week_ago,
            shows__bookings__status='confirmed'
        ).annotate(
            recent_bookings=Count('shows__bookings')
        ).order_by('-recent_bookings')[:limit]
    
    @staticmethod
    def recently_released(limit=10):
        """Released in last 30 days, ordered by release_date desc."""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        now = timezone.now()
        return Movie.objects.filter(
            release_date__range=(thirty_days_ago, now)
        ).order_by('-release_date')[:limit]
    
    @staticmethod
    def recommended_for_user(user, limit=10):
        """Based on user's booking history genres. Excludes already booked."""
        if not user.is_authenticated:
            return Movie.objects.none()
            
        user_bookings = Booking.objects.filter(user=user, status='confirmed')
        booked_movies_ids = user_bookings.values_list('show__movie_id', flat=True)
        
        user_genres = Movie.objects.filter(id__in=booked_movies_ids).values_list('genres__id', flat=True)
        
        return Movie.objects.filter(
            genres__id__in=user_genres
        ).exclude(
            id__in=booked_movies_ids
        ).annotate(
            genre_match=Count('genres', filter=Q(genres__id__in=user_genres))
        ).order_by('-genre_match', '-release_date').distinct()[:limit]
    
    @staticmethod
    def coming_soon(limit=10):
        """Movies with release_date in the future."""
        return Movie.objects.filter(
            release_date__gt=timezone.now()
        ).order_by('release_date')[:limit]
