import django_filters
from .models import CollegeStudentApplication
from django import forms

class CollegeStudentApplicationFilter(django_filters.FilterSet):

    CHOICES = (
        ('ascending', 'Ascending'),
        ('descending', 'Descending')
    )

    ordering = django_filters.ChoiceFilter(
        label='Ordering',
        choices=CHOICES,
        method='filter_by_order',
        widget=forms.Select(attrs={'class': 'your-dropdown-css-class'}),
    )

    class Meta:
        model = CollegeStudentApplication
        fields = {
            'control_number': ['icontains'],
            'last_name': ['icontains'],
        }

    def filter_by_order(self, queryset, value):
        expression = 'created' if value == 'ascending' else '-created'
        return queryset.order_by(expression)