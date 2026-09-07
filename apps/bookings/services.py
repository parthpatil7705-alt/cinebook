import uuid
from datetime import timedelta
from django.db import transaction, OperationalError
from django.utils import timezone
from django.conf import settings
from .models import SeatReservation, Booking, BookedSeat
from apps.theaters.models import ShowSeatPrice

class SeatUnavailableError(Exception):
    pass

class BookingService:
    @staticmethod
    def get_seat_availability(show):
        """Returns dict mapping seat_id to status (available/held/booked) for a show."""
        availability = {}
        
        # All seats for the show's screen
        for seat in show.screen.seats.all():
            availability[seat.id] = 'available'
            
        # Get active (non-expired) held reservations
        held_reservations = SeatReservation.objects.filter(
            show=show, 
            status='held',
            expires_at__gt=timezone.now()
        ).values_list('seat_id', flat=True)
        
        for seat_id in held_reservations:
            availability[seat_id] = 'held'
            
        # Get confirmed booked seats
        booked_seats = BookedSeat.objects.filter(
            booking__show=show, 
            booking__status='confirmed'
        ).values_list('seat_id', flat=True)
        
        for seat_id in booked_seats:
            availability[seat_id] = 'booked'
            
        return availability

    @staticmethod
    def reserve_seats(user, show, seat_ids):
        """Atomically reserve seats with select_for_update(nowait=True)."""
        with transaction.atomic():
            try:
                # Lock existing held reservations for these seats
                existing = SeatReservation.objects.select_for_update(nowait=True).filter(
                    show=show, seat_id__in=seat_ids, status='held',
                    expires_at__gt=timezone.now()
                )
            except OperationalError:
                raise SeatUnavailableError("Seats are being reserved by another user.")
            
            # Check if any are held by another user
            for res in existing:
                if res.user != user:
                    raise SeatUnavailableError(f"Seat {res.seat.display_name} is currently held.")
            
            # Check confirmed bookings
            booked = BookedSeat.objects.filter(
                booking__show=show, booking__status='confirmed',
                seat_id__in=seat_ids
            ).exists()
            if booked:
                raise SeatUnavailableError("One or more seats are already booked.")
            
            # Release user's previous holds for this show
            SeatReservation.objects.filter(
                show=show, user=user, status='held'
            ).update(status='released')
            
            # Create new reservations with 2-minute expiry
            timeout = getattr(settings, 'SEAT_RESERVATION_TIMEOUT_MINUTES', 2)
            expires = timezone.now() + timedelta(minutes=timeout)
            
            reservations = SeatReservation.objects.bulk_create([
                SeatReservation(show=show, seat_id=sid, user=user, expires_at=expires, status='held')
                for sid in seat_ids
            ])
            return reservations, expires

    @staticmethod
    def create_booking(user, show, seat_ids):
        """Create a pending booking from reserved seats."""
        with transaction.atomic():
            # Get seat prices
            seat_prices = {}
            for sp in ShowSeatPrice.objects.filter(show=show):
                seat_prices[sp.category_id] = sp.price
                
            from apps.theaters.models import Seat
            seats = Seat.objects.filter(id__in=seat_ids)
            
            from decimal import Decimal
            total_amount = sum(seat_prices.get(seat.category_id, Decimal('0.00')) for seat in seats)
            booking_fee_val = getattr(settings, 'BOOKING_FEE', 20.00)
            booking_fee = Decimal(str(booking_fee_val))
            
            booking = Booking.objects.create(
                user=user,
                show=show,
                total_amount=total_amount + booking_fee,
                booking_fee=booking_fee,
                status='pending'
            )
            
            BookedSeat.objects.bulk_create([
                BookedSeat(booking=booking, seat=seat, price=seat_prices.get(seat.category_id, 0))
                for seat in seats
            ])
            
            return booking

    @staticmethod
    def confirm_booking(booking):
        """Confirm booking after successful payment."""
        from django.db.models import F
        with transaction.atomic():
            booking.status = 'confirmed'
            booking.confirmed_at = timezone.now()
            booking.save(update_fields=['status', 'confirmed_at'])
            
            # Update reservations to confirmed
            SeatReservation.objects.filter(
                show=booking.show, user=booking.user, status='held'
            ).update(status='confirmed')
            
            # Increment user's total_bookings (if model supports it)
            if hasattr(booking.user, 'total_bookings'):
                booking.user.total_bookings = F('total_bookings') + 1
                booking.user.save(update_fields=['total_bookings'])

    @staticmethod
    def cancel_booking(booking):
        """Cancel booking and release seats."""
        with transaction.atomic():
            booking.status = 'cancelled'
            booking.cancelled_at = timezone.now()
            booking.save(update_fields=['status', 'cancelled_at'])
            
            SeatReservation.objects.filter(
                show=booking.show, user=booking.user, status__in=['held', 'confirmed']
            ).update(status='released')

    @staticmethod
    def release_expired_reservations():
        """Release all expired held reservations. Called by Celery beat."""
        return SeatReservation.objects.filter(
            status='held', expires_at__lte=timezone.now()
        ).update(status='expired')
