# Generated by Django 4.2.7 on 2023-12-10 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_alter_applicantinforepositoryinb_father_voter_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicantinforepositoryinb',
            name='father_voter_status',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='applicantinforepositoryinb',
            name='guardian_voter_status',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='applicantinforepositoryinb',
            name='mother_voter_status',
            field=models.CharField(default='', max_length=100),
        ),
    ]