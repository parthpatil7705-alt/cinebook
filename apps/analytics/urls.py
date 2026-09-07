from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('export/', views.ExportCSVView.as_view(), name='export'),
]
