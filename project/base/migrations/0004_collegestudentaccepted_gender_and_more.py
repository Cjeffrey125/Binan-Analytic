# Generated by Django 4.2.5 on 2024-01-06 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_applicantinforepositoryinb_school_year_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='collegestudentaccepted',
            name='gender',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='collegestudentaccepted',
            name='year',
            field=models.IntegerField(default=2024),
        ),
    ]
