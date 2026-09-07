from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('select-seats/<int:show_id>/', views.SeatSelectionView.as_view(), name='select_seats'),
    path('reserve/', views.ReserveSeatsView.as_view(), name='reserve_seats'),
    path('modify/', views.ModifyReservationView.as_view(), name='modify_reservation'),
    path('summary/<str:booking_id>/', views.BookingSummaryGetView.as_view(), name='summary'),
    path('summary/create/<int:show_id>/', views.BookingSummaryView.as_view(), name='create_summary'),
    path('detail/<str:booking_id>/', views.BookingDetailView.as_view(), name='detail'),
    path('cancel/<str:booking_id>/', views.BookingCancelView.as_view(), name='cancel'),
    path('api/seats/<int:show_id>/', views.SeatAvailabilityAPIView.as_view(), name='api_seats'),
]
