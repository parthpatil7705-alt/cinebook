from celery import shared_task

@shared_task
def expire_stale_reservations():
    from .services import BookingService
    count = BookingService.release_expired_reservations()
    return f'Expired {count} reservations'
