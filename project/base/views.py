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
    StudentGradeRepository,
)
from django.db.models import Count
from django.http import HttpResponse
import csv
import pandas as pd
from import_export import resources
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db import IntegrityError
from django.contrib import messages
from django.http import JsonResponse
from .filter import (
    TableFilter,

)


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

#changes/ no filter for passed yet
def print_permit_view(request):
    get_permit = ApplicantInfoRepositoryINB.objects.all()
    pdf_buffer = generate_permit_pdf(get_permit)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="INB-Permit.pdf"'
    response.write(pdf_buffer.read())

    return response


def print_view(request):
    get_permit = ApplicantInfoRepositoryINB.objects.all()
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
from django.db import models

def fa_data_visualization(request):
    
    return render(request, "fa-dashboard.html")

def active_scholar_summary(request):
    active_scholar = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing")
        .values("created_at__year")
        .annotate(active_scholar_count=Count("id"))
        .order_by("created_at__year")  
    )

    school_counts = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing")
        .exclude(status="Graduated")
        .values("school")
        .annotate(count=Count("school"))
        .order_by("-count")
    )

    course_counts = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing")
        .exclude(status="Graduated")
        .values("course")
        .annotate(count=Count("course"))
        .order_by("-count")
    )

    unique_years_list = sorted(set(entry["created_at__year"] for entry in active_scholar))

    first_year_count = ApplicantInfoRepositoryINB.objects.filter(
        school_year="1st Year", tracker="Ongoing"
    ).count()
    second_year_count = ApplicantInfoRepositoryINB.objects.filter(
        school_year="2nd Year", tracker="Ongoing"
    ).count()
    third_year_count = ApplicantInfoRepositoryINB.objects.filter(
        school_year="3rd Year", tracker="Ongoing"
    ).count()
    fourth_year_count = ApplicantInfoRepositoryINB.objects.filter(
        school_year="4th Year", tracker="Ongoing"
    ).count()
    fifth_year_count = ApplicantInfoRepositoryINB.objects.filter(
        school_year="5th Year", tracker="Ongoing"
    ).count()

    context = {
        "active_scholar": active_scholar,
        "unique_years_list": unique_years_list,
        "schoolCustomLabels": [entry["school"] for entry in school_counts],
        "schoolDataCounts": [entry["count"] for entry in school_counts],
        "first_year_count": first_year_count,
        "second_year_count": second_year_count,
        "third_year_count": third_year_count,
        "fourth_year_count": fourth_year_count, 
        "fifth_year_count": fifth_year_count,
        "course_counts": course_counts,
        "courseCustomLabels" : [entry['course'] for entry in course_counts],
        "courseDataCounts" :[entry['count'] for entry in course_counts],
    }
    return render(
        request, "in-depth-charts/active-scholar/active_scholar.html", context
    )



def graduate_scholar_summary(request):
    graduated_data = (
        ApplicantInfoRepositoryINB.objects.filter(status="Graduated")
        .values("created_at__year")
        .annotate(graduates_scholar_count=Count("id"))
        .order_by("created_at__year")  
    )

    school_graduate_counts = (
        ApplicantInfoRepositoryINB.objects.filter(status="Graduated")
        .values("school")
        .annotate(count=Count("school"))
        .order_by("-count")
    )

    course_graduate_counts = (
        ApplicantInfoRepositoryINB.objects.filter(status="Graduated")
        .values("course")
        .annotate(count=Count("course"))
        .order_by("-count")
    )

    gender_data = (
        ApplicantInfoRepositoryINB.objects.filter(status="Graduated")
        .values("gender")
        .annotate(count=models.Count("gender"))
    )

    labels = [entry["gender"] for entry in gender_data]
    counts = [entry["count"] for entry in gender_data]

    unique_years_list = sorted(set(entry["created_at__year"] for entry in graduated_data))

    context = {
        "graduated_data": graduated_data,
        "unique_years_list": unique_years_list,
        "school_graduate_counts": school_graduate_counts,
        "schoolCustomLabels": [entry["school"] for entry in school_graduate_counts],
        "schoolDataCounts": [entry["count"] for entry in school_graduate_counts],
        "course_graduate_counts": course_graduate_counts,
        "courseCustomLabels" : [entry['course'] for entry in course_graduate_counts],
        "courseDataCounts" :[entry['count'] for entry in course_graduate_counts],
        "gender_data": gender_data,
        "labels": labels,
        "counts": counts,

    }

    return render(
        request, "in-depth-charts/graduated-scholar/graduated-scholar.html", context
    )


