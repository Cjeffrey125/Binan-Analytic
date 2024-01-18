from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from project.forms import (
    SignUpForm,
    AddINBForm,
    ExportForm,
    ApplicantUploadForm,
    AddFinancialAssistanceForm,
    INBRequirementList,
    FARequirementList,
    INBSchoolForm,
    INBCourseForm,
    GradeUploadForm,
    INBPendingApplicants,
    UpdateUserForm,
    ProfileImageForm,
    FAPendingApplicants,
)
from .models import (
    CollegeStudentApplication,
    CollegeStudentAccepted,
    CollegeStudentAssesment,
    CollegeStudentRejected,
    ApplicantInfoRepositoryINB,
    FinancialAssistanceApplication,
    FinancialAssistanceAccepted,
    FinancialAssistanceAssesment,
    FinancialAssistanceRejected,
    FinancialAssistanceInfoRepository,
    INBRequirementRepository,
    FARequirementRepository,
    INBSchool,
    INBCourse,
    StudentGrade,
    INBApplicationRequirements,
    FAApplicationRequirements,
    INBApplicantTracker,
    ProfileImage,
    LogEntry,
    StudentGradeRepository
)
from django.db.models import Count
from django.http import HttpResponse
import csv
import pandas as pd
from import_export import resources
from django.db.models import Q
import datetime
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db import IntegrityError
from django.contrib import messages
from django.http import JsonResponse


def logger(request):
    logs = LogEntry.objects.all()
    return render(request, "admin/logger.html", {"logs": logs})


# ------------------------------------------------------------------------

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.conf import settings
from django.template.loader import get_template
from django.urls import reverse


def generate_permit_pdf(permits):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)

    textob = c.beginText()
    textob.setTextOrigin(100, 700)
    textob.setFont("Helvetica", 14)

    for permit in permits:
        lines = [
            f"Control Number: {permit.control_number}",
            f"Full Name: {permit.fullname}",
            f"School Year: {permit.school_year}",
            f"Course: {permit.course}",
            f"School: {permit.school}",
            f"Grant: {permit.grant}",
            f"Semester: {permit.semester}",
        ]

        for line in lines:
            textob.textLine(line)

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return buf


def print_permit_view(request):
    get_permit = CollegeStudentAccepted.objects.all()
    pdf_buffer = generate_permit_pdf(get_permit)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="INB-Permit.pdf"'
    response.write(pdf_buffer.read())

    return response


def print_view(request):
    get_permit = CollegeStudentAccepted.objects.all()
    context = {"permits": get_permit}
    return render(request, "print_permit.html", context)


class CollegeStudentApplicationResource(resources.ModelResource):
    class Meta:
        model = CollegeStudentApplication
        import_id_fields = ("Control Number",)


def home(request):
    return render(request, "home.html", {})


def check_control_number(request):
    control_number = request.GET.get("control_number", None)
    data = {
        "is_taken": CollegeStudentApplication.objects.filter(
            control_number__iexact=control_number
        ).exists()
    }
    return JsonResponse(data)


# import ----------------------------------------------------------------------------------------------------------------------------------
# problem fk nan&update



def import_excel(request):
    if request.method == "POST":
        form = ApplicantUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            try:
                df = pd.read_excel(file, na_values=["N/A", "-", "Not Available"])

                required_headers = ["Control Number", "School Year", "Surname", "Firstname", "Middlename", "Blk Street",
                                    "Barangay", "Province", "City", "Gender", "Date of Birth", "Place of Birth",
                                    "Contact No.", "Email Address", "Preferred School", "Desired Course", "GWA",
                                    "Rank", "JHS", "JHS Address", "JHS Education Provider", "SHS", "SHS Address",
                                    "SHS Education Provider", "Father Name", "Father Voter Status",
                                    "Father Educational Attainment", "Father Employer", "Father Occupation",
                                    "Mother Name", "Mother Voter Status", "Mother Educational Attainment",
                                    "Mother Employer", "Mother Occupation", "Legal Guardian", "Guardian Voter Status",
                                    "Guardian Educational Attainment", "Guardian Employer", "Guardian Occupation"]

                for header in required_headers:
                    if header not in df.columns:
                        messages.error(request, f"The file does not contain the right information. Invalid file")
                        return redirect("inb_applicant_list")

                df = df.fillna("N/A")
                date_columns = ["Date of Birth"]
                for col in date_columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

                applicant_count = 0

                for index, row in df.iterrows():
                    try:
                        if "Desired Course" in df.columns:
                            applicant = CollegeStudentApplication(
                                control_number=row["Control Number"],
                                school_year=row["School Year"],
                                last_name=row["Surname"],
                                first_name=row["Firstname"],
                                middle_name=row["Middlename"],
                                blkstr=row["Blk Street"],
                                barangay=row["Barangay"],
                                province=row["Province"],
                                city=row["City"],
                                gender=row["Gender"],
                                date_of_birth=row["Date of Birth"],
                                place_of_birth=row["Place of Birth"],
                                contact_no=row["Contact No."],
                                email_address=row["Email Address"],
                                school=row["Preferred School"],
                                course=row["Desired Course"],
                                gwa=row["GWA"],
                                rank=row["Rank"],
                                jhs=row["JHS"],
                                jhs_address=row["JHS Address"],
                                jhs_educational_provider=row["JHS Education Provider"],
                                shs=row["SHS"],
                                shs_address=row["SHS Address"],
                                shs_educational_provider=row["SHS Education Provider"],
                                father_name=row["Father Name"],
                                father_voter_status=row["Father Voter Status"],
                                father_educational_attainment=row["Father Educational Attainment"],
                                father_employer=row["Father Employer"],
                                father_occupation=row["Father Occupation"],
                                mother_name=row["Mother Name"],
                                mother_voter_status=row["Mother Voter Status"],
                                mother_educational_attainment=row["Mother Educational Attainment"],
                                mother_employer=row["Mother Employer"],
                                mother_occupation=row["Mother Occupation"],
                                guardian_name=row["Legal Guardian"],
                                guardian_voter_status=row["Guardian Voter Status"],
                                guardian_educational_attainment=row["Guardian Educational Attainment"],
                                guardian_employer=row["Guardian Employer"],
                                guardian_occupation=row["Guardian Occupation"],
                            )

                            messages.success(
                                request,
                                f"{applicant_count} applicant(s) imported successfully.",
                            )
                        else:
                            sibling_count = row["Sibling Count"]
                            if pd.isna(sibling_count) or sibling_count == 0:
                                messages.warning(
                                    request,
                                    f'Entry for {row["Control Number"]} has sibling_count 0 or N/A. Imported with default values.',
                                )
                            applicant = FinancialAssistanceApplication(
                                control_number=row["Control Number"],
                                first_name=row["Firstname"],
                                middle_name=row["Middlename"],
                                last_name=row["Surname"],
                                suffix=row["Suffix"],
                                date_of_birth=row["Date of Birth"],
                                place_of_birth=row["Place of Birth"],
                                gender=row["Gender"],
                                religion=row["Religion"],
                                blkstr=row["Blk Street"],
                                barangay=row["Barangay"],
                                city=row["City"],
                                province=row["Province"],
                                email_address=row["Email Address"],
                                contact_no=row["Contact No."],
                                general_average=row["GWA"],
                                school=row["School"],
                                school_address=row["School Address"],
                                track=row["Track"],
                                strand=row["Strand"],
                                father_name=row["Father Name"],
                                father_age=row["Father Age"],
                                father_occupation=row["Father Occupation"],
                                father_employer=row["Father Employer"],
                                father_income=row["Father Income"],
                                mother_name=row["Mother Name"],
                                mother_age=row["Mother Age"],
                                mother_occupation=row["Mother Occupation"],
                                mother_employer=row["Mother Employer"],
                                mother_income=row["Mother Income"],
                                sibling_count=row["Sibling Count"],
                                a_sibling_name=row["Sibling Name"],
                                a_sibling_DOB=row["Sibling Date of Birth"],
                                a_sibling_age=row["Sibling Age"],
                                a_sibling_address=row["Sibling Address"],
                                b_sibling_name=row["Sibling Name"],
                                b_sibling_DOB=row["Sibling Date of Birth"],
                                b_sibling_age=row["Sibling Age"],
                                b_sibling_address=row["Sibling Address"],
                                c_sibling_name=row["Sibling Name"],
                                c_sibling_DOB=row["Sibling Date of Birth"],
                                c_sibling_age=row["Sibling Age"],
                                c_sibling_address=row["Sibling Address"],
                                d_sibling_name=row["Sibling Name"],
                                d_sibling_DOB=row["Sibling Date of Birth"],
                                d_sibling_age=row["Sibling Age"],
                                d_sibling_address=row["Sibling Address"],
                                e_sibling_name=row["Sibling Name"],
                                e_sibling_DOB=row["Sibling Date of Birth"],
                                e_sibling_age=row["Sibling Age"],
                                e_sibling_address=row["Sibling Address"],
                            )
                        applicant.save()
                        applicant_count += 1
                    except IntegrityError:
                        messages.warning(
                            request,
                            f'Duplicate entry found for {row["Control Number"]}. Skipped.',
                        )

                if "Desired Course" not in df.columns:
                    return redirect("fa_applicant_list")

                return redirect("inb_applicant_list")

            except Exception as e:
                messages.error(request, f"An error occurred during the import process. Please check your data and try again. Error: {str(e)}")

    else:
        form = ApplicantUploadForm()
    return render(request, "INB/import.html", {"form": form})



