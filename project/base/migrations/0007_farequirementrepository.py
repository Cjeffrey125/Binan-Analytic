# Generated by Django 4.2.7 on 2023-11-26 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_inbrequirementrepository'),
    ]

    operations = [
        migrations.CreateModel(
            name='FARequirementRepository',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('requirement', models.CharField(default='', max_length=500)),
            ],
        ),
    ]
