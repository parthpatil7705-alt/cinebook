import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.views.generic import TemplateView, View
from django.http import JsonResponse, StreamingHttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .services import AnalyticsService

@method_decorator(staff_member_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'analytics/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_str = self.request.GET.get('date_start')
        end_str = self.request.GET.get('date_end')
        
        if start_str and end_str:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            end_date = datetime.strptime(end_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        else:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
            
        service = AnalyticsService()
        
        context['date_start'] = start_date.strftime('%Y-%m-%d')
        context['date_end'] = end_date.strftime('%Y-%m-%d')
        context['summary'] = service.dashboard_summary(start_date, end_date)
        context['cancellation_stats'] = service.cancellation_stats(start_date, end_date)
        
        # Serialize data for charts
        def default_serializer(obj):
            if isinstance(obj, datetime) or hasattr(obj, 'isoformat'):
                return obj.isoformat()
            import decimal
            if isinstance(obj, decimal.Decimal):
                return float(obj)
            return str(obj)
            
        context['revenue_data'] = json.dumps(service.revenue_summary(start_date, end_date, 'daily'), default=default_serializer)
        context['trends_data'] = json.dumps(service.booking_trends(start_date, end_date), default=default_serializer)
        context['movies_data'] = json.dumps(service.most_booked_movies(start_date, end_date), default=default_serializer)
        context['occupancy_data'] = json.dumps(service.theater_occupancy(start_date, end_date), default=default_serializer)
        context['peak_hours_data'] = json.dumps(service.peak_booking_hours(start_date, end_date), default=default_serializer)
        context['user_growth_data'] = json.dumps(service.user_growth(start_date, end_date), default=default_serializer)
        
        return context

@method_decorator(staff_member_required, name='dispatch')
class ExportCSVView(View):
    def get(self, request, *args, **kwargs):
        report_type = request.GET.get('report_type', 'revenue')
        start_str = request.GET.get('date_start')
        end_str = request.GET.get('date_end')
        
        if start_str and end_str:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            end_date = datetime.strptime(end_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        else:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
            
        service = AnalyticsService()
        response = StreamingHttpResponse(
            service.export_csv(report_type, start_date, end_date),
            content_type="text/csv"
        )
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{start_date.date()}_to_{end_date.date()}.csv"'
        return response
