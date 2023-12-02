from django.shortcuts import render, redirect, get_object_or_404
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
)
from .models import (
    CollegeStudentApplication,
    CollegeRequirements,
    CollegeStudentAccepted,
    CollegeStudentRejected,
    ApplicantInfoRepositoryINB,
    FinancialAssistanceApplication,
    FinancialAssistanceRequirement,
    FinancialAssistanceAccepted,
    FinancialAssistanceRejected,
    FinancialAssistanceInfoRepository,
    INBRequirementRepository,
    FARequirementRepository,
    INBSchool,
    INBCourse,
)
from django.db.models import Count
from django.http import HttpResponse
import csv
import pandas as pd
from import_export import resources
from django.db.models import Q
import json


class CollegeStudentApplicationResource(resources.ModelResource):
    class Meta:
        model = CollegeStudentApplication
        import_id_fields = ("Control Number",)


def home(request):
    return render(request, "home.html", {})


# import ----------------------------------------------------------------------------------------------------------------------------------
# problem fk nan&update
from django.db import IntegrityError
from django.contrib import messages


# INB import
def import_excel(request):
    if request.method == "POST":
        form = ApplicantUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            df = pd.read_excel(file, na_values=["N/A", "-", "Not Available"])

            # Replace NaN values with "N/A"
            df = df.fillna("N/A")

            # Convert date columns to the correct format
            date_columns = ["Date of Birth"]  # Add other date columns if needed
            for col in date_columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime(
                    "%Y-%m-%d"
                )

            applicant_count = 0

            for index, row in df.iterrows():
                try:
                    if "Desired Course" in df.columns:
                        applicant = CollegeStudentApplication(
                            control_number=row["Control Number"],
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
                            father_educational_attainment=row[
                                "Father Educational Attainment"
                            ],
                            father_employer=row["Father Employer"],
                            father_occupation=row["Father Occupation"],
                            mother_name=row["Mother Name"],
                            mother_voter_status=row["Mother Voter Status"],
                            mother_educational_attainment=row[
                                "Mother Educational Attainment"
                            ],
                            mother_employer=row["Mother Employer"],
                            mother_occupation=row["Mother Occupation"],
                            guardian_name=row["Legal Guardian"],
                            guardian_voter_status=row["Guardian Voter Status"],
                            guardian_educational_attainment=row[
                                "Guardian Educational Attainment"
                            ],
                            guardian_employer=row["Guardian Employer"],
                            guardian_occupation=row["Guardian Occupation"],
                        )
                    else:
                        # Check if sibling_count is 0 or 'N/A' before creating FinancialAssistanceApplication
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
                            sibling_name=row["Sibling Name"],
                            sibling_DOB=row["Sibling Date of Birth"],
                            sibling_age=row["Sibling Age"],
                            sibling_address=row["Sibling Address"],
                        )
                    applicant.save()
                    applicant_count += 1
                except IntegrityError:
                    messages.warning(
                        request,
                        f'Duplicate entry found for {row["Control Number"]}. Skipped.',
                    )

            messages.success(
                request, f"{applicant_count} applicant(s) imported successfully."
            )

            # Check if "Desired Course" is not in columns
            if "Desired Course" not in df.columns:
                return redirect("fa_applicant_list")

            return redirect("inb_applicant_list")

    else:
        form = ApplicantUploadForm()
    return render(request, "INB/import.html", {"form": form})


# ---------------------------------------------------------------------------------------------------------------------------------------


# export ----------------------------------------------------------------------------------------------------------------------------------


def csv_record(request):
    if request.method == "POST":
        form = ExportForm(request.POST)

        if form.is_valid():
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=record.csv"

            writer = csv.writer(response)

            include_id = form.cleaned_data.get("include_id", False)
            include_name = form.cleaned_data.get("include_name", False)
            include_course = form.cleaned_data.get("include_course", False)
            include_school = form.cleaned_data.get("include_school", False)

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
        form = ExportForm()

    return render(request, "INB/export_form.html", {"form": form})


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Login  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def login_user(request):
    if request.method == "POST":
        username = request.POST["user_name"]
        password = request.POST["user_password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Incorrect username or password.")
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


