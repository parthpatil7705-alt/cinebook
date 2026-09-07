from django.contrib import admin
from .models import City, Theater, Screen, SeatCategory, Seat, Show, ShowSeatPrice

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'is_active')
    prepopulated_fields = {'slug': ('name',)}

class SeatInline(admin.TabularInline):
    model = Seat
    extra = 0

@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    list_display = ('name', 'theater', 'screen_type', 'total_seats')
    inlines = [SeatInline]

class ShowSeatPriceInline(admin.TabularInline):
    model = ShowSeatPrice
    extra = 3

@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('movie', 'screen', 'start_time', 'is_active')
    list_filter = ('is_active', 'start_time', 'screen__theater')
    inlines = [ShowSeatPriceInline]
    autocomplete_fields = ['movie']

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'phone', 'is_active')
    list_filter = ('city', 'is_active')
    search_fields = ('name', 'address')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(SeatCategory)
class SeatCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_multiplier')