def unsuccessful_scholar_summary(request):
    failed_scholar = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Rejected")
        .values("created_at__year")
        .annotate(failed_scholar_count=Count("id"))
        .order_by("created_at__year")  
    )

    rejected_scholar = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Failed")
        .values("created_at__year")
        .annotate(rejected_scholar_count=Count("id"))
        .order_by("created_at__year")  
    )

    failed_unique_years_list = sorted(set(entry["created_at__year"] for entry in failed_scholar))
    rejected_unique_years_list = sorted(set(entry["created_at__year"] for entry in rejected_scholar))

    failed_scholar_remarks = (
    ApplicantInfoRepositoryINB.objects.filter(tracker="Failed")
    .values('remarks')
    .annotate(failed_count=Count('remarks'))
    .order_by('-failed_count')  
    )

    rejected_scholar_remarks = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Rejected")
        .values('remarks')
        .annotate(rejected_count=Count('remarks'))
        .order_by('-rejected_count')  
    )

    rejected_gender = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Rejected")
        .values("gender")
        .annotate(count=models.Count("gender"))
    )

    rejected_gender_labels = [entry["gender"] for entry in rejected_gender]
    rejected_gender_counts = [entry["count"] for entry in rejected_gender]

    failed_gender = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Failed")
        .values("gender")
        .annotate(count=models.Count("gender"))
    )

    failed_gender_labels = [entry["gender"] for entry in failed_gender]
    failed_gender_counts = [entry["count"] for entry in failed_gender]

    failed_schools = (
    ApplicantInfoRepositoryINB.objects.filter(tracker="Failed")
    .values('school')
    .annotate(failed_school_count=Count('school'))
    .order_by('-failed_school_count')  
    )
 
    failed_course = (
    ApplicantInfoRepositoryINB.objects.filter(tracker="Failed")
    .values('course')
    .annotate(failed_course_count=Count('course'))
    .order_by('-failed_course_count')  
    )
    

    context = { 
                'failed_scholar' : failed_scholar, 
                'rejected_scholar': rejected_scholar,
                'failed_unique_years_list': failed_unique_years_list,
                'rejected_unique_years_list':rejected_unique_years_list, 
                'rejected_scholar_remarks': rejected_scholar_remarks,
                'failed_scholar_remarks': failed_scholar_remarks,

                'rejected_gender': rejected_gender,
                'rejected_gender_labels': rejected_gender_labels,
                'rejected_gender_counts': rejected_gender_counts,

                'failed_gender': failed_gender,
                'failed_gender_labels': failed_gender_labels,
                'failed_gender_counts': failed_gender_counts,

                'failed_schools': failed_schools,
                'schoolCustomLabels': [entry["school"] for entry in failed_schools],
                'schoolDataCounts': [entry["failed_school_count"] for entry in failed_schools],

                'failed_course': failed_course,
                'courseCustomLabels': [entry["course"] for entry in failed_course],
                'courseDataCounts': [entry["failed_course_count"] for entry in failed_course],

            }

    return render(
        request, "in-depth-charts/unsuccessful-scholar/unsuccessful-scholar.html", context
    )



