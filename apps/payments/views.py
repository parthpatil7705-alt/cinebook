import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from apps.bookings.models import Booking
from apps.tickets.tasks import generate_and_email_ticket
from .models import Payment
from .services import RazorpayService

class InitiatePaymentView(LoginRequiredMixin, View):
    def post(self, request, booking_id, *args, **kwargs):
        booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
        if booking.status != 'pending':
            return JsonResponse({'error': 'Booking is not pending'}, status=400)
            
        service = RazorpayService()
        try:
            order_data = service.create_order(booking)
            return JsonResponse(order_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class PaymentCallbackView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        
        payment = get_object_or_404(Payment, razorpay_order_id=razorpay_order_id)
        
        service = RazorpayService()
        if service.verify_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'captured'
            payment.save()
            
            booking = payment.booking
            booking.status = 'confirmed'
            booking.save()
            
            transaction.on_commit(lambda: generate_and_email_ticket.delay(booking.id))
            return JsonResponse({'status': 'success'})
        else:
            payment.status = 'failed'
            payment.error_message = 'Signature verification failed'
            payment.save()
            
            booking = payment.booking
            booking.status = 'cancelled'
            booking.save()
            
            return JsonResponse({'error': 'Signature verification failed'}, status=400)

class PaymentRetryView(LoginRequiredMixin, View):
    def post(self, request, booking_id, *args, **kwargs):
        booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
        if booking.status != 'pending':
            return JsonResponse({'error': 'Booking is not pending'}, status=400)
            
        service = RazorpayService()
        try:
            order_data = service.create_order(booking)
            payment = Payment.objects.filter(booking=booking).last()
            if payment:
                payment.attempts += 1
                payment.save()
            return JsonResponse(order_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class PaymentHistoryView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'payments/payment_history.html'
    context_object_name = 'payments'
    
    def get_queryset(self):
        return Payment.objects.filter(booking__user=self.request.user).select_related('booking')

@method_decorator(csrf_exempt, name='dispatch')
class RazorpayWebhookView(View):
    def post(self, request, *args, **kwargs):
        body = request.body.decode('utf-8')
        signature = request.headers.get('x-razorpay-signature', '')
        
        service = RazorpayService()
        if not service.verify_webhook_signature(body, signature):
            return HttpResponse(status=400)
            
        try:
            event_data = json.loads(body)
            event_type = event_data.get('event')
            payload = event_data.get('payload', {}).get('payment', {}).get('entity', {})
            order_id = payload.get('order_id')
            payment_id = payload.get('id')
            
            if event_type == 'payment.captured':
                payment = Payment.objects.filter(razorpay_order_id=order_id).first()
                if payment and payment.status != 'captured':
                    payment.status = 'captured'
                    payment.razorpay_payment_id = payment_id
                    payment.save()
                    
                    booking = payment.booking
                    if booking.status != 'confirmed':
                        booking.status = 'confirmed'
                        booking.save()
                        generate_and_email_ticket.delay(booking.id)
                        
            elif event_type == 'payment.failed':
                payment = Payment.objects.filter(razorpay_order_id=order_id).first()
                if payment and payment.status != 'failed':
                    payment.status = 'failed'
                    payment.error_message = payload.get('error_description', '')
                    payment.save()
                    
            return HttpResponse(status=200)
        except Exception:
            return HttpResponse(status=400)
