# Generated by Django 4.2.5 on 2024-01-08 04:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_remove_collegestudentapplication_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='collegestudentapplication',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]