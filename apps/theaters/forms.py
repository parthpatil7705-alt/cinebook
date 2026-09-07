from django import forms
from .models import City, Theater
import datetime

class ShowFilterForm(forms.Form):
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    city = forms.ModelChoiceField(queryset=City.objects.filter(is_active=True), required=False, empty_label="All Cities")
    theater = forms.ModelChoiceField(queryset=Theater.objects.filter(is_active=True), required=False, empty_label="All Theaters")