def gender_summary(request):
    male_scholar = (
    ApplicantInfoRepositoryINB.objects.filter(gender="Male", tracker="Ongoing")
    .values("created_at__year")
    .annotate(male_scholar_count=Count("id"))
    .order_by("created_at__year")  
    )

    female_scholar = (
        ApplicantInfoRepositoryINB.objects.filter(gender="Female", tracker="Ongoing")
        .values("created_at__year")
        .annotate(female_scholar_count=Count("id"))
        .order_by("created_at__year")  
    )

    male_unique_years_list = sorted(set(entry["created_at__year"] for entry in male_scholar))
    female_unique_years_list = sorted(set(entry["created_at__year"] for entry in female_scholar))

    male_schools = (
        ApplicantInfoRepositoryINB.objects.filter(gender="Male", tracker="Ongoing")
        .values('school')
        .annotate(male_count=Count('id'))
        .order_by('-male_count')  
    )

    female_schools = (
        ApplicantInfoRepositoryINB.objects.filter(gender="Female", tracker="Ongoing")
        .values('school')
        .annotate(female_count=Count('id'))
        .order_by('-female_count')  
    )

    male_first_year_count = ApplicantInfoRepositoryINB.objects.filter(
        gender="Male",
        school_year="1st Year",
        tracker="Ongoing"
    ).count()

    female_first_year_count = ApplicantInfoRepositoryINB.objects.filter(
        gender="Female",
        school_year="1st Year",
        tracker="Ongoing"
    ).count()

    male_second_year_count = ApplicantInfoRepositoryINB.objects.filter(
        gender="Male",
        school_year="2nd Year",
        tracker="Ongoing"
    ).count()

    female_second_year_count = ApplicantInfoRepositoryINB.objects.filter(
        gender="Female",
        school_year="2nd Year",
        tracker="Ongoing"
    ).count()

    male_third_year_count = ApplicantInfoRepositoryINB.objects.filter(
        gender="Male",
        school_year="3rd Year",
        tracker="Ongoing"
    ).count()

    female_third_year_count = ApplicantInfoRepositoryINB.objects.filter(
        gender="Female",
        school_year="3rd Year",
        tracker="Ongoing"
    ).count()

    male_fourth_year_count = ApplicantInfoRepositoryINB.objects.filter(
        gender="Male",
        school_year="4th Year",
        tracker="Ongoing"
    ).count()

    female_fourth_year_count = ApplicantInfoRepositoryINB.objects.filter(
        gender="Female",
        school_year="4th Year",
        tracker="Ongoing"
    ).count()

    male_fifth_year_count = ApplicantInfoRepositoryINB.objects.filter(
        gender="Male",
        school_year="5th Year",
        tracker="Ongoing"
    ).count()

    female_fifth_year_count = ApplicantInfoRepositoryINB.objects.filter(
        gender="Female",
        school_year="5th Year",
        tracker="Ongoing"
    ).count()

    male_course = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing", gender="Male")
        .values('course')
        .annotate(male_course_count=Count('course'))
        .order_by('-male_course_count')  
    )

    female_course = (
       ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing", gender="Female")
        .values('course')
        .annotate(female_course_count=Count('course'))
        .order_by('-female_course_count')  
    )

    context = {
        'male_scholar': male_scholar,
        'female_scholar': female_scholar,
        'male_unique_years_list': male_unique_years_list,
        'female_unique_years_list':female_unique_years_list, 

        'male_schools':male_schools,
        'maleSchoolCustomLabels': [entry["school"] for entry in male_schools],
        'maleSchoolDataCounts': [entry["male_count"] for entry in male_schools],

        'female_schools':female_schools,
        'femaleSchoolCustomLabels': [entry["school"] for entry in female_schools],
        'femaleSchoolDataCounts': [entry["female_count"] for entry in female_schools],

        'male_first_year_count': male_first_year_count,
        'female_first_year_count': female_first_year_count,
        'male_second_year_count': male_second_year_count,
        'female_second_year_count': female_second_year_count,
        'male_third_year_count': male_third_year_count,
        'female_third_year_count': female_third_year_count,
        'male_fourth_year_count': male_fourth_year_count,
        'female_fourth_year_count': female_fourth_year_count,
        'male_fifth_year_count': male_fifth_year_count,
        'female_fifth_year_count': female_fifth_year_count,


        'male_course':male_course,
        'maleCourseCustomLabels': [entry["course"] for entry in male_course],
        'maleCourseDataCounts': [entry["male_course_count"] for entry in male_course],

        'female_course':female_course,
        'femaleCourseCustomLabels': [entry["course"] for entry in female_course],
        'femaleCourseDataCounts': [entry["female_course_count"] for entry in female_course],

    }

    return render(request, "in-depth-charts/gender/gender_data.html", context)

