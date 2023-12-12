from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from base.models import (
    CollegeStudentApplication,
    FinancialAssistanceApplication,
    INBRequirementRepository,
    FARequirementRepository,
    INBSchool,
    INBCourse,
)


class INBSchoolForm(forms.ModelForm):
    school = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Add New Requirements", "class": "form-control"}
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


class FARequirementList(forms.ModelForm):
    class Meta:
        model = FARequirementRepository
        fields = ["requirement"]
        widgets = {
            "requirement": forms.TextInput(
                attrs={"placeholder": "Add New Requirements", "class": "form-control"}
            )
        }


class ApplicantUploadForm(forms.Form):
    file = forms.FileField()

class GradeUploadForm(forms.Form):
    file = forms.FileField(label='Choose Excel file', widget=forms.FileInput(attrs={'accept': '.xlsx'}))

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
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    EDUCATIONAL_PROVIDERS = [
        ("Deped", "DepEd"),
        ("Non-Deped", "Non-DepEd"),
    ]

    VOTER_STATUS = [
        ("Registered Voter", "Registered Voter"),
        ("Not Registered Voter", "Not Registered Voter"),
    ]

    control_number = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Control Number", "class": "control-number-input"}
        ),
        label="",
    )

    # Personal Data
    first_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "name-input", "placeholder":"First name"}),
        label="",
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "name-input", "placeholder":"Last name"}),
        label="",
    )
    middle_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "name-input", "placeholder":"Middle Name"}),
        label="",
    )

    blkstr = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "address-input-1", "placeholder":"Number/Block/Street"}),
        help_text='<span class="subscript">Blk Street</span>',
        label="",
    )
    barangay = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "address-input-2", "placeholder":"Barangay"}),
        help_text='<span class="subscript">Barangay</span>',
        label="",
    )
    province = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "address-input-2", "placeholder":"Province"}),
        help_text='<span class="subscript">Province</span>',
        label="",
    )
    city = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "address-input-2", "placeholder":"City"}),
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
        widget=forms.DateInput(attrs={"class": "date-input", "type": "date", "value": "yyyy-mm-dd"}),
        label="Date of Birth",
    )

    place_of_birth = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"class":"place-birth-input", "placeholder":"Place of Birth"}
        ),
        label="",
    )
    contact_no = forms.IntegerField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"class":"contact-input", "placeholder":"Contact Number"}
        ),
        label="",
    )

    email_address = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"class":"half-input", "placeholder":"Email Address"}
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
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "General Weighted Average", "class": "rank-gwa-input"}
        ),
        label="",
    )
    rank = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Rank", "class": "rank-gwa-input"}
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
        required=True,
        choices=VOTER_STATUS,
        widget=forms.RadioSelect(attrs={"class": "radio-container"}),
        label="",
    )
    father_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Father Name", "class": "prev-school"}
        ),
        label="",
    )
    father_educational_attainment = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Educational Attainment", "class": "prev-school"}
        ),
        label="",
    )
    father_occupation = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Occupation", "class": "prev-school"}
        ),
        label="",
    )
    father_employer = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Name of Employer", "class": "prev-school"}
        ),
        label="",
    )

    mother_voter_status = forms.ChoiceField(
        required=True,
        choices=VOTER_STATUS,
        widget=forms.RadioSelect(attrs={"class": "radio-container"}),
        label="",
    )
    mother_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Mother Name", "class": "prev-school"}
        ),
        label="",
    )
    mother_educational_attainment = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Educational Attainment", "class": "prev-school"}
        ),
        label="",
    )
    mother_occupation = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Occupation", "class": "prev-school"}
        ),
        label="",
    )
    mother_employer = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Name of Employer", "class": "prev-school"}
        ),
        label="",
    )

    guardian_voter_status = forms.ChoiceField(
        required=True,
        choices=VOTER_STATUS,
        widget=forms.RadioSelect(attrs={"class": "radio-container"}),
        label="",
    )
    guardian_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Legal Guardian Name", "class": "prev-school"}
        ),
        label="",
    )
    guardian_educational_attainment = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Educational Attainment", "class": "prev-school"}
        ),
        label="",
    )
    guardian_occupation = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Occupation", "class": "prev-school"}
        ),
        label="",
    )
    guardian_employer = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Name of Employer", "class": "prev-school"}
        ),
        label="",
    )

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
        ("0", "Select Gender"),
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

    # Personal Data
    first_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
        help_text='<span class="subscript">First Name</span>',
        label="",
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
        help_text='<span class="subscript">Surname</span>',
        label="",
    )
    middle_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
        help_text='<span class="subscript">Middle Name</span>',
        label="",
    )
    suffix = forms.CharField(
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
        help_text='<span class="subscript">Suffix</span>',
        label="",
    )

    date_of_birth = forms.DateField(
        required=True,
        widget=forms.SelectDateWidget(attrs={"class": "date-input"}),
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
        widget=forms.Select(attrs={"class": "form-control"}),
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
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
        help_text='<span class="subscript">Blk Street</span>',
        label="",
    )
    barangay = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
        help_text='<span class="subscript">Barangay</span>',
        label="",
    )
    province = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
        help_text='<span class="subscript">Province</span>',
        label="",
    )
    city = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
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
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "No. of Siblings", "class": "form-control"}
        ),
        label="",
    )

    sibling_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
        help_text='<span class="subscript">Name</span>',
        label="",
    )
    sibling_DOB = forms.DateField(
        required=True,
        widget=forms.SelectDateWidget(attrs={"class": "form-control"}),
        help_text='<span class="subscript">Date of Birth</span>',
        label="Date of Birth",
    )
    sibling_age = forms.IntegerField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Age", "class": "form-control"}
        ),
        label="",
    )
    sibling_address = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
        help_text='<span class="subscript">Address</span>',
        label="",
    )

    class Meta:
        model = FinancialAssistanceApplication

        exclude = ("user",)


