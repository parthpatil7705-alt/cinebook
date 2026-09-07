from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('download/<uuid:booking_id>/', views.DownloadTicketView.as_view(), name='download'),
]
