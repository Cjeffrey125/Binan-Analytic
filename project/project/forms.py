from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django import forms
from base.models import (
    CollegeStudentApplication,
    ApplicantInfoRepositoryINB,
    FinancialAssistanceApplication,
    INBRequirementRepository,
    FARequirementRepository,
    INBSchool,
    INBCourse,
    INBApplicationRequirements,
    FAApplicationRequirements,
    FinancialAssistanceAssesment,
    ProfileImage,
)


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = ProfileImage
        fields = ["image"]


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]


class INBSchoolForm(forms.ModelForm):
    def clean_school(self):
        school = self.cleaned_data.get("school")
        if INBSchool.objects.filter(
            school=school
        ).exists():
            raise forms.ValidationError("School Already Exist.")
        return school
    
    school = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Add School",
                "class": "school-input",
                "required": "Please enter the school name.",
                "unique": "This name is already existing.",
            }
        ),
        label="",
    )

    class Meta:
        model = INBSchool
        fields = ["school"]


class INBCourseForm(forms.ModelForm):
    class Meta:
        model = INBCourse
        fields = ["course", "acronym"]


class INBRequirementList(forms.ModelForm):
    class Meta:
        model = INBRequirementRepository
        fields = ["requirement"]
        widgets = {
            "requirement": forms.TextInput(
                attrs={"placeholder": "Add New Requirements", "class": "form-control"}
            )
        }


