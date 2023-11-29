# Generated by Django 4.2.6 on 2023-10-30 05:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicantInfoRepositoryINB',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('control_number', models.CharField(max_length=50, unique=True)),
                ('status', models.CharField(choices=[('Accepted', 'Accepted'), ('Rejected', 'Rejected')], max_length=20)),
                ('fullname', models.CharField(default='', max_length=250)),
                ('address', models.CharField(default='Unknown', max_length=100)),
                ('gender', models.CharField(max_length=50)),
                ('date_of_birth', models.DateField(default='2001-01-01')),
                ('place_of_birth', models.CharField(default='', max_length=100)),
                ('contact_no', models.CharField(default='', max_length=25)),
                ('email_address', models.EmailField(default='', max_length=100)),
                ('school', models.CharField(default='', max_length=100)),
                ('course', models.CharField(default='', max_length=100)),
                ('gwa', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('rank', models.IntegerField(default=0)),
                ('jhs', models.CharField(default='', max_length=100)),
                ('jhs_address', models.CharField(default='', max_length=100)),
                ('jhs_educational_provider', models.CharField(default='', max_length=100)),
                ('shs', models.CharField(default='', max_length=100)),
                ('shs_address', models.CharField(default='', max_length=100)),
                ('shs_educational_provider', models.CharField(default='', max_length=100)),
                ('father_voter_status', models.CharField(default='', max_length=100)),
                ('father_name', models.CharField(default='', max_length=100)),
                ('father_educational_attainment', models.CharField(default='', max_length=100)),
                ('father_occupation', models.CharField(default='', max_length=100)),
                ('father_employer', models.CharField(default='', max_length=100)),
                ('mother_voter_status', models.CharField(default='', max_length=100)),
                ('mother_name', models.CharField(default='', max_length=100)),
                ('mother_educational_attainment', models.CharField(default='', max_length=100)),
                ('mother_occupation', models.CharField(default='', max_length=100)),
                ('mother_employer', models.CharField(default='', max_length=100)),
                ('guardian_voter_status', models.CharField(default='', max_length=100)),
                ('guardian_name', models.CharField(default='', max_length=100)),
                ('guardian_educational_attainment', models.CharField(default='', max_length=100)),
                ('guardian_occupation', models.CharField(default='', max_length=100)),
                ('guardian_employer', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CollegeStudentAccepted',
            fields=[
                ('control_number', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('fullname', models.CharField(max_length=50)),
                ('school_year', models.CharField(default='1st Years', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='CollegeStudentApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('control_number', models.CharField(max_length=50, unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(default='', max_length=50)),
                ('address', models.CharField(default='Unknown', max_length=100)),
                ('gender', models.CharField(max_length=50)),
                ('date_of_birth', models.DateField(default='01-01-2001')),
                ('place_of_birth', models.CharField(default='', max_length=100)),
                ('contact_no', models.CharField(default='', max_length=25)),
                ('email_address', models.EmailField(default='', max_length=100)),
                ('school', models.CharField(default='', max_length=100)),
                ('course', models.CharField(default='', max_length=100)),
                ('gwa', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('rank', models.IntegerField(default=0)),
                ('jhs', models.CharField(default='', max_length=100)),
                ('jhs_address', models.CharField(default='', max_length=100)),
                ('jhs_educational_provider', models.CharField(default='', max_length=100)),
                ('shs', models.CharField(default='', max_length=100)),
                ('shs_address', models.CharField(default='', max_length=100)),
                ('shs_educational_provider', models.CharField(default='', max_length=100)),
                ('father_voter_status', models.CharField(default='', max_length=100)),
                ('father_name', models.CharField(default='', max_length=100)),
                ('father_educational_attainment', models.CharField(default='', max_length=100)),
                ('father_occupation', models.CharField(default='', max_length=100)),
                ('father_employer', models.CharField(default='', max_length=100)),
                ('mother_voter_status', models.CharField(default='', max_length=100)),
                ('mother_name', models.CharField(default='', max_length=100)),
                ('mother_educational_attainment', models.CharField(default='', max_length=100)),
                ('mother_occupation', models.CharField(default='', max_length=100)),
                ('mother_employer', models.CharField(default='', max_length=100)),
                ('guardian_voter_status', models.CharField(default='', max_length=100)),
                ('guardian_name', models.CharField(default='', max_length=100)),
                ('guardian_educational_attainment', models.CharField(default='', max_length=100)),
                ('guardian_occupation', models.CharField(default='', max_length=100)),
                ('guardian_employer', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CollegeStudentRejected',
            fields=[
                ('control_number', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('fullname', models.CharField(max_length=50)),
                ('remarks', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='FinancialAssistanceApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('control_number', models.CharField(max_length=50, unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(default='', max_length=50)),
                ('suffix', models.CharField(default='', max_length=50)),
                ('date_of_birth', models.DateField(default='01-01-2001')),
                ('place_of_birth', models.CharField(default='', max_length=100)),
                ('gender', models.CharField(max_length=50)),
                ('religion', models.CharField(default='', max_length=100)),
                ('address', models.CharField(default='Unknown', max_length=100)),
                ('email_address', models.EmailField(default='', max_length=100)),
                ('contact_no', models.CharField(default='', max_length=25)),
                ('general_average', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('school', models.CharField(default='', max_length=100)),
                ('school_address', models.CharField(default='', max_length=100)),
                ('track', models.CharField(default='', max_length=100)),
                ('strand', models.CharField(default='', max_length=100)),
                ('father_name', models.CharField(default='', max_length=100)),
                ('father_age', models.SmallIntegerField(default='')),
                ('father_occupation', models.CharField(default='', max_length=100)),
                ('father_employer', models.CharField(default='', max_length=100)),
                ('father_income', models.IntegerField(default='')),
                ('mother_name', models.CharField(default='', max_length=100)),
                ('mother_age', models.SmallIntegerField(default='')),
                ('mother_occupation', models.CharField(default='', max_length=100)),
                ('mother_employer', models.CharField(default='', max_length=100)),
                ('mother_income', models.IntegerField(default='')),
                ('sibling_count', models.SmallIntegerField(default='')),
                ('sibling_name', models.CharField(default='', max_length=100)),
                ('sibling_DOB', models.DateField(default='01-01-2001')),
                ('sibling_age', models.SmallIntegerField(default=0)),
                ('sibling_address', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CollegeRequirements',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('control_number', models.CharField(default='', max_length=50)),
                ('requirement', models.IntegerField(default=0)),
                ('req_a', models.CharField(default='False', max_length=100)),
                ('req_b', models.CharField(default='False', max_length=100)),
                ('req_c', models.CharField(default='False', max_length=100)),
                ('req_d', models.CharField(default='False', max_length=100)),
                ('req_e', models.CharField(default='False', max_length=100)),
                ('req_f', models.CharField(default='False', max_length=100)),
                ('req_g', models.CharField(default='False', max_length=100)),
                ('req_h', models.CharField(default='False', max_length=100)),
                ('req_i', models.CharField(default='False', max_length=100)),
                ('req_j', models.CharField(default='False', max_length=100)),
                ('req_k', models.CharField(default='False', max_length=100)),
                ('req_l', models.CharField(default='False', max_length=100)),
                ('req_m', models.CharField(default='False', max_length=100)),
                ('approved', models.BooleanField(default=False)),
                ('control', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.collegestudentapplication')),
            ],
        ),
    ]
