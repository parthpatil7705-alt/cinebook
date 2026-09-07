import csv
from django.db.models import Sum, Count, Avg, F, Q, Value, DecimalField, FloatField
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear, ExtractHour, Coalesce
from django.utils import timezone
from datetime import timedelta
from apps.bookings.models import Booking
from apps.theaters.models import Theater
from apps.movies.models import Movie
from apps.accounts.models import CustomUser

class AnalyticsService:
    def revenue_summary(self, start_date, end_date, granularity='daily'):
        """Revenue grouped by day/week/month/year."""
        trunc_func = {
            'daily': TruncDate('created_at'),
            'weekly': TruncWeek('created_at'),
            'monthly': TruncMonth('created_at'),
            'yearly': TruncYear('created_at')
        }.get(granularity, TruncDate('created_at'))

        return list(
            Booking.objects.filter(
                created_at__range=(start_date, end_date),
                status='confirmed'
            ).annotate(period=trunc_func)
            .values('period')
            .annotate(
                revenue=Sum('total_amount'),
                booking_count=Count('id')
            ).order_by('period')
        )
    
    def total_revenue(self, start_date, end_date):
        """Single aggregate: total revenue in date range."""
        result = Booking.objects.filter(
            created_at__range=(start_date, end_date),
            status='confirmed'
        ).aggregate(total=Sum('total_amount'))
        return result['total'] or 0
    
    def booking_trends(self, start_date, end_date):
        """Daily booking counts."""
        return list(
            Booking.objects.filter(
                created_at__range=(start_date, end_date)
            ).annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
    
    def theater_occupancy(self, start_date, end_date):
        """For each theater: total capacity vs booked seats = occupancy %."""
        # Simplified: total seats in theater vs total booked seats in range
        return list(
            Theater.objects.annotate(
                total_capacity=Count('screens__seats'),
                booked_seats=Count('screens__shows__bookings__booked_seats', 
                                   filter=Q(screens__shows__bookings__created_at__range=(start_date, end_date),
                                            screens__shows__bookings__status='confirmed'))
            ).annotate(
                occupancy=Coalesce(
                    F('booked_seats') * 100.0 / F('total_capacity'),
                    0.0,
                    output_field=FloatField()
                )
            ).values('name', 'total_capacity', 'booked_seats', 'occupancy')
            .order_by('-occupancy')
        )
    
    def most_booked_movies(self, start_date, end_date, limit=10):
        """Top movies by booking count."""
        return list(
            Movie.objects.annotate(
                booking_count=Count('shows__bookings', filter=Q(shows__bookings__created_at__range=(start_date, end_date), shows__bookings__status='confirmed'))
            ).filter(booking_count__gt=0).values('title', 'booking_count').order_by('-booking_count')[:limit]
        )
    
    def top_theaters(self, start_date, end_date, limit=10):
        """Top theaters by revenue."""
        return list(
            Theater.objects.annotate(
                revenue=Sum('screens__shows__bookings__total_amount', 
                            filter=Q(screens__shows__bookings__created_at__range=(start_date, end_date), screens__shows__bookings__status='confirmed'))
            ).filter(revenue__gt=0).values('name', 'revenue').order_by('-revenue')[:limit]
        )
    
    def peak_booking_hours(self, start_date, end_date):
        """Bookings by hour of day using ExtractHour."""
        return list(
            Booking.objects.filter(
                created_at__range=(start_date, end_date)
            ).annotate(hour=ExtractHour('created_at'))
            .values('hour')
            .annotate(count=Count('id'))
            .order_by('hour')
        )
    
    def cancellation_stats(self, start_date, end_date):
        """Cancelled and refunded bookings count and amount."""
        return Booking.objects.filter(
            created_at__range=(start_date, end_date),
            status='cancelled'
        ).aggregate(
            count=Count('id'),
            amount=Sum('total_amount')
        )
    
    def user_growth(self, start_date, end_date):
        """New user registrations per day."""
        return list(
            CustomUser.objects.filter(
                date_joined__range=(start_date, end_date)
            ).annotate(date=TruncDate('date_joined'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
    
    def dashboard_summary(self, start_date, end_date):
        """Combined summary for dashboard: total revenue, total bookings, total users, avg occupancy."""
        total_rev = self.total_revenue(start_date, end_date)
        total_bkgs = Booking.objects.filter(created_at__range=(start_date, end_date), status='confirmed').count()
        total_users = CustomUser.objects.filter(date_joined__range=(start_date, end_date)).count()
        
        # Calculate avg occupancy
        occupancies = self.theater_occupancy(start_date, end_date)
        avg_occ = sum([t['occupancy'] for t in occupancies]) / len(occupancies) if occupancies else 0
        
        return {
            'total_revenue': total_rev,
            'total_bookings': total_bkgs,
            'total_new_users': total_users,
            'avg_occupancy': avg_occ,
        }
    
    def export_csv(self, report_type, start_date, end_date):
        """Generate CSV content for given report type. Returns generator for StreamingHttpResponse."""
        class Echo:
            def write(self, value):
                return value
                
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        
        if report_type == 'revenue':
            data = self.revenue_summary(start_date, end_date)
            yield writer.writerow(['Period', 'Revenue', 'Bookings'])
            for row in data:
                yield writer.writerow([row['period'], row['revenue'], row['booking_count']])
        elif report_type == 'movies':
            data = self.most_booked_movies(start_date, end_date, limit=100)
            yield writer.writerow(['Movie Title', 'Bookings'])
            for row in data:
                yield writer.writerow([row['title'], row['booking_count']])
        else:
            yield writer.writerow(['Report type not supported'])
