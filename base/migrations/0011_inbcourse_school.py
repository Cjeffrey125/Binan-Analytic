# Generated by Django 4.2.7 on 2023-12-02 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_remove_inbcourse_school'),
    ]

    operations = [
        migrations.AddField(
            model_name='inbcourse',
            name='school',
            field=models.ManyToManyField(to='base.inbschool'),
        ),
    ]
