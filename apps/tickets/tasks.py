from celery import shared_task
from django.utils import timezone
from django.core.mail import EmailMessage
from django.core.files.base import ContentFile

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_and_email_ticket(self, booking_id):
    """Generate PDF ticket and email to user. Retries up to 3 times."""
    from apps.bookings.models import Booking
    from .models import Ticket
    from .utils import generate_qr_code, generate_ticket_pdf
    
    try:
        booking = Booking.objects.select_related(
            'user', 'show__movie', 'show__screen__theater'
        ).prefetch_related('booked_seats__seat').get(id=booking_id)
        
        # Generate QR
        qr_data, qr_buffer = generate_qr_code(booking)
        
        # Generate PDF
        pdf_buffer = generate_ticket_pdf(booking)
        
        # Create/update Ticket record
        ticket, created = Ticket.objects.get_or_create(booking=booking, defaults={'qr_data': qr_data})
        ticket.pdf_file.save(f'ticket_{booking.booking_id}.pdf', ContentFile(pdf_buffer.getvalue()), save=False)
        ticket.email_attempts += 1
        ticket.last_email_attempt = timezone.now()
        
        # Send email
        body = (
            f"Hi {booking.user.first_name},\n\n"
            f"Your booking for {booking.show.movie.title} has been confirmed!\n\n"
            f"Booking ID: {booking.booking_id}\n"
            f"Theater: {booking.show.screen.theater.name}\n"
            f"Show Time: {booking.show.start_time.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"Please find your ticket attached.\n\n"
            f"Enjoy the movie!\n"
            f"CineBook Team"
        )
        email = EmailMessage(
            subject=f'Your CineBook Ticket - {booking.booking_id}',
            body=body,
            to=[booking.user.email],
        )
        email.attach(f'ticket_{booking.booking_id}.pdf', pdf_buffer.getvalue(), 'application/pdf')
        email.send()
        
        ticket.email_sent = True
        ticket.save()
        
    except Exception as exc:
        raise self.retry(exc=exc)