# ---------------------------------------------------------------------------------------------------------------------------------------


# export ----------------------------------------------------------------------------------------------------------------------------------


def csv_record(request):
    if request.method == "POST":
        export_form = ExportForm(request.POST)

        if export_form.is_valid():
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=record.csv"

            writer = csv.writer(response)

            include_id = export_form.cleaned_data.get("include_id", False)
            include_name = export_form.cleaned_data.get("include_name", False)
            include_course = export_form.cleaned_data.get("include_course", False)
            include_school = export_form.cleaned_data.get("include_school", False)

            headers = []
            if include_id:
                headers.append("ID")
            if include_name:
                headers.append("Name")
            if include_course:
                headers.append("Course")
            if include_school:
                headers.append("School")

            writer.writerow(headers)

            records = CollegeStudentApplication.objects.all()

            for record in records:
                row = []
                if include_id:
                    row.append(record.id)
                if include_name:
                    row.append(str(record))
                if include_course:
                    row.append(record.course)
                if include_school:
                    row.append(record.school)

                writer.writerow(row)

            return response
    else:
        export_form = ExportForm()

    return render(request, "INB/export_form.html", {"export_form": export_form})


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Login  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
from django.contrib.auth.forms import PasswordChangeForm


def user_settings(request):
    user = request.user

    profile_image_instance, created = ProfileImage.objects.get_or_create(
        user=request.user
    )
    if request.method == "POST":
        form = ProfileImageForm(
            request.POST, request.FILES, instance=profile_image_instance
        )
        if form.is_valid():
            form.save()
            return redirect("user_setting")
    else:
        form = ProfileImageForm(instance=profile_image_instance)

    return render(request, "user-settings.html", {"user": user, "form": form})


def update_user(request):
    if request.method == "POST":
        form = UpdateUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("user_setting")
    else:
        form = UpdateUserForm(instance=request.user)

    return render(request, "update-user.html", {"form": form})


