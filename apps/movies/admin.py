from django.contrib import admin
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