class INBRequirementForm(forms.ModelForm):
    class Meta:
        model = INBApplicationRequirements
        fields = ["is_met"]
        widgets = {
            "is_met": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class FARequirementList(forms.ModelForm):
    class Meta:
        model = FARequirementRepository
        fields = ["requirement"]
        widgets = {
            "requirement": forms.TextInput(
                attrs={"placeholder": "Add New Requirements", "class": "form-control"}
            )
        }


class FARequirementForm(forms.ModelForm):
    class Meta:
        model = FAApplicationRequirements
        fields = ["is_met"]
        widgets = {
            "is_met": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ApplicantUploadForm(forms.Form):
    file = forms.FileField(
        label="Choose Excel file", widget=forms.FileInput(attrs={"accept": ".xlsx"})
    )


class GradeUploadForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={"accept": ".xlsx"}))


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        label="",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Email Address"}
        ),
    )
    first_name = forms.CharField(
        label="",
        max_length="50",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First Name"}
        ),
    )
    last_name = forms.CharField(
        label="",
        max_length="50",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last Name"}
        ),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["username"].widget.attrs["placeholder"] = "User Name"
        self.fields["username"].label = ""
        self.fields[
            "username"
        ].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password1"].widget.attrs["placeholder"] = "Password"
        self.fields["password1"].label = ""
        self.fields[
            "password1"
        ].help_text = "<ul class=\"form-text text-muted small\"><li>Your password can't be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can't be a commonly used password.</li><li>Your password can't be entirely numeric.</li></ul>"

        self.fields["password2"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm Password"
        self.fields["password2"].label = ""
        self.fields[
            "password2"
        ].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class ExportForm(forms.Form):
    include_id = forms.BooleanField(
        required=True, initial=True, label="Include Student ID"
    )
    include_name = forms.BooleanField(
        required=False, initial=True, label="Include Student Name"
    )
    include_school = forms.BooleanField(
        required=False, initial=True, label="Include Student School"
    )
    include_course = forms.BooleanField(
        required=False, initial=True, label="Include Student Course"
    )


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class AddINBForm(forms.ModelForm):
    BARANGAY_CHOICES = [
        ("0", "Select Barangay"),
        ("Biñan", "Biñan"),
        ("Bungahan", "Bungahan"),
        ("Canlalay", "Canlalay"),
        ("Casile", "Casile"),
        ("Dela Paz", "Dela Paz"),
        ("Ganado", "Ganado"),
        ("Lankiwa", "Lankiwa"),
        ("Loma", "Loma"),
        ("Malaban", "Malaban"),
        ("Malamig", "Malamig"),
        ("Mamplasan", "Mamplasan"),
        ("Platero", "Platero"),
        ("Poblacion", "Poblacion"),
        ("San Antonio", "San Antonio"),
        ("San Francisco", "San Francisco"),
        ("San Jose", "San Jose"),
        ("San Vicente", "San Vicente"),
        ("Santo Domingo", "Santo Domingo"),
        ("Santo Niño", "Santo Niño"),
        ("Santo Tomas", "Santo Tomas"),
        ("Soro Soro", "Soro Soro"),
        ("Tubigan", "Tubigan"),
        ("Timbao", "Timbao"),
        ("Zapote", "Zapote"),
    ]

    SCHOOL_YEAR_CHOICES = [
        ("0", "Select Year"),
        ("1st Year", "1st Year"),
        ("2nd Year", "2nd Year"),
        ("3rd Year", "3rd Year"),
        ("4th Year", "4th Year"),
        ("5th Year", "5th Year"),
        ("Graduated", "Graduated"),
    ]

    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
    ]

    EDUCATIONAL_PROVIDERS = [
        ("Deped", "DepEd"),
        ("Non-Deped", "Non-DepEd"),
    ]

    VOTER_STATUS = [
        ("Registered Voter", ""),
    ]

    def clean_control_number(self):
        control_number = self.cleaned_data.get("control_number")
        if CollegeStudentApplication.objects.filter(
            control_number=control_number
        ).exists():
            raise forms.ValidationError("This control number is already in use.")
        return control_number

    control_number = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={
                "placeholder": "Control Number",
                "class": "control-number-input",
                "required": "Please enter your control number.",
                "unique": "This control number is already taken.",
            }
        ),
        label="",
    )

    school_year = forms.ChoiceField(
        required=True,
        choices=SCHOOL_YEAR_CHOICES,
        widget=forms.widgets.Select(),
        label="",
    )

    requirement = forms.CharField(
        required=False,
    )
    # Personal Data

    def validate_name(value):
        if not value.isalpha():
            raise ValidationError(
                "Invalid name: %(value)s. Only alphabetical characters are allowed.",
                code="invalid_name",
                params={"value": value},
            )

    first_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "name-input",
                "placeholder": "First name",
                "class": "form-control",
                "autocomplete": "off",
                "pattern": "[A-Za-z ]+",
                "title": "Enter Characters Only ",
            }
        ),
        label="",
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "name-input",
                "placeholder": "Last name",
                "class": "form-control",
                "autocomplete": "off",
                "pattern": "[A-Za-z ']+",
                "title": "Enter Characters Only ",
            }
        ),
        label="",
    )
    middle_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "name-input",
                "placeholder": "Middle Name",
                "class": "form-control",
                "autocomplete": "off",
                "pattern": "[A-Za-z ']+",
                "title": "Enter Characters Only ",
            }
        ),
        label="",
    )

    blkstr = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"class": "address-input-1", "placeholder": "Number/Block/Street"}
        ),
        help_text='<span class="subscript">Blk Street</span>',
        label="",
    )

    barangay = forms.ChoiceField(
        choices=BARANGAY_CHOICES,
        widget=forms.widgets.Select(),
        label="",
    )

    province = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "address-input-2",
                "placeholder": "Province",
                "class": "form-control",
                "autocomplete": "off",
                "pattern": "[A-Za-z ]+",
                "title": "Enter Characters Only ",
            }
        ),
        help_text='<span class="subscript">Province</span>',
        label="",
    )
    city = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "address-input-2",
                "placeholder": "City",
                "class": "form-control",
                "autocomplete": "off",
                "pattern": "[A-Za-z ]+",
                "title": "Enter Characters Only ",
            }
        ),
        help_text='<span class="subscript">City</span>',
        label="",
    )

    gender = forms.ChoiceField(
        required=True,
        choices=GENDER_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "radio-container"}),
        label="",
    )

    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={"class": "date-input", "type": "date", "value": "yyyy-mm-dd"}
        ),
        label="Date of Birth",
    )

    place_of_birth = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"class": "place-birth-input", "placeholder": "Place of Birth"}
        ),
        label="",
    )
    contact_no = forms.IntegerField(
        required=True,
        validators=[
            MinValueValidator(10000000000, "The number must be at least 1000000000."),
            MaxValueValidator(
                99999999999, "The number must be less than or equal to 99999999999."
            ),
        ],
        widget=forms.widgets.NumberInput(
            attrs={
                "class": "contact-input",
                "placeholder": "Contact Number",
                "autocomplete": "off",
                "pattern": "[0-9]+",
                "title": "Enter Numbers Only ",
                "maxlength": "10",
                "oninvalid": "this.setCustomValidity('Please enter your contact number.')",
                "oninput": "this.setCustomValidity(''); if(this.value.length > 11) { this.setCustomValidity('Contact number must be 11 digits.'); }",
            }
        ),
        label="",
    )

    email_address = forms.EmailField(
        required=True,
        widget=forms.widgets.EmailInput(
            attrs={"class": "half-input", "placeholder": "Email Address"}
        ),
        label="",
    )

    school = forms.ChoiceField(
        required=True,
        choices=[("0", "Choose School")],
        widget=forms.Select(attrs={"class": "custom-dropdown"}),
        label="",
    )

    course = forms.ChoiceField(
        required=True,
        choices=[("0", "Choose Course")],
        widget=forms.Select(attrs={"class": "course-dropdown"}),
        label="",
    )
    gwa = forms.CharField(
        required=True,
        widget=forms.widgets.NumberInput(
            attrs={
                "placeholder": "General Weighted Average",
                "class": "rank-gwa-input",
                "pattern": "[0-9]+",
                "title": "Enter Numbers Only ",
                "maxlength": "4",
                "oninvalid": "this.setCustomValidity('Please enter gwa.')",
            }
        ),
        label="",
    )
    rank = forms.CharField(
        required=True,
        widget=forms.widgets.NumberInput(
            attrs={
                "placeholder": "Rank",
                "class": "rank-gwa-input",
                "pattern": "[0-9]+",
                "title": "Enter Numbers Only ",
                "maxlength": "4",
                "oninvalid": "this.setCustomValidity('Please enter rank.')",
            }
        ),
        label="",
    )

    jhs = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Junior High School", "class": "prev-school"}
        ),
        label="",
    )
    jhs_address = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "SHS Address", "class": "prev-school"}
        ),
        label="",
    )

    jhs_educational_provider = forms.ChoiceField(
        required=True,
        choices=EDUCATIONAL_PROVIDERS,
        widget=forms.RadioSelect(attrs={"class": "radio-container"}),
        label="",
    )

    shs = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Senior High School", "class": "prev-school"}
        ),
        label="",
    )
    shs_address = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "SHS Address", "class": "prev-school"}
        ),
        label="",
    )

    shs_educational_provider = forms.ChoiceField(
        required=True,
        choices=EDUCATIONAL_PROVIDERS,
        widget=forms.RadioSelect(attrs={"class": "radio-container"}),
        label="",
    )

    # Family Data
    father_voter_status = forms.ChoiceField(
        required=False,
        choices=VOTER_STATUS,
        widget=forms.RadioSelect(attrs={"class": "radio-container"}),
        label="",
    )
    father_name = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={
                "placeholder": "Father Name",
                "class": "prev-school",
                "class": "form-control",
                "autocomplete": "off",
                "pattern": "[A-Za-z ' ]+",
                "title": "Enter Characters Only ",
            }
        ),
        label="",
    )
    father_educational_attainment = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Educational Attainment", "class": "prev-school"}
        ),
        label="",
    )
    father_occupation = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Occupation", "class": "prev-school"}
        ),
        label="",
    )
    father_employer = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Name of Employer", "class": "prev-school"}
        ),
        label="",
    )

    mother_voter_status = forms.ChoiceField(
        required=False,
        choices=VOTER_STATUS,
        widget=forms.RadioSelect(attrs={"class": "radio-container"}),
        label="",
    )
    mother_name = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={
                "placeholder": "Mother Name",
                "class": "prev-school",
                "class": "form-control",
                "autocomplete": "off",
                "pattern": "[A-Za-z ' ]+",
                "title": "Enter Characters Only ",
            }
        ),
        label="",
    )
    mother_educational_attainment = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Educational Attainment", "class": "prev-school"}
        ),
        label="",
    )
    mother_occupation = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Occupation", "class": "prev-school"}
        ),
        label="",
    )
    mother_employer = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Name of Employer", "class": "prev-school"}
        ),
        label="",
    )

    guardian_voter_status = forms.ChoiceField(
        required=False,
        choices=VOTER_STATUS,
        widget=forms.RadioSelect(attrs={"class": "radio-container"}),
        label="",
    )
    guardian_name = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={
                "placeholder": "Legal Guardian Name",
                "class": "prev-school",
                "class": "form-control",
                "autocomplete": "off",
                "pattern": "[A-Za-z ']+",
                "title": "Enter Characters Only ",
            }
        ),
        label="",
    )
    guardian_educational_attainment = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Educational Attainment", "class": "prev-school"}
        ),
        label="",
    )
    guardian_occupation = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Occupation", "class": "prev-school"}
        ),
        label="",
    )
    guardian_employer = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Name of Employer", "class": "prev-school"}
        ),
        label="",
    )

    def clean(self):
        cleaned_data = super().clean()

        father_name = cleaned_data.get("father_name")
        mother_name = cleaned_data.get("mother_name")
        guardian_name = cleaned_data.get("guardian_name")

        if not any([father_name, mother_name, guardian_name]):
            raise ValidationError(
                "At least one of Father, Mother, or Legal Guardian must be filled out."
            )

        return cleaned_data

    class Meta:
        model = CollegeStudentApplication

        exclude = ("user",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        distinct_courses = INBCourse.objects.values_list("course", flat=True).distinct()
        course_choices = [(course, course) for course in distinct_courses]
        self.fields["course"].choices = [("", "Select a course")] + course_choices

        schools = INBSchool.objects.all()
        school_choices = [(str(school.school), school.school) for school in schools]
        self.fields["school"].choices = [("0", "Choose School")] + school_choices


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class AddFinancialAssistanceForm(forms.ModelForm):
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
    ]

    SCHOOL_CHOICES = [
        ("0", "Preferred School"),
        (
            "Biñan Secondary School of Applied Academics",
            "Biñan Secondary School of Applied Academics",
        ),
        (
            "Biñan Integrated National High School",
            "Biñan Integrated National High School",
        ),
        ("Saint Francis National High School", "Saint Francis National High School"),
        ("Southville 5-A National High School", "Southville 5-A National High School"),
        (
            "Jacobo Z. Gonzales Memorial National High School",
            "Jacobo Z. Gonzales Memorial National High School",
        ),
        ("Dela Paz National High School", "Dela Paz National High School"),
        (
            "Biñan City Science and Technology High School",
            "Biñan City Science and Technology High School",
        ),
        ("Mamplasan National High School", "Mamplasan National High School"),
        (
            "Nereo R. Joaquin National High School",
            "Nereo R. Joaquin National High School",
        ),
    ]

    STRAND_CHOICE = [
        ("0", "Preferred Strand"),
        ("ABM", "Accountancy, Business, and Management"),
        ("HUMSS", "Humanities and Social Sciences"),
        ("STEM", "Science, Technology, Engineering, and Mathematics"),
        ("GAS", "General Academic Strand"),
        ("TVL", "Technical Vocational Livelihood (TVL) Track"),
        ("Sports", "Sports Track"),
        ("ArtsAndDesign", "Arts and Design Track"),
    ]

    TRACK_CHOICE = [
        ("0", "Preferred Track"),
        ("Academic Track", "Academic Track"),
        ("Vocational Track", "Vocational Track"),
        ("Technical Track", "Technical Track"),
    ]

    control_number = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Control Number", "class": "form-control"}
        ),
        label="",
    )

    requirement = forms.CharField(
        required=False,
    )

    # Personal Data
    first_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"class": "name-input", "placeholder": "First name"}
        ),
        label="",
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"class": "name-input", "placeholder": "Last name"}
        ),
        label="",
    )
    middle_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"class": "name-input", "placeholder": "Middle Name"}
        ),
        label="",
    )
    suffix = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"class": "form-control", "placeholder": "Suffix"}
        ),
        label="",
    )

    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={"class": "date-input", "type": "date", "value": "yyyy-mm-dd"}
        ),
        label="Date of Birth",
    )

    place_of_birth = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Place of Birth", "class": "form-control"}
        ),
        label="",
    )
    gender = forms.ChoiceField(
        required=True,
        choices=GENDER_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "radio-container"}),
        label="",
    )

    religion = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Religion", "class": "form-control"}
        ),
        label="",
    )

    blkstr = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"class": "address-input-1", "placeholder": "Number/Block/Street"}
        ),
        help_text='<span class="subscript">Blk Street</span>',
        label="",
    )
    barangay = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"class": "address-input-2", "placeholder": "Barangay"}
        ),
        help_text='<span class="subscript">Barangay</span>',
        label="",
    )
    province = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"class": "address-input-2", "placeholder": "Province"}
        ),
        help_text='<span class="subscript">Province</span>',
        label="",
    )
    city = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"class": "address-input-2", "placeholder": "City"}
        ),
        help_text='<span class="subscript">City</span>',
        label="",
    )

    email_address = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Email Address", "class": "form-control"}
        ),
        label="",
    )

    contact_no = forms.IntegerField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Contact No", "class": "form-control"}
        ),
        label="",
    )
    general_average = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "General Weighted Average", "class": "form-control"}
        ),
        label="",
    )

    school = forms.ChoiceField(
        required=True,
        choices=SCHOOL_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="",
    )
    school_address = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "SHS Address", "class": "form-control"}
        ),
        label="",
    )
    track = forms.ChoiceField(
        required=True,
        choices=TRACK_CHOICE,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="",
    )
    strand = forms.ChoiceField(
        required=True,
        choices=STRAND_CHOICE,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="",
    )

    # Family Data
    father_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Father Name", "class": "form-control"}
        ),
        label="",
    )
    father_age = forms.IntegerField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Age", "class": "form-control"}
        ),
        label="",
    )
    father_income = forms.IntegerField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Income", "class": "form-control"}
        ),
        label="",
    )
    father_occupation = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Occupation", "class": "form-control"}
        ),
        label="",
    )
    father_employer = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Name of Employer", "class": "form-control"}
        ),
        label="",
    )

    mother_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Mother Name", "class": "form-control"}
        ),
        label="",
    )
    mother_age = forms.IntegerField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Age", "class": "form-control"}
        ),
        label="",
    )
    mother_income = forms.IntegerField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Income", "class": "form-control"}
        ),
        label="",
    )
    mother_occupation = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Occupation", "class": "form-control"}
        ),
        label="",
    )
    mother_employer = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Name of Employer", "class": "form-control"}
        ),
        label="",
    )

    sibling_count = forms.IntegerField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Siblings", "class": "form-control"}
        ),
        label="",
    )

    a_sibling_name = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Name", "class": "form-control"}
        ),
        label="",
    )
    a_sibling_DOB = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"class": "date-input", "type": "date", "value": "yyyy-mm-dd"}
        ),
        label="Date of Birth",
    )
    a_sibling_age = forms.IntegerField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Age", "class": "form-control"}
        ),
        label="",
    )
    a_sibling_address = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Address", "class": "form-control"}
        ),
        label="",
    )

    b_sibling_name = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Name", "class": "form-control"}
        ),
        label="",
    )
    b_sibling_DOB = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"class": "date-input", "type": "date", "value": "yyyy-mm-dd"}
        ),
        label="Date of Birth",
    )
    b_sibling_age = forms.IntegerField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Age", "class": "form-control"}
        ),
        label="",
    )
    b_sibling_address = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Address", "class": "form-control"}
        ),
        label="",
    )

    c_sibling_name = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Name", "class": "form-control"}
        ),
        label="",
    )
    c_sibling_DOB = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"class": "date-input", "type": "date", "value": "yyyy-mm-dd"}
        ),
        label="Date of Birth",
    )
    c_sibling_age = forms.IntegerField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Age", "class": "form-control"}
        ),
        label="",
    )
    c_sibling_address = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Address", "class": "form-control"}
        ),
        label="",
    )

    d_sibling_name = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Name", "class": "form-control"}
        ),
        label="",
    )
    d_sibling_DOB = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"class": "date-input", "type": "date", "value": "yyyy-mm-dd"}
        ),
        label="Date of Birth",
    )
    d_sibling_age = forms.IntegerField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Age", "class": "form-control"}
        ),
        label="",
    )
    d_sibling_address = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Address", "class": "form-control"}
        ),
        label="",
    )

    e_sibling_name = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Name", "class": "form-control"}
        ),
        label="",
    )
    e_sibling_DOB = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"class": "date-input", "type": "date", "value": "yyyy-mm-dd"}
        ),
        label="Date of Birth",
    )
    e_sibling_age = forms.IntegerField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Age", "class": "form-control"}
        ),
        label="",
    )
    e_sibling_address = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Address", "class": "form-control"}
        ),
        label="",
    )

    class Meta:
        model = FinancialAssistanceApplication

        exclude = ("user",)


class INBPendingApplicants(forms.ModelForm):
    APPLICANT_STATUS = [
        ("Accepted", "Accepted"),
        ("Failed", "Failed"),
    ]

    tracker = forms.ChoiceField(
        required=True,
        choices=APPLICANT_STATUS,
        widget=forms.Select(attrs={}),
        label="Status",
    )

    remarks = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "cols": 40}),
        label="Remarks",
        required=True,
    )

    class Meta:
        model = ApplicantInfoRepositoryINB
        fields = ["tracker", "remarks"]


class FAPendingApplicants(forms.ModelForm):
    APPLICANT_STATUS = [
        ("Accepted", "Accepted"),
        ("Failed", "Failed"),
    ]

    status = forms.ChoiceField(
        required=True,
        choices=APPLICANT_STATUS,
        widget=forms.Select(attrs={}),
        label="Status",
    )

    remarks = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "cols": 40}),
        label="Remarks",
        required=True,
    )

    class Meta:
        model = FinancialAssistanceAssesment
        fields = ["status", "remarks"]
