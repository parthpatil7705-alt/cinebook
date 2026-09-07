from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'content']

class MovieSearchForm(forms.Form):
    SORT_CHOICES = [
        ('popularity', 'Popularity'),
        ('newest', 'Newest First'),
        ('rating', 'Top Rated'),
        ('price', 'Price: Low to High'),
    ]
    q = forms.CharField(required=False)
    genre = forms.CharField(required=False)
    language = forms.CharField(required=False)
    city = forms.CharField(required=False)
    min_rating = forms.DecimalField(required=False, max_digits=3, decimal_places=1)
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False)
