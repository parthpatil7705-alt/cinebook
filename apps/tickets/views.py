from django.views import View
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Ticket

class DownloadTicketView(LoginRequiredMixin, View):
    def get(self, request, booking_id, *args, **kwargs):
        ticket = get_object_or_404(Ticket, booking__booking_id=booking_id, booking__user=request.user)
        if not ticket.pdf_file:
            raise Http404("Ticket PDF not yet generated.")
            
        response = HttpResponse(ticket.pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ticket_{booking_id}.pdf"'
        return response