def login_user(request):
    if request.method == "POST":
        try:
            username = request.POST["username"]
            password = request.POST["user_password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("inb-dashboard")
            else:
                messages.error(request, "Incorrect username or password.")
        except MultiValueDictKeyError:
            messages.error(request, "Please provide a username.")
            return render(request, "login.html")
    return render(request, "login.html")


def logout_user(request):
    logout(request)
    messages.success(request, "You have been Logged Out")
    return render(request, "home.html", {})


def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Account Successfully Registered")
            return redirect("home")
    else:
        form = SignUpForm()
        return render(request, "signup.html", {"form": form})

    return render(request, "signup.html", {"form": form})


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# dashboardo
from django.db.models import Count
from django.db import models


def fa_data_visualization(request):
    return render(
        request,
        "fa-dashboard.html",
    )


def inb_data_visualization(request):
    applicant_courses = (
        CollegeStudentAccepted.objects.exclude(status="Graduated")
        .exclude(school_year="Graduated")
        .values("course")
        .annotate(count=Count("course"))
        .order_by("-count")
    )

    school_counts = (
        CollegeStudentAccepted.objects.exclude(status="Graduated")
        .exclude(school_year="Graduated")
        .values("school")
        .annotate(count=Count("school"))
        .order_by("-count")
    )

    barangay_counts = (
        CollegeStudentAccepted.objects.exclude(status="Graduated")
        .exclude(school_year="Graduated")
        .values("barangay")
        .annotate(count=Count("barangay"))
        .order_by("-count")
    )

    first_year_count = CollegeStudentAccepted.objects.filter(
        school_year="1st Year", status="Ongoing"
    ).count()
    second_year_count = CollegeStudentAccepted.objects.filter(
        school_year="2nd Year", status="Ongoing"
    ).count()
    third_year_count = CollegeStudentAccepted.objects.filter(
        school_year="3rd Year", status="Ongoing"
    ).count()
    fourth_year_count = CollegeStudentAccepted.objects.filter(
        school_year="4th Year", status="Ongoing"
    ).count()
    fifth_year_count = CollegeStudentAccepted.objects.filter(
        school_year="5th Year", status="Ongoing"
    ).count()

    total_scholars_count = CollegeStudentAccepted.objects.count()

    graduated_scholars_count = CollegeStudentAccepted.objects.filter(
        school_year="Graduated"
    ).count()
    ongoing_scholars_count = (
        CollegeStudentAccepted.objects.filter(status="Ongoing")
        .exclude(school_year="Graduated")
        .count()
    )

    rejected_scholars_count = CollegeStudentRejected.objects.count()
    unsuccessful_scholar_count = CollegeStudentAccepted.objects.filter(
        status="Failed"
    ).count()

    total_failed_applicants = rejected_scholars_count + unsuccessful_scholar_count

    percentage_ongoing = (
        (ongoing_scholars_count / total_scholars_count) * 100
        if total_scholars_count > 0
        else 0
    )

    gender_data = (
        CollegeStudentAccepted.objects.filter(status="Ongoing")
        .values("gender")
        .annotate(count=models.Count("gender"))
    )

    labels = [entry["gender"] for entry in gender_data]
    counts = [entry["count"] for entry in gender_data]

    context = {
        "applicant_courses": applicant_courses,
        "customLabels": [entry["school"] for entry in school_counts],
        "dataCounts": [entry["count"] for entry in school_counts],
        "barangay_counts": barangay_counts,
        "first_year_count": first_year_count,
        "second_year_count": second_year_count,
        "third_year_count": third_year_count,
        "fourth_year_count": fourth_year_count,
        "fifth_year_count": fifth_year_count,
        "graduated_scholars_count": graduated_scholars_count,
        "total_failed_applicants": total_failed_applicants,
        "ongoing_scholars_count": ongoing_scholars_count,
        "percentage_ongoing": percentage_ongoing,
        "labels": labels,
        "counts": counts,
    }

    return render(request, "inb-dashboard.html", context)


from django.db.models import Sum, F

def graduate_scholar_summary(request):
  
    graduated_data = CollegeStudentAccepted.objects.filter(
        school_year='Graduated'
    ).values('created_at__year', 'school').annotate(graduates_count=Count('control_number'))

    unique_years = set(entry["created_at__year"] for entry in graduated_data)
    unique_years_list = sorted(unique_years)

    context = {
        'graduated_data': graduated_data,
        'unique_years_list': unique_years_list
    }

    return render(request, "in-depth-charts/graduated-scholar/graduated-scholar.html", context)


def barangay_summary(request):
    return render(request, "in-depth-charts/barangay/barangay_data.html")

def unsuccessful_scholar_summary(request):
    return render(
        request, "in-depth-charts/unsuccessful-scholar/unsuccessful-scholar.html"
    )


def tracker_scholar_summary(request):
    return render(request, "in-depth-charts/tracker-count/tracket-count.html")




from django.db.models import Count

def school_scholar_summary(request):
    courses = (
        CollegeStudentAccepted.objects.exclude(status="Graduated")
        .exclude(school_year="Graduated")
        .values("course")
        .annotate(count=Count("course"))
        .order_by("-count")
    )

    schools = (
        CollegeStudentAccepted.objects.exclude(status="Graduated")
        .exclude(school_year="Graduated")
        .values("school")
        .annotate(count=Count("school"))
        .order_by("-count")
    )

    unique_schools_data = CollegeStudentAccepted.objects.values('school').distinct()

    schools_with_courses = []

    for school_data in unique_schools_data:
        school_courses_data = CollegeStudentAccepted.objects.filter(
            school=school_data['school']
        ).exclude(
            school_year='Graduated'
        ).values('course').annotate(student_count=Count('control_number'))

        if school_courses_data:
            course_info = {
                'school': school_data['school'],
                'courses': list(school_courses_data)
            }

            schools_with_courses.append(course_info)

    custom_labels = [course['course'] for school_info in schools_with_courses for course in school_info['courses']]

    data_counts = []

    for school_info in schools_with_courses:
        counts_per_school = [0] * len(custom_labels)

        for course_data in school_info['courses']:
            course_index = custom_labels.index(course_data['course'])
            counts_per_school[course_index] = course_data['student_count']

        data_counts.append(counts_per_school)

    return render(request, "in-depth-charts/school-grantees/school-grantees.html", {
        'schools_with_courses': schools_with_courses,
        'custom_labels': custom_labels,
        'data_counts': data_counts,

        "customLabel": [entry["school"] for entry in schools],
        "dataCounts": [entry["count"] for entry in courses],
    })



def course_scholar_summary(request):
    courses_data = (
        CollegeStudentAccepted.objects.exclude(status="Graduated")
        .exclude(school_year="Graduated")
        .values("course")
        .annotate(student_count=Count('control_number'))
        .order_by("-student_count")
    )

    custom_labels = [entry["course"] for entry in courses_data]
    data_counts = [entry["student_count"] for entry in courses_data]

    return render(request, "in-depth-charts/course-grantees/course-grantees.html", {
        'customLabels': custom_labels,
        'dataCounts': data_counts,
    })


def yearlevel_scholar_summary(request):
    

    first_year_count = CollegeStudentAccepted.objects.filter(
        school_year="1st Year", status="Ongoing"
    ).count()
    second_year_count = CollegeStudentAccepted.objects.filter(
        school_year="2nd Year", status="Ongoing"
    ).count()
    third_year_count = CollegeStudentAccepted.objects.filter(
        school_year="3rd Year", status="Ongoing"
    ).count()
    fourth_year_count = CollegeStudentAccepted.objects.filter(
        school_year="4th Year", status="Ongoing"
    ).count()
    fifth_year_count = CollegeStudentAccepted.objects.filter(
        school_year="5th Year", status="Ongoing"
    ).count()

    year_levels = ["1st Year", "2nd Year", "3rd Year", "4th Year", "5th Year"]

    schools = CollegeStudentAccepted.objects.values('school').distinct()

    school_year_counts = {}

    for school_data in schools:
        school = school_data['school']
        school_year_counts[school] = {}
        for year_level in year_levels:
            count = CollegeStudentAccepted.objects.filter(
                school_year=year_level, status="Ongoing", school=school
            ).count()
            school_year_counts[school][year_level] = count

    context = {
        "first_year_count": first_year_count,
        "second_year_count": second_year_count,
        "third_year_count": third_year_count,
        "fourth_year_count": fourth_year_count,
        "fifth_year_count": fifth_year_count,
        "school_year_counts": school_year_counts,
    }

    return render(request, "in-depth-charts/year-tracker/year-tracker.html", context)

   

def active_scholar_summary(request):
    graduated_data = CollegeStudentAccepted.objects.filter(
        school_year='Graduated'
    ).values('created_at__year', 'school').annotate(graduates_count=Count('control_number'))

    unique_years = set(entry["created_at__year"] for entry in graduated_data)
    unique_years_list = sorted(unique_years)

    unique_schools = set(entry["school"] for entry in graduated_data)
    unique_schools_list = sorted(unique_schools)

    context = {
        'graduated_data': graduated_data,
        'unique_years_list': unique_years_list,
        'unique_schools_list': unique_schools_list,
    }

    return render(request, "in-depth-charts/active-scholar/active_scholar.html", context)
   



def gender_summary(request):
    gender_data = (
        CollegeStudentAccepted.objects.filter(status="Ongoing")
        .values("gender")
        .annotate(count=models.Count("gender"))
    )

    labels = [entry["gender"] for entry in gender_data]
    counts = [entry["count"] for entry in gender_data]

    unique_school_years = [
        "1st Year",
        "2nd Year",
        "3rd Year",
        "4th Year",
        "5th Year",
        "Graduated",
    ]

    gender_table_data = []

    for year in unique_school_years:
        year_data = (
            CollegeStudentAccepted.objects.filter(status="Ongoing", school_year=year)
            .values("gender")
            .annotate(count=Count("gender"))
            .order_by("gender")
        )
        gender_table_data.append(
            {
                "year": year,
                "labels": [entry["gender"] for entry in year_data],
                "counts": [entry["count"] for entry in year_data],
            }
        )

    total_male_count = sum(
        entry["counts"][0] if entry["counts"] else 0 for entry in gender_table_data
    )
    total_female_count = sum(
        entry["counts"][1] if len(entry["counts"]) > 1 else 0
        for entry in gender_table_data
    )

    gender_data_creation_year = CollegeStudentAccepted.objects.values(
        "gender", "created_at__year"
    ).annotate(count=models.Count("gender"))

    unique_years = set(entry["created_at__year"] for entry in gender_data_creation_year)
    unique_years = sorted(unique_years)[-4:]

    gender_table_data_creation_year = []

    for year in unique_years:
        year_data = gender_data_creation_year.filter(
            status="Ongoing", created_at__year=year
        ).order_by("gender")
        male_count = (
            year_data.filter(gender="Male").first()["count"]
            if year_data.filter(gender="Male").exists()
            else 0
        )
        female_count = (
            year_data.filter(gender="Female").first()["count"]
            if year_data.filter(gender="Female").exists()
            else 0
        )
        gender_table_data_creation_year.append(
            {"year": year, "male_count": male_count, "female_count": female_count}
        )

    context = {
        "labels": labels,
        "counts": counts,
        "unique_school_years": unique_school_years,
        "gender_table_data": gender_table_data,
        "total_male_count": total_male_count,
        "total_female_count": total_female_count,
        "unique_years": unique_years,
        "gender_table_data_creation_year": gender_table_data_creation_year,
    }

    return render(request, "in-depth-charts/gender/gender_data.html", context)


#  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def fa_filter_applicants(request):
    if FinancialAssistanceApplication.objects.exists():
        applicants_to_transfer = FinancialAssistanceApplication.objects.all()

        with transaction.atomic():
            for applicant in applicants_to_transfer:
                FinancialAssistanceInfoRepository.objects.get_or_create(
                    control_number=applicant.control_number,
                    fullname=f"{applicant.last_name}, {applicant.first_name} {applicant.middle_name}. {applicant.suffix}",
                    date_of_birth=applicant.date_of_birth,
                    place_of_birth=applicant.place_of_birth,
                    gender=applicant.gender,
                    religion=applicant.religion,
                    blkstr=applicant.blkstr,
                    barangay=applicant.barangay,
                    city=applicant.city,
                    province=applicant.province,
                    email_address=applicant.email_address,
                    contact_no=applicant.contact_no,
                    general_average=applicant.general_average,
                    school=applicant.school,
                    school_address=applicant.school_address,
                    track=applicant.track,
                    strand=applicant.strand,
                    # family data
                    father_name=applicant.father_name,
                    father_age=applicant.father_age,
                    father_occupation=applicant.father_occupation,
                    father_employer=applicant.father_employer,
                    father_income=applicant.father_income,
                    mother_name=applicant.mother_name,
                    mother_age=applicant.mother_age,
                    mother_occupation=applicant.mother_occupation,
                    mother_employer=applicant.mother_employer,
                    mother_income=applicant.mother_income,
                    sibling_count=applicant.sibling_count,
                    a_sibling_name=applicant.a_sibling_name,
                    a_sibling_DOB=applicant.a_sibling_DOB,
                    a_sibling_age=applicant.a_sibling_age,
                    a_sibling_address=applicant.a_sibling_address,
                    b_sibling_name=applicant.a_sibling_name,
                    b_sibling_DOB=applicant.a_sibling_DOB,
                    b_sibling_age=applicant.a_sibling_age,
                    b_sibling_address=applicant.a_sibling_address,
                    c_sibling_name=applicant.a_sibling_name,
                    c_sibling_DOB=applicant.a_sibling_DOB,
                    c_sibling_age=applicant.a_sibling_age,
                    c_sibling_address=applicant.a_sibling_address,
                    d_sibling_name=applicant.a_sibling_name,
                    d_sibling_DOB=applicant.a_sibling_DOB,
                    d_sibling_age=applicant.a_sibling_age,
                    d_sibling_address=applicant.a_sibling_address,
                    e_sibling_name=applicant.a_sibling_name,
                    e_sibling_DOB=applicant.a_sibling_DOB,
                    e_sibling_age=applicant.a_sibling_age,
                    e_sibling_address=applicant.a_sibling_address,
                )

            is_met_list = [
                req.is_met
                for req in FAApplicationRequirements.objects.filter(applicant=applicant)
            ]

            if all(is_met_list):
                applicant.requirement = "Complete"

                FinancialAssistanceInfoRepository.objects.filter(
                    control_number=applicant.control_number
                ).update(status="Accepted")
                FinancialAssistanceAccepted.objects.create(
                    control_number=applicant.control_number,
                    fullname=f"{applicant.last_name}, {applicant.first_name} {applicant.middle_name}",
                    school=applicant.school,
                    strand=applicant.strand,
                    gender=applicant.gender,
                    barangay=applicant.barangay,
                )
                FinancialAssistanceApplication.objects.filter(
                    control_number=applicant.control_number
                ).delete()
            else:
                applicant.requirement = "Incomplete"

                FinancialAssistanceInfoRepository.objects.filter(
                    control_number=applicant.control_number
                ).update(status="Incomplete")
                FinancialAssistanceAssesment.objects.create(
                    control_number=applicant.control_number,
                    fullname=f"{applicant.last_name}, {applicant.first_name} {applicant.middle_name}",
                    school=applicant.school,
                )
                FinancialAssistanceApplication.objects.filter(
                    control_number=applicant.control_number
                ).delete()

        messages.success(request, "Applicants have been successfully filtered.")
    else:
        messages.warning(request, "There are no applicants to filter.")

    return redirect("fa_applicant_list")


def inb_filter_applicants(request):
    if CollegeStudentApplication.objects.exists():
        applicants_to_transfer = CollegeStudentApplication.objects.all()

        with transaction.atomic():
            for applicant in applicants_to_transfer:
                ApplicantInfoRepositoryINB.objects.get_or_create(
                    control_number=applicant.control_number,
                    fullname=f"{applicant.last_name}, {applicant.first_name} {applicant.middle_name}",
                    school_year=applicant.school_year,
                    blkstr=applicant.blkstr,
                    barangay=applicant.barangay,
                    province=applicant.province,
                    city=applicant.city,
                    gender=applicant.gender,
                    date_of_birth=applicant.date_of_birth,
                    place_of_birth=applicant.place_of_birth,
                    contact_no=applicant.contact_no,
                    email_address=applicant.email_address,
                    school=applicant.school,
                    course=applicant.course,
                    gwa=applicant.gwa,
                    rank=applicant.rank,
                    jhs=applicant.jhs,
                    jhs_address=applicant.jhs_address,
                    jhs_educational_provider=applicant.jhs_educational_provider,
                    shs=applicant.shs,
                    shs_address=applicant.shs_address,
                    shs_educational_provider=applicant.shs_educational_provider,
                    father_name=applicant.father_name,
                    father_voter_status=applicant.father_voter_status,
                    father_educational_attainment=applicant.father_educational_attainment,
                    father_employer=applicant.father_employer,
                    father_occupation=applicant.father_occupation,
                    mother_name=applicant.mother_name,
                    mother_voter_status=applicant.mother_voter_status,
                    mother_educational_attainment=applicant.mother_educational_attainment,
                    mother_employer=applicant.mother_employer,
                    mother_occupation=applicant.mother_occupation,
                    guardian_name=applicant.guardian_name,
                    guardian_voter_status=applicant.guardian_voter_status,
                    guardian_educational_attainment=applicant.guardian_educational_attainment,
                    guardian_employer=applicant.guardian_employer,
                    guardian_occupation=applicant.guardian_occupation,
                )

                is_met_list = [
                    req.is_met
                    for req in INBApplicationRequirements.objects.filter(
                        applicant=applicant
                    )
                ]

                if all(is_met_list):
                    applicant.requirement = "Complete"

                    ApplicantInfoRepositoryINB.objects.filter(
                        control_number=applicant.control_number
                    ).update(status="Accepted")
                    CollegeStudentAccepted.objects.create(
                        created_at=applicant.created_at,
                        control_number=applicant.control_number,
                        fullname=f"{applicant.last_name}, {applicant.first_name} {applicant.middle_name}",
                        school=applicant.school,
                        course=applicant.course,
                        gender=applicant.gender,
                        school_year=applicant.school_year,
                        barangay=applicant.barangay,
                    )
                    CollegeStudentApplication.objects.filter(
                        control_number=applicant.control_number
                    ).delete()
                else:
                    applicant.requirement = "Incomplete"

                    ApplicantInfoRepositoryINB.objects.filter(
                        control_number=applicant.control_number
                    ).update(status="Incomplete")
                    CollegeStudentAssesment.objects.create(
                        control_number=applicant.control_number,
                        fullname=f"{applicant.last_name}, {applicant.first_name} {applicant.middle_name}",
                        school=applicant.school,
                        course=applicant.course,
                    )
                    CollegeStudentApplication.objects.filter(
                        control_number=applicant.control_number
                    ).delete()

            messages.success(request, "Applicants have been successfully filtered.")
    else:
        messages.warning(request, "There are no applicants to filter.")

    return redirect("inb_applicant_list")


def inb_filter_assessment(request):
    applicants_to_transfer = CollegeStudentAssesment.objects.filter(
        status__in=["Accepted", "Rejected"]
    )

    if applicants_to_transfer.exists():
        for applicant in applicants_to_transfer:
            try:
                (
                    applicant_info,
                    created,
                ) = ApplicantInfoRepositoryINB.objects.get_or_create(
                    control_number=applicant.control_number
                )

                if created:
                    if applicant.status == "Accepted":
                        applicant_info.status = "Accepted"
                    elif applicant.status == "Rejected":
                        applicant_info.status = "Rejected"
                    applicant_info.save()

                if applicant.status == "Accepted":
                    CollegeStudentAccepted.objects.create(
                        control_number=applicant.control_number,
                        fullname=applicant.fullname,
                        school=applicant.school,
                        course=applicant.course,
                    )
                elif applicant.status == "Rejected":
                    CollegeStudentRejected.objects.create(
                        control_number=applicant.control_number,
                        fullname=applicant.fullname,
                        school=applicant.school,
                        course=applicant.course,
                        remarks=applicant.remarks,
                    )

                applicant.delete()

                messages.success(request, "Applicants have been successfully filtered.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        messages.warning(
            request,
            "There are no applicants with status 'Accepted' or 'Rejected' to filter.",
        )

    return redirect("inb_pending_applicant")


def fa_filter_assessment(request):
    applicants_to_transfer = FinancialAssistanceAssesment.objects.filter(
        status__in=["Accepted", "Rejected"]
    )

    if applicants_to_transfer.exists():
        for applicant in applicants_to_transfer:
            try:
                (
                    applicant_info,
                    created,
                ) = FinancialAssistanceInfoRepository.objects.get_or_create(
                    control_number=applicant.control_number
                )

                if created:
                    if applicant.status == "Accepted":
                        applicant_info.status = "Accepted"
                    elif applicant.status == "Rejected":
                        applicant_info.status = "Rejected"
                    applicant_info.save()

                if applicant.status == "Accepted":
                    FinancialAssistanceAccepted.objects.create(
                        control_number=applicant.control_number,
                        fullname=applicant.fullname,
                        school=applicant.school,
                        strand=applicant.strand,
                    )
                elif applicant.status == "Rejected":
                    FinancialAssistanceRejected.objects.create(
                        control_number=applicant.control_number,
                        fullname=applicant.fullname,
                        school=applicant.school,
                        strand=applicant.strand,
                    )

                applicant.delete()

                messages.success(request, "Applicants have been successfully filtered.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        messages.warning(
            request,
            "There are no applicants with status 'Accepted' or 'Rejected' to filter.",
        )

    return redirect("fa_pending_applicant")


# ---------------------------------------------


# ------------------------------------------------------------------------------------------------------------------------


# CRUD


def iskolar_ng_bayan_list(request):
    if request.user.is_authenticated:
        schools = INBSchool.objects.all()
        courses = INBCourse.objects.values("acronym").distinct()
        form = AddINBForm()
        import_form = ApplicantUploadForm(request.POST, request.FILES)
        export_form = ExportForm(request.POST)
        all_applicants = CollegeStudentApplication.objects.all()

        accepted_applicants = CollegeStudentAccepted.objects.values_list(
            "control_number", flat=True
        )
        rejected_applicants = CollegeStudentAssesment.objects.values_list(
            "control_number", flat=True
        )

        filtered_applicants = all_applicants.exclude(
            control_number__in=list(accepted_applicants) + list(rejected_applicants)
        )

        # Search functionality
        query = request.GET.get("q")
        if query:
            filtered_applicants = filtered_applicants.filter(
                Q(control_number__icontains=query)
                | Q(first_name__icontains=query)
                | Q(middle_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(course__icontains=query)
                | Q(school__icontains=query)
            )

        records = []

        with transaction.atomic():
            for applicant in filtered_applicants:
                applicant_requirements = INBApplicationRequirements.objects.filter(
                    applicant=applicant
                )

                completed_requirements_count = applicant_requirements.filter(
                    is_met=True
                ).count()

                total_requirements = INBRequirementRepository.objects.count()

                records.append(
                    (applicant, completed_requirements_count, total_requirements)
                )

                if completed_requirements_count == total_requirements:
                    applicant.requirement = "Complete"
                    applicant.save()

        # Paginator object
        paginator = Paginator(records, 20)  # Show 20 records per page
        page_number = request.GET.get("page")
        page = paginator.get_page(page_number)

        if not request.session.get("login_message_displayed", False):
            messages.success(request, "You have logged in successfully!")
            request.session["login_message_displayed"] = True

        return render(
            request,
            "INB/applicant_list.html",
            {
                "records": page,
                "form": form,
                "import_form": import_form,
                "export_form": export_form,
                "schools": schools,
                "courses": courses,
                "filtered_applicants": filtered_applicants,
            },
        )


def financial_assistance_list(request):
    if request.user.is_authenticated:
        import_form = ApplicantUploadForm(request.POST, request.FILES)
        form = AddFinancialAssistanceForm()
        all_applicants = FinancialAssistanceApplication.objects.all()

        accepted_applicants = FinancialAssistanceAccepted.objects.values_list(
            "control_number", flat=True
        )
        rejected_applicants = FinancialAssistanceRejected.objects.values_list(
            "control_number", flat=True
        )

        filtered_applicants = all_applicants.exclude(
            control_number__in=list(accepted_applicants) + list(rejected_applicants)
        )

        # Search functionality
        query = request.GET.get("q")
        if query:
            filtered_applicants = filtered_applicants.filter(
                Q(control_number__icontains=query)
                | Q(first_name__icontains=query)
                | Q(middle_name__icontains=query)
                | Q(last_name__icontains=query)
            )

        records = []

        with transaction.atomic():
            for applicant in filtered_applicants:
                applicant_requirements = FAApplicationRequirements.objects.filter(
                    applicant=applicant
                )

                completed_requirements_count = applicant_requirements.filter(
                    is_met=True
                ).count()

                total_requirements = FARequirementRepository.objects.count()

                records.append(
                    (applicant, completed_requirements_count, total_requirements)
                )

                if completed_requirements_count == total_requirements:
                    applicant.requirement = "Complete"
                    applicant.save()

        # Paginator object
        paginator = Paginator(records, 20)  # Show 20 records per page
        page_number = request.GET.get("page")
        page = paginator.get_page(page_number)

        if not request.session.get("login_message_displayed", False):
            messages.success(request, "You have logged in successfully!")
            request.session["login_message_displayed"] = True

        return render(
            request,
            "FA/applicant_list.html",
            {
                "records": page,
                "form": form,
                "import_form": import_form,
            },
        )


# ------------------------------------------------------------------------------------------------------------------------
# done refactoring


def inb_applicant_info(request, status, control_number):
    if request.user.is_authenticated:
        if status == "passed":
            model_class = CollegeStudentAccepted
            grade_class = StudentGrade
            template = "INB/passed_info.html"
        elif status == "pending":
            model_class = CollegeStudentAssesment
            template = "INB/inb_pending_info.html"
            form_class = INBPendingApplicants
        elif status == "failed":
            model_class = CollegeStudentRejected
            template = "INB/failed_info.html"
        else:
            messages.error(request, "Invalid status parameter.")
            return redirect("home")

        try:
            if request.method == "GET":
                if status == "passed":
                    passed_applicant = get_object_or_404(
                        model_class, control_number=control_number
                    )
                    student_grades = grade_class.objects.filter(
                        control_number=control_number
                    )

                    return render(
                        request,
                        template,
                        {
                            "passed_applicant": passed_applicant,
                            "status": status,
                            "student_grades": student_grades,
                        },
                    )

                elif status == "pending":
                    pending_applicant = get_object_or_404(
                        model_class, control_number=control_number
                    )
                    form = form_class()
                    return render(
                        request,
                        template,
                        {
                            "pending_applicant": pending_applicant,
                            "status": status,
                            "form": form,
                            "control_number": control_number,
                        },
                    )
                elif status == "failed":
                    failed_applicant = get_object_or_404(
                        model_class, control_number=control_number
                    )
                    return render(
                        request,
                        template,
                        {"failed_applicant": failed_applicant, "status": status},
                    )

            elif request.method == "POST":
                form = form_class(request.POST)
                if form.is_valid():
                    if status == "pending":
                        pending_applicant = get_object_or_404(
                            model_class, control_number=control_number
                        )
                        pending_applicant.status = form.cleaned_data["status"]
                        pending_applicant.remarks = form.cleaned_data["remarks"]
                        pending_applicant.save()

                    messages.success(
                        request,
                        f"{status.capitalize()} applicant information updated successfully.",
                    )
                    return redirect("inb_pending_applicant")

        except model_class.DoesNotExist:
            messages.error(request, f"{status.capitalize()} applicant not found.")
            return redirect(f"inb_{status}_applicant")

    else:
        messages.error(request, "You don't have permission.")
        return redirect("home")


def inb_applicant_list(request, status):
    if request.user.is_authenticated:
        if status == "passed":
            model_class = CollegeStudentAccepted
            template = "INB/accepted_applicants.html"
        elif status == "pending":
            model_class = CollegeStudentAssesment
            template = "INB/inb_pending_list.html"
        elif status == "failed":
            model_class = CollegeStudentRejected
            template = "INB/rejected_applicants.html"
        else:
            messages.error(request, "Invalid status parameter.")
            return redirect("home")

        applicants_list = model_class.objects.all()

        # the search functionality
        query = request.GET.get("q")
        if query:
            applicants_list = applicants_list.filter(
                Q(control_number__icontains=query)
                | Q(fullname__icontains=query)
                | Q(course__icontains=query)
                | Q(school__icontains=query)
            )

        paginator = Paginator(applicants_list, 10)
        page_number = request.GET.get("page")
        applicants = paginator.get_page(page_number)

        form = GradeUploadForm(request.POST, request.FILES)
        return render(request, template, {"applicants": applicants, "form": form})
    else:
        messages.error(request, "You don't have permission.")
        return redirect("home")


def fa_applicant_info(request, status, control_number):
    if request.user.is_authenticated:
        if status == "passed":
            model_class = FinancialAssistanceAccepted
            template = "FA/fa_passed_info.html"
        elif status == "pending":
            model_class = FinancialAssistanceAssesment
            template = "FA/fa_pending_info.html"
            form_class = FAPendingApplicants
        elif status == "failed":
            model_class = FinancialAssistanceRejected
            template = "FA/fa_failed_info.html"
        else:
            messages.error(request, "Invalid status parameter.")
            return redirect("home")

        try:
            if request.method == "GET":
                if status == "passed":
                    passed_applicant = get_object_or_404(
                        model_class, control_number=control_number
                    )
                    return render(
                        request,
                        template,
                        {"passed_applicant": passed_applicant, "status": status},
                    )
                elif status == "pending":
                    pending_applicant = get_object_or_404(
                        model_class, control_number=control_number
                    )
                    form = form_class()
                    return render(
                        request,
                        template,
                        {
                            "pending_applicant": pending_applicant,
                            "status": status,
                            "form": form,
                            "control_number": control_number,
                        },
                    )
                elif status == "failed":
                    failed_applicant = get_object_or_404(
                        model_class, control_number=control_number
                    )
                    return render(
                        request,
                        template,
                        {"failed_applicant": failed_applicant, "status": status},
                    )

            elif request.method == "POST":
                form = form_class(request.POST)
                if form.is_valid():
                    if status == "pending":
                        pending_applicant = get_object_or_404(
                            model_class, control_number=control_number
                        )
                        pending_applicant.status = form.cleaned_data["status"]
                        pending_applicant.remarks = form.cleaned_data["remarks"]
                        pending_applicant.save()

                    messages.success(
                        request,
                        f"{status.capitalize()} applicant information updated successfully.",
                    )
                    return redirect("fa_pending_applicant")

        except model_class.DoesNotExist:
            messages.error(request, f"{status.capitalize()} applicant not found.")
            return redirect(f"fa_{status}_applicant")

    else:
        messages.error(request, "You don't have permission.")
        return redirect("home")


def fa_applicant_list(request, status):
    if request.user.is_authenticated:
        if status == "passed":
            model_class = FinancialAssistanceAccepted
            template = "FA/fa_passed_list.html"
        elif status == "pending":
            model_class = FinancialAssistanceAssesment
            template = "FA/fa_pending_list.html"
        elif status == "failed":
            model_class = FinancialAssistanceRejected
            template = "FA/fa_failed_list.html"
        else:
            messages.error(request, "Invalid status parameter.")
            return redirect("home")

        applicants = model_class.objects.all()

        # the search functionality
        query = request.GET.get("q")
        if query:
            applicants = applicants.filter(
                Q(control_number__icontains=query)
                | Q(fullname__icontains=query)
                | Q(strand__icontains=query)
                | Q(school__icontains=query)
            )

        return render(request, template, {"applicants": applicants})
    else:
        messages.error(request, "You don't have permission.")
        return redirect("home")


# ------------------------------------------------------------------------------------------------------------------------


def inb_applicant_information_details(request, control_number):
    if request.user.is_authenticated:
        try:
            records = ApplicantInfoRepositoryINB.objects.get(
                control_number=control_number
            )
            context = {"records": records, "control_number": control_number}
            return render(
                request,
                "INB/applicant_detailed_info.html",
                context,
            )
        except ApplicantInfoRepositoryINB.DoesNotExist:
            messages.error(request, "Applicant data not found.")
            return redirect("home")
    else:
        messages.success(request, "You need to be logged in to see this data!")
        return redirect("home")


def page_not_found(request):
    return render(request, "page_not_found.html")


from django.dispatch import Signal
from django.contrib.auth.decorators import login_required

applicant_added_signal = Signal()


@login_required
def inb_applicant_information(request, pk):
    if request.user.is_authenticated:
        current_record_inb = CollegeStudentApplication.objects.get(id=pk)
        form_inb = AddINBForm(request.POST or None, instance=current_record_inb)

        if request.method == "POST" and form_inb.is_valid():
            form_inb.save()

            username = request.user.username

            applicant_added_signal.send(
                sender=CollegeStudentApplication,
                instance=current_record_inb,
                created=True,
                username=request.user.username,
            )

        try:
            records = CollegeStudentApplication.objects.get(id=pk)
            requirements = INBApplicationRequirements.objects.filter(applicant=records)

        except CollegeStudentApplication.DoesNotExist:
            records = None
            requirements = []

        return render(
            request,
            "INB/applicants_info.html",
            {"records": records, "requirements": requirements, "form": form_inb},
        )
    else:
        messages.success(request, "You need to be logged in to see this data!")
        return redirect("home")


def fa_applicant_information(request, pk):
    if request.user.is_authenticated:
        try:
            records = FinancialAssistanceApplication.objects.get(id=pk)
            requirements = FAApplicationRequirements.objects.filter(applicant=records)

        except FinancialAssistanceApplication.DoesNotExist:
            records = None
            requirements = []

        return render(
            request,
            "FA/fa_applicant_info.html",
            {"records": records, "requirements": requirements},
        )
    else:
        messages.success(request, "You need to be logged in to see this data!")
        return redirect("home")


def delete_by_id(request, pk, model_name):
    return delete_record(request, pk, model_name, use_id=True)


def delete_by_control_number(request, control_number, model_name):
    return delete_record(request, control_number, model_name, use_id=False)


def delete_record(request, identifier, model_name, use_id=True):
    if request.user.is_authenticated:
        list_view = "home"

        model_map = {
            "application": (CollegeStudentApplication, "inb_applicant_list"),
            "inb_passed": (CollegeStudentAccepted, "inb_passed_applicant"),
            "inb_pending": (CollegeStudentAssesment, "inb_pending_applicant"),
            "inb_failed": (CollegeStudentRejected, "inb_failed_applicant"),
            "fa_application": (FinancialAssistanceApplication, "fa_applicant_list"),
            "fa_passed": (FinancialAssistanceAccepted, "fa_passed_applicant"),
            "fa_pending": (FinancialAssistanceAssesment, "fa_pending_applicant"),
            "fa_failed": (FinancialAssistanceRejected, "fa_failed_applicant"),
        }

        if model_name in model_map:
            model, list_view = model_map[model_name]
        else:
            messages.error(request, "Invalid model name")
            return redirect("home")

        try:
            if use_id:
                record = get_object_or_404(model, id=identifier)
            else:
                record = get_object_or_404(model, control_number=identifier)

            record.delete()
            messages.success(
                request, f"Record for {model_name.capitalize()} has been deleted"
            )
        except model.DoesNotExist:
            messages.error(request, f"{model_name.capitalize()} record not found")

        return redirect(list_view)
    else:
        messages.error(request, "You need to be logged in for this process")
        return redirect("home")


def add_information(request, form_type):
    if request.user.is_authenticated:
        if form_type == "applicant":
            form = AddINBForm(request.POST or None)
            template = "INB/add_record.html"
            success_url = "inb_applicant_list"
        elif form_type == "financial_assistance":
            form = AddFinancialAssistanceForm(request.POST or None)
            template = "FA/assistance_add_applicant.html"
            success_url = "fa_applicant_list"
        else:
            messages.error(request, "Invalid form type.")
            return redirect("home")

        if request.method == "POST":
            if form.is_valid():
                add_record = form.save()
                messages.success(request, "Record Successfully Added")
                return redirect(success_url)

        return render(request, template, {"form": form})
    else:
        messages.error(request, "You need to be logged in for this process.")
        return redirect("home")


def update_information(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in for this process.")
        return redirect("home")

    try:
        current_record_inb = CollegeStudentApplication.objects.get(id=pk)
        form_inb = AddINBForm(request.POST or None, instance=current_record_inb)
        if form_inb.is_valid():
            form_inb.save()
            messages.success(request, "INB Record has been updated!!")
            return redirect("inb_applicant_list")
        return render(request, "INB/update_record.html", {"form": form_inb})
    except CollegeStudentApplication.DoesNotExist:
        pass

    try:
        current_record_fa = FinancialAssistanceApplication.objects.get(id=pk)
        form_fa = AddFinancialAssistanceForm(
            request.POST or None, instance=current_record_fa
        )
        if form_fa.is_valid():
            form_fa.save()
            messages.success(request, "Financial Assistance Record has been updated!!")
            return redirect("fa_applicant_list")
        return render(request, "FA/fa_update_record.html", {"form": form_fa})
    except FinancialAssistanceApplication.DoesNotExist:
        pass

    messages.error(request, "Invalid record or model name")
    return render(
        request, "error_page.html", {"message": "Invalid record or model name provided"}
    )


# Requirements~~
def inb_requirements_list(request, control_number):
    student = CollegeStudentApplication.objects.get(control_number=control_number)
    requirements = INBApplicationRequirements.objects.filter(applicant=student)

    if request.method == "POST":
        selected_requirements = request.POST.getlist("requirements")

        INBApplicationRequirements.objects.filter(applicant=student).update(
            is_met=False
        )
        INBApplicationRequirements.objects.filter(id__in=selected_requirements).update(
            is_met=True
        )

        return redirect("inb_applicant_list")

    context = {
        "student": student,
        "requirements": requirements,
    }

    return render(request, "INB/requirement.html", context)


def fa_requirement_list(request, control_number):
    student = FinancialAssistanceApplication.objects.get(control_number=control_number)
    requirements = FAApplicationRequirements.objects.filter(applicant=student)

    if request.method == "POST":
        selected_requirements = request.POST.getlist("requirements")

        FAApplicationRequirements.objects.filter(applicant=student).update(is_met=False)
        FAApplicationRequirements.objects.filter(id__in=selected_requirements).update(
            is_met=True
        )

        return redirect("fa_applicant_list")

    context = {
        "student": student,
        "requirements": requirements,
    }

    return render(request, "FA/requirement.html", context)


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Navbar
def navbar_user(request):
    active_user = {"user": request.user}

    return render(request, "navbar.html", active_user)


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def school_course_list(request):
    schools = INBSchool.objects.all()

    schools_with_courses = []
    for school in schools:
        courses = INBCourse.objects.filter(school_id=school.id)
        schools_with_courses.append(
            {
                "school": school,
                "courses": courses,
            }
        )

    return render(
        request,
        "Admin/list_course_school.html",
        {"schools_with_courses": schools_with_courses, "schools": schools},
    )


def create_school(request):
    if request.method == "POST":
        form = INBSchoolForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            error_message = form.errors['school'][0]
            return JsonResponse({'success': False, 'error_message': error_message})
    else:
        form = INBSchoolForm()

    return render(request, "Admin/list-school-course.html", {"school_form": form})


def add_course(request):
    if request.method == "POST":
        form = INBCourseForm(request.POST)
        if form.is_valid():
            selected_schools = request.POST.getlist("schools")
            course_data = form.cleaned_data

            for school_id in selected_schools:
                course_instance = INBCourse(
                    course=course_data["course"],
                    acronym=course_data["acronym"],
                    school_id=int(school_id),
                )
                course_instance.save()

            messages.success(request, "Course(s) Successfully Added")
            return redirect("sc_list")
    else:
        form = INBCourseForm()

    schools = INBSchool.objects.all()
    return render(
        request,
        "Admin/list_course_school.html",
        {"course_form": form, "schools": schools},
    )


def update_list(request):
    schools = INBSchool.objects.all()
    courses = INBCourse.objects.all()
    schools_with_courses = []

    for school in schools:
        school_courses = INBCourse.objects.filter(school_id=school.id)
        schools_with_courses.append(
            {
                "school": school,
                "courses": school_courses,
                "form": INBSchoolForm(),
            }
        )

    return render(
        request,
        "Admin/update-school-course.html",
        {"schools_with_courses": schools_with_courses, "all_courses": courses},
    )


def update_school_list(request, school_id):
    school = get_object_or_404(INBSchool, id=school_id)

    if request.method == "POST":
        form = INBSchoolForm(request.POST, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated the Data Successfully")
            return redirect("sc_list")
    else:
        form = INBSchoolForm(instance=school)

    return render(
        request, "Admin/update-school-course.html", {"school": school, "form": form}
    )


def update_course_list(request, course_id):
    course = get_object_or_404(INBCourse, id=course_id)

    if request.method == "POST":
        print(request.method)
        print(request.POST)
        form = INBCourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated the Data Successfully")
            return redirect("sc_list")
    else:
        form = INBCourseForm(instance=course)

    return render(
        request, "Admin/update-school-course.html", {"course": course, "form": form}
    )


def delete_item(request, item_type, item_id):
    if item_type == "school":
        model_class = INBSchool
        success_message = "School and Courses Deleted Successfully"
    elif item_type == "course":
        model_class = INBCourse
        success_message = "Course Deleted Successfully"
    else:
        return redirect("sc_list")

    if request.method == "POST":
        item = get_object_or_404(model_class, pk=item_id)
        if item_type == "school":
            item.inbcourse_set.all().delete()
        item.delete()
        messages.success(request, success_message)
        return redirect("sc_list")

    return redirect("sc_list")


def filter(request):
    schools = INBSchool.objects.all()
    courses = INBCourse.objects.values("acronym").distinct()

    school_list = CollegeStudentApplication.objects.values("school")
    course_list = CollegeStudentApplication.objects.values("course")

    filtered_applicants = CollegeStudentApplication.objects.all()

    if school_list:
        filtered_applicants = filtered_applicants.filter(school__in=school_list)

    if course_list:
        filtered_applicants = filtered_applicants.filter(course__in=course_list)

    return render(
        request,
        "INB/applicant_list.html",
        {
            "schools": schools,
            "courses": courses,
            "filtered_applicants": filtered_applicants,
            "selected_schools": school_list,
            "selected_courses": course_list,
        },
    )


def update_requirement(request):
    inb_requirement_list = INBRequirementRepository.objects.all()
    fa_requirement_list = FARequirementRepository.objects.all()
    return render(
        request,
        "Admin/update-requirement.html",
        {
            "inb_requirements": inb_requirement_list,
            "fa_requirements": fa_requirement_list,
        },
    )


def render_requirement(request, form_type):
    if request.user.is_authenticated:
        template = "Admin/update-requirement.html"
        requirements = None

        if form_type == "inb":
            template = "Admin/inb-requirements.html"
            requirements = INBRequirementRepository.objects.all()
        elif form_type == "fa":
            template = "Admin/fa-requirements.html"
            requirements = FARequirementRepository.objects.all()
        else:
            messages.error(request, "Invalid form type.")
            return redirect("home")

        return render(
            request, template, {"requirements": requirements, "form_type": form_type}
        )
    else:
        messages.error(request, "You need to be logged in for this process.")
        return redirect("home")


def add_requirement(request, form_type):
    if request.user.is_authenticated:
        if form_type == "inb":
            form = INBRequirementList(request.POST or None)
            model_class = INBRequirementRepository
        elif form_type == "fa":
            form = FARequirementList(request.POST or None)
            model_class = FARequirementRepository
        else:
            messages.error(request, "Invalid form type.")
            return redirect("home")

        if request.method == "POST":
            if form.is_valid():
                requirement_data = form.cleaned_data
                requirement_instance = model_class.objects.create(**requirement_data)
                messages.success(request, "Requirements Successfully Added")
                return redirect("update_req")

        return render(request, "Admin/update-requirement.html", {"form": form})
    else:
        messages.error(request, "You need to be logged in for this process.")
        return redirect("home")


def update_inb_requirement(request, requirement_id):
    requirement = get_object_or_404(INBRequirementRepository, id=requirement_id)

    if request.method == "POST":
        form = INBRequirementList(request.POST, instance=requirement)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated the Requirement Successfully")
            return redirect("inb_requirement")
    else:
        form = INBRequirementList(instance=requirement)

    return render(
        request,
        "Admin/inb-requirements.html",
        {"requirement": requirement, "form": form},
    )


def update_fa_requirement(request, requirement_id):
    requirement = get_object_or_404(FARequirementRepository, id=requirement_id)

    if request.method == "POST":
        form = FARequirementList(request.POST, instance=requirement)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated the Requirement Successfully")
            return redirect("fa_requirement")
    else:
        form = FARequirementList(instance=requirement)

    return render(
        request,
        "Admin/fa-requirements.html",
        {"requirement": requirement, "form": form},
    )


def delete_requirement(request, item_type, item_id):
    if item_type == "inb":
        model_class = INBRequirementRepository
        success_message = "Requirement Deleted Successfully"
        redirect_site = "inb_requirement"
    elif item_type == "fa":
        model_class = FARequirementRepository
        success_message = "Requirement Deleted Successfully"
        redirect_site = "fa_requirement"
    else:
        return redirect("sc_list")

    if request.method == "POST":
        item = get_object_or_404(model_class, pk=item_id)
        item.delete()
        messages.success(request, success_message)
        return redirect(redirect_site)

    return redirect("home")


def import_grade(request):
    if request.method == "POST":
        form = GradeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES["file"]
            df = pd.read_excel(excel_file, skiprows=10)
            df.columns = df.columns.str.strip()

            if "CONTROL_NUMBER" not in df.columns:
                return HttpResponse(
                    "Error: 'CONTROL_NUMBER' column not found in the Excel file."
                )

            student_grades = []

            for index, row in df.iterrows():
                control_number = row["CONTROL_NUMBER"]
                gwa = row["GWA"]

                subject_cols = [col for col in df.columns if col.startswith("SUBJECT")]
                grade_cols = [col for col in df.columns if col.startswith("GRADE")]

                for subject_col, grade_col in zip(subject_cols, grade_cols):
                    subject = row[subject_col]
                    grade = row[grade_col]
                    print(
                        f"Creating StudentGrade: control_number={control_number}, subject={subject}, grade={grade}, gwa={gwa}"
                    )
                    student_grades.append(
                        StudentGrade(
                            control_number=control_number,
                            subject=subject,
                            grade=grade,
                            gwa=gwa,
                        )
                    )

                college_student = get_object_or_404(
                    CollegeStudentAccepted, control_number=control_number
                )
                college_student.grant = gwa
                if 1 <= gwa <= 2:
                    college_student.grant = "100%"
                elif 2.25 <= gwa <= 2.75:
                    college_student.grant = "80%"
                elif 3 <= gwa <= 5:
                    college_student.grant = "Failed"
                else:
                    college_student.grant = "Unknown"

                college_student.save()

            StudentGrade.objects.bulk_create(student_grades)

            messages.success(request, "Grades Successfully Imported")
            return redirect("inb_passed_applicant")

    else:
        form = GradeUploadForm()

    return render(request, "modal/import_grades.html", {"form": form})

def new_sem(request):
    data_update = CollegeStudentAccepted.objects.all()

    student_grades = []

    for student in data_update:
        control_number = student.control_number
        school_year = student.school_year
        sem = student.semester

        student_grade_queryset = StudentGrade.objects.filter(control_number=control_number)

        if student_grade_queryset.exists():
            student_grade = student_grade_queryset.first()
            gwa = student_grade.gwa
        else:
            gwa = 0  

        student_grades.append(StudentGradeRepository(
            control_number=control_number,
            school_year=school_year,
            semester=sem,
            gwa=gwa,
        ))

        StudentGrade.objects.all().delete()
        StudentGradeRepository.objects.bulk_create(student_grades)

        if sem == '1st Semester':
            student.semester = '2nd Semester'
        elif sem == '2nd Semester':
            student.semester = '1st Semester'

        if sem == '1st Semester':
            student.semester = '2nd Semester'
            if student.school_year == '1st Year':
                student.school_year = '1st Year'
            elif student.school_year == '2nd Year':
                student.school_year = '2nd Year'
            elif student.school_year == '3rd Year':
                student.school_year = '3rd Year'
            elif student.school_year == '4th Year':
                student.school_year = '4th Year'
            elif student.school_year == '5th Year':
                student.school_year = '5th Year'
        elif sem == '2nd Semester':
            student.semester = '1st Semester'
            if student.school_year == '1st Year':
                student.school_year = '2nd Year'
            elif student.school_year == '2nd Year':
                student.school_year = '3rd Year'
            elif student.school_year == '3rd Year':
                student.school_year = '4th Year'
            elif student.school_year == '4th Year':
                student.school_year = '5th Year'
            elif student.school_year == '5th Year':
                student.school_year = 'Graduated'
        student.save()

        messages.success(request, "Semester Successfully Ended")
        return redirect("inb_passed_applicant")

    return render(request, "modal/end_sem.html")