def tracker_scholar_summary(request):
    current_year = timezone.now().year
    accepted_scholar = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing")
        .values("created_at__year")
        .annotate(accepted_scholar_count=Count("id"))
        .order_by("created_at__year")  
    ) 

    applied_scholar = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Rejected")
        .values("created_at__year")
        .annotate(applied_scholar_count=Count("id"))
        .order_by("created_at__year")  
    )

    accepted_unique_years_list = sorted(set(entry["created_at__year"] for entry in accepted_scholar))
    applied_unique_years_list = sorted(set(entry["created_at__year"] for entry in applied_scholar))

    current_accepted_count = ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing", created_at__year=current_year).count()
    current_applied_count = ApplicantInfoRepositoryINB.objects.filter(tracker="Rejected", created_at__year=current_year).count()
    
    schools = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing", created_at__year=current_year)
        .values('school')
        .annotate(count=Count('id'))
        .order_by('-count')  
    )
    

    context = {
        'accepted_scholar':accepted_scholar,
        'accepted_unique_years_list':accepted_unique_years_list,
        'applied_scholar':applied_scholar,
        'applied_unique_years_list':applied_unique_years_list,
        'current_accepted_count':current_accepted_count,
        'current_applied_count':current_applied_count,
        'schools':schools,
        'schoolCustomLabels': [entry["school"] for entry in schools],
        'schoolDataCounts': [entry["count"] for entry in schools],
    }

    return render(request, "in-depth-charts/tracker-count/tracker-count.html",context)

def school_scholar_summary(request):
    scholar_school = (
        ApplicantInfoRepositoryINB.objects.filter(tracker__in=["Ongoing", "Grantee"])
        .values("created_at__year", "school") 
        .annotate(school_count=Count("id"))
        .order_by("created_at__year", "school")  
    )

    school_data = {}
    for entry in scholar_school:
        school = entry["school"]
        year = entry["created_at__year"]
        count = entry["school_count"]
        if school not in school_data:
            school_data[school] = {"labels": [], "data": []}
        school_data[school]["labels"].append(year)
        school_data[school]["data"].append(count)

    school_counts = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing")
        .values("school")
        .annotate(count=Count("school"))
        .order_by("-count")
    )

    school_dropout = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Failed")
        .values("school")
        .annotate(drop_count=Count("school"))
        .order_by("-drop_count")
    )


    context ={
        'schoolData': school_data,
        'customLabels': [entry["school"] for entry in school_counts],
        'dataCounts': [entry["count"] for entry in school_counts],

        'dropCustomLabels': [entry["school"] for entry in school_dropout],
        'dropDataCounts': [entry["drop_count"] for entry in school_dropout],
    }
    return render(request, "in-depth-charts/school-grantees/school-grantees.html", context)

