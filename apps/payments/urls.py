from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/<str:booking_id>/', views.InitiatePaymentView.as_view(), name='initiate'),
    path('callback/', views.PaymentCallbackView.as_view(), name='callback'),
    path('retry/<str:booking_id>/', views.PaymentRetryView.as_view(), name='retry'),
    path('history/', views.PaymentHistoryView.as_view(), name='payment_history'),
    path('webhook/razorpay/', views.RazorpayWebhookView.as_view(), name='webhook'),
]

