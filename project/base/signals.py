from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth import get_user_model
from .models import LogEntry, CollegeStudentApplication

User = get_user_model()

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    log_action = f"User {user.username} logged in"
    LogEntry.objects.create(
        action=log_action,
        staff=user,
        staff_username=user.username 
    )

@receiver(post_save, sender=CollegeStudentApplication)
def applicant_added_handler(sender, instance, created, **kwargs):
    if created:
        user = kwargs.get('request').user if 'request' in kwargs else None
        log_action = f"Added '{instance.control_number}' in INB Applicant List"

        unknown_user, created = User.objects.get_or_create(username='UnknownUser')
        staff_user = user if user and user.is_authenticated else unknown_user

        LogEntry.objects.create(
            action=log_action,
            staff=staff_user,
            staff_username=staff_user.username  
        )

