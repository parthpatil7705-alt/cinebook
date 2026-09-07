from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, DetailView
from django.http import JsonResponse
from django.urls import reverse
import json

from apps.theaters.models import Show, Seat, ShowSeatPrice
from .models import Booking
from .services import BookingService, SeatUnavailableError

class SeatSelectionView(LoginRequiredMixin, View):
    def get(self, request, show_id):
        show = get_object_or_404(Show, id=show_id, is_active=True, is_cancelled=False)
        availability = BookingService.get_seat_availability(show)
        
        # Group seats by row
        seats_by_row = {}
        seat_prices = {sp.category_id: sp.price for sp in show.seat_prices.all()}
        
        for seat in show.screen.seats.all():
            if seat.row_label not in seats_by_row:
                seats_by_row[seat.row_label] = []
                
            status = availability.get(seat.id, 'available')
            price = seat_prices.get(seat.category_id, 0)
            
            seats_by_row[seat.row_label].append({
                'id': seat.id,
                'seat_number': seat.seat_number,
                'display_name': seat.display_name,
                'status': status,
                'price': price,
            })
            
        context = {
            'show': show,
            'seats_by_row': dict(sorted(seats_by_row.items())),
            'categories': {c.id: c for c in show.seat_prices.select_related('category').all()}
        }
        return render(request, 'bookings/seat_selection.html', context)

class ReserveSeatsView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            show_id = data.get('show_id')
            seat_ids = data.get('seat_ids', [])
            
            show = get_object_or_404(Show, id=show_id)
            if not seat_ids:
                return JsonResponse({'error': 'No seats selected'}, status=400)
                
            reservations, expires = BookingService.reserve_seats(request.user, show, seat_ids)
            
            # create pending booking immediately for simpler flow, or just hold them.
            # let's just return success.
            return JsonResponse({
                'success': True,
                'expires_at': expires.isoformat(),
                'reservation_ids': [r.id for r in reservations]
            })
            
        except SeatUnavailableError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ModifyReservationView(LoginRequiredMixin, View):
    def post(self, request):
        # We can implement it if needed, same as ReserveSeatsView just wrapped
        return JsonResponse({'success': True})

class BookingSummaryView(LoginRequiredMixin, View):
    def post(self, request, show_id):
        show = get_object_or_404(Show, id=show_id)
        seat_ids = request.POST.getlist('seat_ids')
        
        if not seat_ids:
            return redirect('bookings:select_seats', show_id=show.id)
            
        # We assume they are reserved. Create booking.
        booking = BookingService.create_booking(request.user, show, seat_ids)
        return redirect('bookings:summary', booking_id=booking.booking_id)

class BookingSummaryGetView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_summary.html'
    context_object_name = 'booking'
    slug_field = 'booking_id'
    slug_url_kwarg = 'booking_id'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user, status='pending')

class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'
    slug_field = 'booking_id'
    slug_url_kwarg = 'booking_id'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class BookingCancelView(LoginRequiredMixin, View):
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
        if booking.status == 'pending':
            BookingService.cancel_booking(booking)
        return redirect('bookings:detail', booking_id=booking.booking_id)

class SeatAvailabilityAPIView(LoginRequiredMixin, View):
    def get(self, request, show_id):
        show = get_object_or_404(Show, id=show_id)
        availability = BookingService.get_seat_availability(show)
        return JsonResponse(availability)
