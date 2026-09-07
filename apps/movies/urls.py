from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.MovieListView.as_view(), name='movie_list'),
    path('<slug:slug>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('<slug:slug>/review/', views.ReviewCreateView.as_view(), name='review_create'),
    path('review/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='review_edit'),
    path('review/<int:pk>/report/', views.ReviewReportView.as_view(), name='review_report'),
    path('seats/show/<int:show_id>/', views.MovieSeatAvailabilityView.as_view(), name='seat_availability'),
]