# render data in dashboard
def data_visualization(request):
    school_counts = (
        CollegeStudentApplication.objects.values("school")
        .exclude(school="0")
        .annotate(count=Count("school"))
        .order_by("-count")
    )

    total_students = sum(school_count["count"] for school_count in school_counts)

    students_per_school = {}
    for school_count in school_counts:
        school = school_count["school"]
        count = school_count["count"]
        students_per_school[school] = count

    data = []
    labels = []
    for school_count in school_counts:
        percentage = (school_count["count"] / total_students) * 100
        labels.append(school_count["school"])
        data.append(percentage)

    if not request.session.get("login_message_displayed", False):
        messages.success(request, "You have logged in successfully!")
        request.session["login_message_displayed"] = True

    return render(
        request,
        "dashboard.html",
        {
            "labels": labels,
            "data": data,
            "count": total_students,
            "students_per_school": students_per_school,
        },
    )


#  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def fa_filter_applicants(request):
    if FinancialAssistanceApplication.objects.exists():
        applicants_to_transfer = FinancialAssistanceApplication.objects.all()

        for applicant in applicants_to_transfer:
            FinancialAssistanceInfoRepository.objects.get_or_create(
                control_number=applicant.control_number,
                fullname=f"{applicant.last_name}, {applicant.first_name} {applicant.middle_name}. {applicant.suffix}",
                date_of_birth=applicant.date_of_birth,
                place_of_birth=applicant.place_of_birth,
                gender=applicant.gender,
                religion=applicant.religion,
                address=applicant.address,
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
                sibling_name=applicant.sibling_name,
                sibling_DOB=applicant.sibling_DOB,
                sibling_age=applicant.sibling_age,
                sibling_address=applicant.sibling_address,
            )

        accepted_applicants = FinancialAssistanceApplication.objects.filter(
            control_number__in=FinancialAssistanceRequirement.objects.filter(
                requirement=8
            ).values("control_number")
        ).distinct()

        rejected_applicants = FinancialAssistanceApplication.objects.exclude(
            control_number__in=accepted_applicants.values("control_number")
        ).distinct()

        for applicant in accepted_applicants:
            FinancialAssistanceInfoRepository.objects.filter(
                control_number=applicant.control_number
            ).update(status="Accepted")
            FinancialAssistanceAccepted.objects.create(
                control_number=applicant.control_number,
                fullname=f"{applicant.last_name}, {applicant.first_name} {applicant.middle_name}. {applicant.suffix}",
            )

        for applicant in rejected_applicants:
            FinancialAssistanceInfoRepository.objects.filter(
                control_number=applicant.control_number
            ).update(status="Rejected")
            FinancialAssistanceRejected.objects.create(
                control_number=applicant.control_number,
                fullname=f"{applicant.last_name}, {applicant.first_name} {applicant.middle_name}",
            )

        FinancialAssistanceApplication.objects.filter(
            Q(control_number__in=accepted_applicants.values("control_number"))
            | Q(control_number__in=rejected_applicants.values("control_number"))
        ).delete()

        messages.success(request, "Applicants have been successfully filtered.")
    else:
        messages.warning(request, "There are no applicants to filter.")

    return redirect("fa_applicant_list")


