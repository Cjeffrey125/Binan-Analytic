# Generated by Django 4.2.7 on 2023-12-20 05:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0032_alter_collegestudentaccepted_school_year'),
    ]

    operations = [
        migrations.RenameField(
            model_name='financialassistanceaccepted',
            old_name='course',
            new_name='strand',
        ),
        migrations.RenameField(
            model_name='financialassistanceassesment',
            old_name='course',
            new_name='strand',
        ),
    ]