from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth import get_user_model
from .models import LogEntry, CollegeStudentApplication
from .views import applicant_added_signal

User = get_user_model()

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    log_action = f"User {user.username} logged in"
    LogEntry.objects.create(
        action=log_action,
        staff=user,
        staff_username=user.username 
    )

@receiver(applicant_added_signal)
def applicant_added_handler(sender, instance, created, username, **kwargs):
    if created:
        log_action = f"Added '{instance.control_number}' in INB Applicant List"

        staff_user = User.objects.get(username=username)

        LogEntry.objects.create(
            action=log_action,
            staff=staff_user,
            staff_username=staff_user.username  
        )
