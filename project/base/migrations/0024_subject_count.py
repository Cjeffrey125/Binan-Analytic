# Generated by Django 4.2.5 on 2023-12-12 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_alter_studentgrade_grade_alter_studentgrade_subject'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='count',
            field=models.IntegerField(default=0),
        ),
    ]