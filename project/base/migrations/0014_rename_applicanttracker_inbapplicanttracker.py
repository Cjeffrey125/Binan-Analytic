# Generated by Django 4.2.5 on 2024-01-08 07:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_alter_collegestudentapplication_created_at'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ApplicantTracker',
            new_name='INBApplicantTracker',
        ),
    ]