def yearlevel_scholar_summary(request):

    first_year_count = ApplicantInfoRepositoryINB.objects.filter(
        school_year="1st Year",
        tracker="Ongoing"
    ).count()

    second_year_count = ApplicantInfoRepositoryINB.objects.filter(
        school_year="2nd Year",
        tracker="Ongoing"
    ).count()


    third_year_count = ApplicantInfoRepositoryINB.objects.filter(
        school_year="3rd Year",
        tracker="Ongoing"
    ).count()


    fourth_year_count = ApplicantInfoRepositoryINB.objects.filter(
        school_year="4th Year",
        tracker="Ongoing"
    ).count()


    fifth_year_count = ApplicantInfoRepositoryINB.objects.filter(
        school_year="5th Year",
        tracker="Ongoing"
    ).count()

    first_year_school=(
        ApplicantInfoRepositoryINB.objects.filter(school_year="1st Year", tracker="Ongoing")
        .values('school')
        .annotate(first_count=Count('id'))
        .order_by('-first_count')  
    )

    second_year_school=(
        ApplicantInfoRepositoryINB.objects.filter(school_year="2nd Year", tracker="Ongoing")
        .values('school')
        .annotate(second_count=Count('id'))
        .order_by('-second_count')  
    )

    third_year_school=(
        ApplicantInfoRepositoryINB.objects.filter(school_year="3rd Year", tracker="Ongoing")
        .values('school')
        .annotate(third_count=Count('id'))
        .order_by('-third_count')  
    )

    fourth_year_school=(
        ApplicantInfoRepositoryINB.objects.filter(school_year="4th Year", tracker="Ongoing")
        .values('school')
        .annotate(fourth_count=Count('id'))
        .order_by('-fourth_count')  
    )

    fifth_year_school=(
        ApplicantInfoRepositoryINB.objects.filter(school_year="5th Year", tracker="Ongoing")
        .values('school')
        .annotate(fifth_count=Count('id'))
        .order_by('-fifth_count')  
    )

    first_year_course=(
        ApplicantInfoRepositoryINB.objects.filter(school_year="1st Year", tracker="Ongoing")
        .values('course')
        .annotate(first_course_count=Count('id'))
        .order_by('-first_course_count')  
    )

    second_year_course=(
        ApplicantInfoRepositoryINB.objects.filter(school_year="2nd Year", tracker="Ongoing")
        .values('course')
        .annotate(second_course_count=Count('id'))
        .order_by('-second_course_count')  
    )

    third_year_course=(
        ApplicantInfoRepositoryINB.objects.filter(school_year="3rd Year", tracker="Ongoing")
        .values('course')
        .annotate(third_course_count=Count('id'))
        .order_by('-third_course_count')  
    )

    fourth_year_course=(
        ApplicantInfoRepositoryINB.objects.filter(school_year="4th Year", tracker="Ongoing")
        .values('course')
        .annotate(fourth_course_count=Count('id'))
        .order_by('-fourth_course_count')  
    )

    fifth_year_course=(
        ApplicantInfoRepositoryINB.objects.filter(school_year="5th Year", tracker="Ongoing")
        .values('course')
        .annotate(fifth_course_count=Count('id'))
        .order_by('-fifth_course_count')  
    )



    context = {
        'first_year_count':first_year_count,
        'second_year_count':second_year_count,
        'third_year_count':third_year_count,
        'fourth_year_count':fourth_year_count,
        'fifth_year_count':fifth_year_count,

        'first_year_school':first_year_school,
        'firstSchoolCustomLabels': [entry["school"] for entry in first_year_school],
        'firstSchoolDataCounts': [entry["first_count"] for entry in first_year_school],

        'second_year_school':second_year_school,
        'secondSchoolCustomLabels': [entry["school"] for entry in second_year_school],
        'secondSchoolDataCounts': [entry["second_count"] for entry in second_year_school],

        'third_year_school':third_year_school,
        'thirdSchoolCustomLabels': [entry["school"] for entry in third_year_school],
        'thirdSchoolDataCounts': [entry["third_count"] for entry in third_year_school],

        'fourth_year_school':fourth_year_school,
        'fourthSchoolCustomLabels': [entry["school"] for entry in fourth_year_school],
        'fourthSchoolDataCounts': [entry["fourth_count"] for entry in fourth_year_school],


        'fifth_year_school':fifth_year_school,
        'fifthSchoolCustomLabels': [entry["school"] for entry in fifth_year_school],
        'fifthSchoolDataCounts': [entry["fifth_count"] for entry in fifth_year_school],

        'first_year_course':first_year_course,
        'firstCourseCustomLabels': [entry["course"] for entry in first_year_course],
        'firstCourseDataCounts': [entry["first_course_count"] for entry in first_year_course],

        'second_year_course':second_year_course,
        'secondCourseCustomLabels': [entry["course"] for entry in second_year_course],
        'secondCourseDataCounts': [entry["second_course_count"] for entry in second_year_course],

        'third_year_course':third_year_course,
        'thirdCourseCustomLabels': [entry["course"] for entry in third_year_course],
        'thirdCourseDataCounts': [entry["third_course_count"] for entry in third_year_course],

        'fourth_year_course':fourth_year_course,
        'fourthCourseCustomLabels': [entry["course"] for entry in fourth_year_course],
        'fourthCourseDataCounts': [entry["fourth_course_count"] for entry in fourth_year_course],


        'fifth_year_course':fifth_year_course,
        'fifthCourseCustomLabels': [entry["course"] for entry in fifth_year_course],
        'fifthCourseDataCounts': [entry["fifth_course_count"] for entry in fifth_year_course],
    }

    return render(request, "in-depth-charts/year-tracker/year-tracker.html", context)

def course_scholar_summary(request):
    applicant_course=(
        ApplicantInfoRepositoryINB.objects.filter( tracker="Ongoing")
        .values('course')
        .annotate(course_count=Count('id'))
        .order_by('-course_count')  
    )

    context = {
        "applicant_courses": applicant_course,
        'CourseCustomLabels': [entry["course"] for entry in applicant_course],
        'CourseDataCounts': [entry["course_count"] for entry in applicant_course],
    }

    return render(request,"in-depth-charts/course-grantees/course-grantees.html",context)


