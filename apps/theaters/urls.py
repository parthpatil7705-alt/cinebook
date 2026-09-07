from django.urls import path
from . import views

app_name = 'theaters'

urlpatterns = [
    path('', views.TheaterListView.as_view(), name='theater_list'),
    path('<slug:slug>/detail/', views.TheaterDetailView.as_view(), name='theater_detail'),
    path('shows/<slug:movie_slug>/', views.ShowListView.as_view(), name='show_list'),
    path('show/<int:pk>/', views.ShowDetailView.as_view(), name='show_detail'),
    path('city/<slug:slug>/', views.CityShowsView.as_view(), name='city_shows'),
]

