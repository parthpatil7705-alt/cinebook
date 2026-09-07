from .models import Genre, Language

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
