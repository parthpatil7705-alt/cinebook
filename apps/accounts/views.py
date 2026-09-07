from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView, UpdateView, ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, UserProfileForm, LoginForm
from apps.bookings.models import Booking

class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('movies:home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['recent_bookings'] = Booking.objects.filter(user=self.request.user).order_by('-created_at')[:5]
        except Exception:
            context['recent_bookings'] = []
        return context

class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/profile_edit.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

class BookingHistoryView(LoginRequiredMixin, ListView):
    template_name = 'accounts/booking_history.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        try:
            return Booking.objects.filter(user=self.request.user).order_by('-created_at')
        except Exception:
            return []

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    
    def get_success_url(self):
        return super().get_success_url()

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')
