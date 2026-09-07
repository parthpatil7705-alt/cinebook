from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('booking', 'generated_at', 'email_sent', 'email_attempts')
    search_fields = ('booking__booking_id',)
    list_filter = ('email_sent', 'generated_at')
