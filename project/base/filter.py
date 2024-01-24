import django_filters
from .models import CollegeStudentApplication

class TableFilter(django_filters.FilterSet):
    requirement = django_filters.CharFilter(field_name='requirement__acronym', lookup_expr='exact')

    school = django_filters.CharFilter(field_name='school__name', lookup_expr='exact')

    course = django_filters.CharFilter(field_name='course__name', lookup_expr='exact')

    gender = django_filters.CharFilter(field_name='gender__name', lookup_expr='exact')

    class Meta:
        model = CollegeStudentApplication
        fields = ['school', 'course', 'gender', 'requirement']
