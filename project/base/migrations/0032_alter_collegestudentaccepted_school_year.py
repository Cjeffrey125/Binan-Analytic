# Generated by Django 4.2.7 on 2023-12-13 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0031_alter_collegestudentaccepted_school_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collegestudentaccepted',
            name='school_year',
            field=models.CharField(default='1st Year', max_length=50),
        ),
    ]