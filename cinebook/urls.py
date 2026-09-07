"""
CineBook Root URL Configuration.
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from apps.movies.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('movies/', include('apps.movies.urls', namespace='movies')),
    path('theaters/', include('apps.theaters.urls', namespace='theaters')),
    path('bookings/', include('apps.bookings.urls', namespace='bookings')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('tickets/', include('apps.tickets.urls', namespace='tickets')),
    path('dashboard/', include('apps.analytics.urls', namespace='analytics')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customize admin site
admin.site.site_header = 'CineBook Administration'
admin.site.site_title = 'CineBook Admin'
admin.site.index_title = 'Movie Booking Management'
