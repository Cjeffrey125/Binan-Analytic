# Generated by Django 4.2.5 on 2024-01-07 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_collegestudentaccepted_barangay'),
    ]

    operations = [
        migrations.AddField(
            model_name='collegestudentaccepted',
            name='status',
            field=models.CharField(default='Ongoing', max_length=100),
        ),
    ]