def barangay_summary(request):
    barangay_counts = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing")
        .values("barangay")
        .annotate(course_count=Count("barangay"))
        .order_by("-course_count")
    )

    barangay_graduates = (
        ApplicantInfoRepositoryINB.objects.filter(status="Graduated")
        .values("barangay")
        .annotate(graduate_count=Count("barangay"))
        .order_by("-graduate_count")
    )
    
    barangay = ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing").values_list("barangay", flat=True).distinct()

    barangay_courses = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing")
        .values("barangay", "course")  
        .annotate(courses_count=Count("course"))  
        .order_by("-courses_count")
    )

    print(barangay_courses)


    context = {
        "barangay_counts": barangay_counts,

        'graduatesCustomLabels': [entry["barangay"] for entry in barangay_graduates],  
        'graduatesDataCounts': [entry["graduate_count"] for entry in barangay_graduates],

        'barangay': barangay,
        'coursesCustomLabels': [entry["course"] for entry in barangay_courses],  
        'coursesDataCounts': [entry["courses_count"] for entry in barangay_courses],



    }
    return render(request, "in-depth-charts/barangay/barangay_data.html", context)





def inb_data_visualization(request):

    ongoing_scholars_count = (ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing").count())

    graduated_scholars_count = ApplicantInfoRepositoryINB.objects.filter(status="Graduated").count()
    print(graduated_scholars_count)

    unsuccessful_scholar_count = ApplicantInfoRepositoryINB.objects.filter(status="Failed").count()

    rejected_scholars_count = ApplicantInfoRepositoryINB.objects.filter(status="Rejected").count()
   
    total_failed_applicants = rejected_scholars_count + unsuccessful_scholar_count

    gender_data = (
        ApplicantInfoRepositoryINB.objects.filter(status="Grantee")
        .values("gender")
        .annotate(count=models.Count("gender"))
    )

    labels = [entry["gender"] for entry in gender_data]
    counts = [entry["count"] for entry in gender_data]

    accepted_scholar = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing")
        .values("created_at__year")
        .annotate(accepted_scholar_count=Count("id"))
        .order_by("created_at__year")  
    )
   

    applied_scholar = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Rejected")
        .values("created_at__year")
        .annotate(applied_scholar_count=Count("id"))
        .order_by("created_at__year")  
    )

    accepted_unique_years_list = sorted(set(entry["created_at__year"] for entry in accepted_scholar))
    applied_unique_years_list = sorted(set(entry["created_at__year"] for entry in applied_scholar))

    school_counts = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing")
        .values("school")
        .annotate(count=Count("school"))
        .order_by("-count")
    )

    first_year_count = ApplicantInfoRepositoryINB.objects.filter(
        school_year="1st Year",
        tracker="Ongoing"
    ).count()

    second_year_count = ApplicantInfoRepositoryINB.objects.filter(
        school_year="2nd Year",
        tracker="Ongoing"
    ).count()


    third_year_count = ApplicantInfoRepositoryINB.objects.filter(
        school_year="3rd Year",
        tracker="Ongoing"
    ).count()


    fourth_year_count = ApplicantInfoRepositoryINB.objects.filter(
        school_year="4th Year",
        tracker="Ongoing"
    ).count()


    fifth_year_count = ApplicantInfoRepositoryINB.objects.filter(
        school_year="5th Year",
        tracker="Ongoing"
    ).count()

    applicant_course=(
        ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing")
        .values('course')
        .annotate(course_count=Count('id'))
        .order_by('-course_count')  
    )




#above goods

    barangay_counts = (
        ApplicantInfoRepositoryINB.objects.filter(tracker="Ongoing")
        .values("barangay")
        .annotate(course_count=Count("barangay"))
        .order_by("-course_count")
    )

    context = {
       


        "barangay_counts": barangay_counts, 
    

        'ongoing_scholars_count': ongoing_scholars_count,
        'graduated_scholars_count': graduated_scholars_count,
        'total_failed_applicants': total_failed_applicants,
        'gender_date':gender_data,
        'labels': labels,
        'counts': counts,
        'accepted_scholar':accepted_scholar,
        'accepted_unique_years_list':accepted_unique_years_list,
        'applied_scholar':applied_scholar,
        'applied_unique_years_list':applied_unique_years_list,
        'customLabels': [entry["school"] for entry in school_counts],
        'dataCounts': [entry["count"] for entry in school_counts],

        'first_year_count':first_year_count,
        'second_year_count':second_year_count,
        'third_year_count':third_year_count,
        'fourth_year_count':fourth_year_count,
        'fifth_year_count':fifth_year_count,
               
        "applicant_courses": applicant_course,
        'CourseCustomLabels': [entry["course"] for entry in applicant_course],
        'CourseDataCounts': [entry["course_count"] for entry in applicant_course],
    }

    return render(request, "inb-dashboard.html", context)




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