def inb_filter_applicants(request):
    if CollegeStudentApplication.objects.exists():
        applicants_to_transfer = CollegeStudentApplication.objects.all()

        for applicant in applicants_to_transfer:
            ApplicantInfoRepositoryINB.objects.get_or_create(
                control_number=applicant.control_number,
                fullname=f"{applicant.last_name}, {applicant.first_name} {applicant.middle_name}",
                address=applicant.address,
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

        accepted_applicants = CollegeStudentApplication.objects.filter(
            collegerequirements__requirement=13
        ).distinct()

        rejected_applicants = CollegeStudentApplication.objects.exclude(
            collegerequirements__requirement=13
        ).distinct()

        for applicant in accepted_applicants:
            ApplicantInfoRepositoryINB.objects.filter(
                control_number=applicant.control_number
            ).update(status="Accepted")
            CollegeStudentAccepted.objects.create(
                control_number=applicant.control_number,
                fullname=f"{applicant.last_name}, {applicant.first_name} {applicant.middle_name}",
                school=applicant.school,
                course=applicant.course,
            )

        for applicant in rejected_applicants:
            ApplicantInfoRepositoryINB.objects.filter(
                control_number=applicant.control_number
            ).update(status="Rejected")
            CollegeStudentRejected.objects.create(
                control_number=applicant.control_number,
                fullname=f"{applicant.last_name}, {applicant.first_name} {applicant.middle_name}",
            )

        CollegeStudentApplication.objects.filter(
            Q(control_number__in=accepted_applicants.values("control_number"))
            | Q(control_number__in=rejected_applicants.values("control_number"))
        ).delete()

        messages.success(request, "Applicants have been successfully filtered.")
    else:
        messages.warning(request, "There are no applicants to filter.")

    return redirect("inb_applicant_list")


# ------------------------------------------------------------------------------------------------------------------------


# CRUD
def view_applicant_table(request):
    if request.user.is_authenticated:
        all_applicants = CollegeStudentApplication.objects.all()

        accepted_applicants = CollegeStudentAccepted.objects.values_list(
            "control_number", flat=True
        )
        rejected_applicants = CollegeStudentRejected.objects.values_list(
            "control_number", flat=True
        )

        filtered_applicants = all_applicants.exclude(
            control_number__in=list(accepted_applicants) + list(rejected_applicants)
        )

        requirement_records = CollegeRequirements.objects.all()

    if not request.session.get("login_message_displayed", False):
        messages.success(request, "You have logged in successfully!")
        request.session["login_message_displayed"] = True

    return render(
        request,
        "INB/applicant_list.html",
        {"records": zip(filtered_applicants, requirement_records)},
    )


def financial_assistance_list(request):
    if request.user.is_authenticated:
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

        requirement_records = FinancialAssistanceRequirement.objects.all()

    if not request.session.get("login_message_displayed", False):
        messages.success(request, "You have logged in successfully!")
        request.session["login_message_displayed"] = True

    return render(
        request,
        "FA/applicant_list.html",
        {"records": zip(filtered_applicants, requirement_records)},
    )


# ------------------------------------------------------------------------------------------------------------------------
# done refactoring
def inb_applicant_info(request, status, control_number):
    if request.user.is_authenticated:
        if status == "passed":
            model_class = CollegeStudentAccepted
            template = "INB/passed_info.html"
        elif status == "failed":
            model_class = CollegeStudentRejected
            template = "INB/failed_info.html"
        else:
            messages.error(request, "Invalid status parameter.")
            return redirect("home")

        try:
            if status == "passed":
                passed_applicant = get_object_or_404(
                    model_class, control_number=control_number
                )
                return render(
                    request,
                    template,
                    {"passed_applicant": passed_applicant, "status": status},
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
        elif status == "failed":
            model_class = CollegeStudentRejected
            template = "INB/rejected_applicants.html"
        else:
            messages.error(request, "Invalid status parameter.")
            return redirect("home")

        applicants = model_class.objects.all()
        return render(request, template, {"applicants": applicants})
    else:
        messages.error(request, "You don't have permission.")
        return redirect("home")


def fa_applicant_info(request, status, control_number):
    if request.user.is_authenticated:
        if status == "passed":
            model_class = FinancialAssistanceAccepted
            template = "FA/fa_passed_info.html"
        elif status == "failed":
            model_class = FinancialAssistanceRejected
            template = "FA/fa_failed_info.html"
        else:
            messages.error(request, "Invalid status parameter.")
            return redirect("home")

        try:
            if status == "passed":
                passed_applicant = get_object_or_404(
                    model_class, control_number=control_number
                )
                return render(
                    request,
                    template,
                    {"passed_applicant": passed_applicant, "status": status},
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
        except model_class.DoesNotExist:
            messages.error(request, f"{status.capitalize()} applicant not found.")
            return redirect(f"inb_{status}_applicant")

    else:
        messages.error(request, "You don't have permission.")
        return redirect("home")


def fa_applicant_list(request, status):
    if request.user.is_authenticated:
        if status == "passed":
            model_class = FinancialAssistanceAccepted
            template = "FA/fa_passed_list.html"
        elif status == "failed":
            model_class = FinancialAssistanceRejected
            template = "FA/fa_failed_list.html"
        else:
            messages.error(request, "Invalid status parameter.")
            return redirect("home")

        applicants = model_class.objects.all()
        return render(request, template, {"applicants": applicants})
    else:
        messages.error(request, "You don't have permission.")
        return redirect("home")


# ------------------------------------------------------------------------------------------------------------------------


def inb_applicant_information(request, pk):
    if request.user.is_authenticated:
        try:
            records = CollegeStudentApplication.objects.get(id=pk)
            requirements = CollegeRequirements.objects.filter(control=records)

        except CollegeStudentApplication.DoesNotExist:
            records = None
            requirements = []

        return render(
            request,
            "INB/applicants_info.html",
            {"records": records, "requirements": requirements},
        )
    else:
        messages.success(request, "You need to be logged in to see this data!")
        return redirect("home")


def fa_applicant_information(request, pk):
    if request.user.is_authenticated:
        try:
            records = FinancialAssistanceApplication.objects.get(id=pk)
            requirements = FinancialAssistanceRequirement.objects.filter(
                control=records
            )
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
            "inb_failed": (CollegeStudentRejected, "inb_failed_applicant"),
            "fa_application": (FinancialAssistanceApplication, "fa_applicant_list"),
            "fa_passed": (FinancialAssistanceAccepted, "fa_passed_applicant"),
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
    if request.user.is_authenticated:
        if request.method == "POST":
            requirements = CollegeRequirements.objects.filter(
                control__control_number=control_number
            )
            for requirement in requirements:
                for requirement_field in (
                    "req_a",
                    "req_b",
                    "req_c",
                    "req_d",
                    "req_e",
                    "req_f",
                    "req_g",
                    "req_h",
                    "req_i",
                    "req_j",
                    "req_k",
                    "req_l",
                    "req_m",
                ):
                    checkbox_name = f"{requirement_field}_{requirement.id}"
                    approved = checkbox_name in request.POST
                    setattr(
                        requirement, requirement_field, "True" if approved else "False"
                    )
                requirement.save()

            messages.success(request, "Requirements have been updated!!")
            return redirect("inb_applicant_list")

        requirements = CollegeRequirements.objects.filter(
            control__control_number=control_number
        )
        return render(
            request,
            "INB/requirement.html",
            {"requirements": requirements, "control_number": control_number},
        )
    else:
        messages.error(request, "You need to be logged in for this process.")
        return redirect("home")


def fa_requirement_list(request, control_number):
    if request.user.is_authenticated:
        if request.method == "POST":
            requirements = FinancialAssistanceRequirement.objects.filter(
                control__control_number=control_number
            )
            for requirement in requirements:
                for requirement_field in (
                    "req_a",
                    "req_b",
                    "req_c",
                    "req_d",
                    "req_e",
                    "req_f",
                    "req_g",
                    "req_h",
                ):
                    checkbox_name = f"{requirement_field}_{requirement.id}"
                    approved = checkbox_name in request.POST
                    setattr(
                        requirement, requirement_field, "True" if approved else "False"
                    )
                requirement.save()

            messages.success(request, "Requirements have been updated!!")
            return redirect("fa_applicant_list")

        requirements = FinancialAssistanceRequirement.objects.filter(
            control__control_number=control_number
        )
        return render(
            request,
            "FA/requirement.html",
            {"requirements": requirements, "control_number": control_number},
        )
    else:
        messages.error(request, "You need to be logged in for this process.")
        return redirect("home")


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Navbar
def navbar_user(request):
    active_user = {"user": request.user}

    return render(request, "navbar.html", active_user)


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def update_requirement(request):
    return render(request, "Admin/update-requirement.html")


def add_requirement(request, form_type):
    if request.user.is_authenticated:
        if form_type == "inb":
            form = INBRequirementList(request.POST or None)
            template = "Admin/inb-requirements.html"
            model_class = INBRequirementRepository

        elif form_type == "fa":
            form = FARequirementList(request.POST or None)
            template = "Admin/fa-requirements.html"
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

        return render(request, template, {"form": form})
    else:
        messages.error(request, "You need to be logged in for this process.")
        return redirect("home")


def school_course_list(request):
    schools_with_courses = INBSchool.objects.prefetch_related("inbcourse_set").all()
    schools = INBSchool.objects.all()

    return render(
        request,
        "Admin/list_course_school.html",
        {
            "schools_with_courses": schools_with_courses,
            "schools": schools,
        },
    )


def create_school(request):
    if request.method == "POST":
        form = INBSchoolForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "School Successfully Added")
            return redirect("sc_list")
    else:
        form = INBSchoolForm()

    return render(request, "Admin/list-school-course.html", {"school_form": form})


def add_course(request):
    if request.method == "POST":
        form = INBCourseForm(request.POST)
        if form.is_valid():
            course_instance = form.save(commit=False)

            selected_schools = request.POST.getlist("schools")

            associated_schools = []

            for school_id in selected_schools:
                school = get_object_or_404(INBSchool, pk=school_id)
                associated_schools.append(school)

            course_instance.save()
            course_instance.school.set(associated_schools)

            if selected_schools:
                course_instance.school_id = selected_schools[0]
                course_instance.save()

            messages.success(request, "Course Successfully Added")
            return redirect("sc_list")
    else:
        form = INBCourseForm()

    schools = INBSchool.objects.all()
    return render(
        request,
        "Admin/list_course_school.html",
        {"course_form": form, "schools": schools},
    )


def test1(request):
    return render(request, "cms-forms.html")
