from django.db.models.signals import post_save, post_delete
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