#done
def inb_filter_applicants(request):
    if CollegeStudentApplication.objects.exists():
        applicants_to_transfer = CollegeStudentApplication.objects.all()

        with transaction.atomic():
            try:
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
                        ).update(status="Grantee", tracker = "Ongoing")    

                        CollegeStudentApplication.objects.filter(
                            control_number=applicant.control_number
                        ).delete()

                    else:
                        applicant.requirement = "Incomplete"
                        ApplicantInfoRepositoryINB.objects.filter(
                            control_number=applicant.control_number
                        ).update(status="Assessment", tracker="Assessment")
                    
                        CollegeStudentApplication.objects.filter(
                            control_number=applicant.control_number
                        ).delete()

                messages.success(request, "Applicants have been successfully filtered.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect("inb_applicant_list")

    else:
        messages.warning(request, "There are no applicants to filter.")

    return redirect("inb_applicant_list")


def inb_filter_assessment(request):
    applicants_to_transfer = ApplicantInfoRepositoryINB.objects.filter(
        tracker__in=["Accepted", "Failed"]
    )

    if applicants_to_transfer.exists():
        for applicant in applicants_to_transfer:
            try:
                (applicant_info, created,) = ApplicantInfoRepositoryINB.objects.get_or_create(control_number=applicant.control_number)

                if created:
                    if applicant.tracker == "Accepted":
                        applicant_info.tracker = "Accepted"
                    elif applicant.tracker == "Failed":
                        applicant_info.tracker = "Failed"
                    applicant_info.save()

                if applicant.tracker == "Accepted":
                    ApplicantInfoRepositoryINB.objects.filter(control_number=applicant.control_number).update(status="Grantee", tracker="Grantee")
                elif applicant.tracker == "Failed":
                    ApplicantInfoRepositoryINB.objects.filter(control_number=applicant.control_number).update(status="Rejected", tracker="Rejected")

            

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


# ------------------------------------------------------------------------------------------------------------------------


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

        accepted_applicants = ApplicantInfoRepositoryINB.objects.values_list(
            "control_number", flat=True
        )
        

        query = request.GET.get("q")
        filtered_applicants = all_applicants.exclude(
            control_number__in=list(accepted_applicants) 
        )
        if query:
            filtered_applicants = filtered_applicants.filter(
                Q(control_number__icontains=query)
                | Q(first_name__icontains=query)
                | Q(middle_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(course__icontains=query)
                | Q(school__icontains=query)
            )

        # Filter Query
        selected_schools = request.GET.getlist("schools")
        selected_courses = set(request.GET.getlist("courses"))
        selected_gender = request.GET.getlist("gender")
        selected_requirement = request.GET.getlist("requirement")

        if selected_schools:
            filtered_applicants = filtered_applicants.filter(school__in=selected_schools)
        if selected_courses:
            filtered_applicants = filtered_applicants.filter(course__in=selected_courses)
        if selected_gender:
            filtered_applicants = filtered_applicants.filter(gender__in=selected_gender)
        if selected_requirement: 
            filtered_applicants = filtered_applicants.filter(requirement__in=selected_requirement)

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

        paginator = Paginator(records, 20)
        page_number = request.GET.get("page")
        page = paginator.get_page(page_number)

        context = {
            "records": page,
            "form": form,
            "import_form": import_form,
            "export_form": export_form,
            "schools": schools,
            "courses": courses,
            "filtered_applicants": filtered_applicants,
        }

        return render(request, "INB/applicant_list.html", context)




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


        paginator = Paginator(records, 20) 
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

#changes
def inb_applicant_info(request, status, control_number):
    if request.user.is_authenticated:
        if status == "Grantee":
            model_class = ApplicantInfoRepositoryINB.objects.filter(status="Grantee")
            grade_class = StudentGrade
            template = "INB/passed_info.html"
        elif status == "Assessment":
            model_class = ApplicantInfoRepositoryINB.objects.filter(status="Assessment")
            template = "INB/inb_pending_info.html"
            form_class = INBPendingApplicants
        elif status == "Rejected":
            model_class = ApplicantInfoRepositoryINB.objects.filter(status="Rejected")
            template = "INB/failed_info.html"
        else:
            messages.error(request, "Invalid status parameter.")
            return redirect("home")

        if request.method == "POST" and status == "Assessment":
            form = form_class(request.POST)
            if form.is_valid():
                pending_applicant = get_object_or_404(
                    model_class, control_number=control_number
                )
                pending_applicant.tracker = form.cleaned_data["tracker"]
                pending_applicant.remarks = form.cleaned_data["remarks"]
                pending_applicant.save()

                messages.success(
                    request,
                    f"{status.capitalize()} applicant information updated successfully.",
                )
                return redirect("inb_pending_applicant")

        elif request.method == "GET":
            if status == "Grantee":
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

            elif status == "Assessment":
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

            elif status == "Rejected":
                failed_applicant = get_object_or_404(
                    model_class, control_number=control_number
                )
                return render(
                    request,
                    template,
                    {"failed_applicant": failed_applicant, "status": status},
                )

    else:
        messages.error(request, "You don't have permission.")
        return redirect("home")


#changes
def inb_applicant_list(request, status):
    if request.user.is_authenticated:
        if status == "Grantee":
            model_class = ApplicantInfoRepositoryINB.objects.filter(status="Grantee")
            template = "INB/accepted_applicants.html"

        elif status == "Assessment":
            model_class = ApplicantInfoRepositoryINB.objects.filter(status="Assessment")
            template = "INB/inb_pending_list.html"

        elif status == "Rejected":
            model_class = ApplicantInfoRepositoryINB.objects.filter(status="Rejected")
            template = "INB/rejected_applicants.html"
        else:
            messages.error(request, "Invalid status parameter.")
            return redirect("home")

        applicants_list = model_class 

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

#changes
def delete_record(request, control_number, model_name):
    if request.user.is_authenticated:
        list_view = "home"

        model_map = {
            "application": (CollegeStudentApplication, "inb_applicant_list"),
            "inb_passed": (ApplicantInfoRepositoryINB, "inb_passed_applicant"),
            "inb_pending": (ApplicantInfoRepositoryINB, "inb_pending_applicant"),
            "inb_failed": (ApplicantInfoRepositoryINB, "inb_failed_applicant"),
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
            record = get_object_or_404(model, control_number=control_number)
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
            try:
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

                    subject_cols = [
                        col for col in df.columns if col.startswith("SUBJECT")
                    ]
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
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

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

        student_grade_queryset = StudentGrade.objects.filter(
            control_number=control_number
        )

        if student_grade_queryset.exists():
            student_grade = student_grade_queryset.first()
            gwa = student_grade.gwa
        else:
            gwa = 0

        student_grades.append(
            StudentGradeRepository(
                control_number=control_number,
                school_year=school_year,
                semester=sem,
                gwa=gwa,
            )
        )

  
    StudentGrade.objects.all().delete()
    StudentGradeRepository.objects.bulk_create(student_grades)

    for student in data_update:
        sem = student.semester  
    for student in data_update:
        if student.semester == "1st Semester":
            student.semester = "2nd Semester"
        elif student.semester == "2nd Semester":
            student.semester = "1st Semester"

        if student.semester == "1st Semester":
            if student.school_year == "1st Year":
                student.school_year = "2nd Year"
            elif student.school_year == "2nd Year":
                student.school_year = "3rd Year"
            elif student.school_year == "3rd Year":
                student.school_year = "4th Year"
            elif student.school_year == "4th Year":
                student.school_year = "5th Year"
            elif student.school_year == "5th Year":
                student.school_year = "Graduated"
        elif student.semester == "2nd Semester":
            if student.school_year == "1st Year":
                student.school_year = "1st Year"
            elif student.school_year == "2nd Year":
                student.school_year = "2nd Year"
            elif student.school_year == "3rd Year":
                student.school_year = "3rd Year"
            elif student.school_year == "4th Year":
                student.school_year = "4th Year"
            elif student.school_year == "5th Year":
                student.school_year = "5th Year"

    
        student.save()

    messages.success(request, "Semester Successfully Ended")
    return redirect("inb_passed_applicant")

