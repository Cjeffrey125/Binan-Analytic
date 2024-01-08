from django.db import models
from django.utils import timezone

class CollegeStudentApplication(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    control_number = models.CharField(unique=True, max_length=50)

    requirement = models.CharField(max_length=50, default="Incomplete")
    school_year = models.CharField(max_length=50, default="1st Year")
    # personal data
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, default="")

    blkstr = models.CharField(max_length=100, default="")
    barangay = models.CharField(max_length=100, default="Unknown")
    province = models.CharField(max_length=100, default="Unknown")
    city = models.CharField(max_length=100, default="Unknown")

    gender = models.CharField(max_length=50)
    date_of_birth = models.DateField(default="01-01-2001")
    place_of_birth = models.CharField(max_length=100, default="")
    contact_no = models.CharField(max_length=25, default="")

    email_address = models.EmailField(max_length=100, default="")
    school = models.CharField(max_length=100, default="")

    course = models.CharField(max_length=100, default="")
    gwa = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    rank = models.IntegerField(default=0)

    jhs = models.CharField(max_length=100, default="")
    jhs_address = models.CharField(max_length=100, default="")
    jhs_educational_provider = models.CharField(max_length=100, default="")

    shs = models.CharField(max_length=100, default="")
    shs_address = models.CharField(max_length=100, default="")
    shs_educational_provider = models.CharField(max_length=100, default="")

    # family data
    father_voter_status = models.CharField(max_length=100, default="Not Registered")
    father_name = models.CharField(max_length=100, default="")
    father_educational_attainment = models.CharField(max_length=100, default="")
    father_occupation = models.CharField(max_length=100, default="")
    father_employer = models.CharField(max_length=100, default="")

    mother_voter_status = models.CharField(max_length=100, default="Not Registered")
    mother_name = models.CharField(max_length=100, default="")
    mother_educational_attainment = models.CharField(max_length=100, default="")
    mother_occupation = models.CharField(max_length=100, default="")
    mother_employer = models.CharField(max_length=100, default="")

    guardian_voter_status = models.CharField(max_length=100, default="Not Registered")
    guardian_name = models.CharField(max_length=100, default="")
    guardian_educational_attainment = models.CharField(max_length=100, default="")
    guardian_occupation = models.CharField(max_length=100, default="")
    guardian_employer = models.CharField(max_length=100, default="")

    def __str__(self):
        return f"{self.last_name}, {self.first_name} {self.middle_name}"

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)

        if created:
            requirements = INBRequirementRepository.objects.all()
            for requirement in requirements:
                INBApplicationRequirements.objects.create(
                    applicant=self, requirement=requirement
                )


class INBRequirementRepository(models.Model):
    id = models.AutoField(primary_key=True)
    requirement = models.CharField(max_length=500, default="")

    def __str__(self):
        return f"{self.requirement}"


class INBApplicationRequirements(models.Model):
    applicant = models.ForeignKey(CollegeStudentApplication, on_delete=models.CASCADE)
    requirement = models.ForeignKey(INBRequirementRepository, on_delete=models.CASCADE)
    is_met = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.applicant.control_number} - {self.requirement.requirement} - {'Met' if self.is_met else 'Not Met'}"


class CollegeStudentAccepted(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    status =  models.CharField(max_length=100, default="Ongoing")
    control_number = models.CharField(primary_key=True, max_length=50)
    fullname = models.CharField(max_length=50)
    school_year = models.CharField(max_length=50, default="1st Year")
    course = models.CharField(max_length=50, default="")
    school = models.CharField(max_length=150, default="")
    gender = models.CharField(max_length=50, default="")
    barangay = models.CharField(max_length=100, default="Unknown")
    grant = models.CharField(max_length=500, default="100%")
    remarks = models.CharField(max_length=500, default="")
    


class CollegeStudentAssesment(models.Model):
    control_number = models.CharField(primary_key=True, max_length=50)
    fullname = models.CharField(max_length=50)
    course = models.CharField(max_length=100, default="")
    school = models.CharField(max_length=200, default="")
    remarks = models.CharField(max_length=200, default="")
    status = models.CharField(max_length=200, default="Pending")


class CollegeStudentRejected(models.Model):
    control_number = models.CharField(primary_key=True, max_length=50)
    fullname = models.CharField(max_length=50)
    remarks = models.CharField(max_length=200, default="")


class ApplicantInfoRepositoryINB(models.Model):
    control_number = models.CharField(unique=True, max_length=50)
    status = models.CharField(max_length=20, choices=(("Accepted", "Accepted"), ("Rejected", "Rejected")))

    fullname = models.CharField(max_length=250, default="")

    school_year = models.CharField(max_length=50, default="1st Year")

    blkstr = models.CharField(max_length=100, default="")
    barangay = models.CharField(max_length=100, default="Unknown")
    province = models.CharField(max_length=100, default="Unknown")
    city = models.CharField(max_length=100, default="Unknown")

    gender = models.CharField(max_length=50)
    date_of_birth = models.DateField(default="2001-01-01")
    place_of_birth = models.CharField(max_length=100, default="")
    contact_no = models.CharField(max_length=25, default="")

    email_address = models.EmailField(max_length=100, default="")
    school = models.CharField(max_length=150, default="")

    course = models.CharField(max_length=100, default="")
    gwa = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    rank = models.IntegerField(default=0)

    jhs = models.CharField(max_length=100, default="")
    jhs_address = models.CharField(max_length=100, default="")
    jhs_educational_provider = models.CharField(max_length=100, default="")

    shs = models.CharField(max_length=100, default="")
    shs_address = models.CharField(max_length=100, default="")
    shs_educational_provider = models.CharField(max_length=100, default="")

    # family data
    father_voter_status = models.CharField(max_length=100, default="")
    father_name = models.CharField(max_length=100, default="")
    father_educational_attainment = models.CharField(max_length=100, default="")
    father_occupation = models.CharField(max_length=100, default="")
    father_employer = models.CharField(max_length=100, default="")

    mother_voter_status = models.CharField(max_length=100, default="")
    mother_name = models.CharField(max_length=100, default="")
    mother_educational_attainment = models.CharField(max_length=100, default="")
    mother_occupation = models.CharField(max_length=100, default="")
    mother_employer = models.CharField(max_length=100, default="")

    guardian_voter_status = models.CharField(max_length=100, default="")
    guardian_name = models.CharField(max_length=100, default="")
    guardian_educational_attainment = models.CharField(max_length=100, default="")
    guardian_occupation = models.CharField(max_length=100, default="")
    guardian_employer = models.CharField(max_length=100, default="")

    def __str__(self):
        return self.fullname


# ----------------------------------------------------------------------------------------------------------------------------
class FinancialAssistanceApplication(models.Model):
    control_number = models.CharField(unique=True, max_length=50)

    requirement = models.CharField(max_length=50, default="Incomplete")

    # personal data
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, default="")
    suffix = models.CharField(max_length=50, default="")

    date_of_birth = models.DateField(default="01-01-2001")
    place_of_birth = models.CharField(max_length=100, default="")
    gender = models.CharField(max_length=50)
    religion = models.CharField(max_length=100, default="")

    blkstr = models.CharField(max_length=100, default="")
    barangay = models.CharField(max_length=100, default="Unknown")
    province = models.CharField(max_length=100, default="Unknown")
    city = models.CharField(max_length=100, default="Unknown")

    email_address = models.EmailField(max_length=100, default="")
    contact_no = models.CharField(max_length=25, default="")
    general_average = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    school = models.CharField(max_length=100, default="")
    school_address = models.CharField(max_length=100, default="")

    track = models.CharField(max_length=100, default="")
    strand = models.CharField(max_length=100, default="")

    # family data
    father_name = models.CharField(max_length=100, default="")
    father_age = models.SmallIntegerField(default="")
    father_occupation = models.CharField(max_length=100, default="")
    father_employer = models.CharField(max_length=100, default="")
    father_income = models.IntegerField(default="")

    mother_name = models.CharField(max_length=100, default="")
    mother_age = models.SmallIntegerField(default="")
    mother_occupation = models.CharField(max_length=100, default="")
    mother_employer = models.CharField(max_length=100, default="")
    mother_income = models.IntegerField(default="")

    sibling_count = models.SmallIntegerField(default="")

    a_sibling_name = models.CharField(max_length=100, default="")
    a_sibling_DOB = models.DateField(default="00-00-0000")
    a_sibling_age = models.SmallIntegerField(default=0)
    a_sibling_address = models.CharField(max_length=100, default="")

    b_sibling_name = models.CharField(max_length=100, default="")
    b_sibling_DOB = models.DateField(default="00-00-0000")
    b_sibling_age = models.SmallIntegerField(default=0)
    b_sibling_address = models.CharField(max_length=100, default="")

    c_sibling_name = models.CharField(max_length=100, default="")
    c_sibling_DOB = models.DateField(default="00-00-0000")
    c_sibling_age = models.SmallIntegerField(default=0)
    c_sibling_address = models.CharField(max_length=100, default="")

    d_sibling_name = models.CharField(max_length=100, default="")
    d_sibling_DOB = models.DateField(default="00-00-0000")
    d_sibling_age = models.SmallIntegerField(default=0)
    d_sibling_address = models.CharField(max_length=100, default="")

    e_sibling_name = models.CharField(max_length=100, default="")
    e_sibling_DOB = models.DateField(default="00-00-0000")
    e_sibling_age = models.SmallIntegerField(default=0)
    e_sibling_address = models.CharField(max_length=100, default="")

    def __str__(self):
        return f"{self.last_name}, {self.first_name} {self.middle_name}"

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)

        if created:
            requirements = FARequirementRepository.objects.all()
            for requirement in requirements:
                FAApplicationRequirements.objects.create(
                    applicant=self, requirement=requirement
                )


class FARequirementRepository(models.Model):
    id = models.AutoField(primary_key=True)
    requirement = models.CharField(max_length=500, default="")

    def __str__(self):
        return f"{self.requirement}"


class FAApplicationRequirements(models.Model):
    applicant = models.ForeignKey(
        FinancialAssistanceApplication, on_delete=models.CASCADE
    )
    requirement = models.ForeignKey(FARequirementRepository, on_delete=models.CASCADE)
    is_met = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.applicant.control_number} - {self.requirement.requirement} - {'Met' if self.is_met else 'Not Met'}"


class FinancialAssistanceAccepted(models.Model):
    control_number = models.CharField(primary_key=True, max_length=50)
    fullname = models.CharField(max_length=50)
    school_year = models.CharField(max_length=50, default="1st Years")
    strand = models.CharField(max_length=50, default="")
    school = models.CharField(max_length=50, default="")


class FinancialAssistanceRejected(models.Model):
    control_number = models.CharField(primary_key=True, max_length=50)
    fullname = models.CharField(max_length=50)
    remarks = models.CharField(max_length=200, default="")


class FinancialAssistanceAssesment(models.Model):
    control_number = models.CharField(primary_key=True, max_length=50)
    fullname = models.CharField(max_length=50)
    school_year = models.CharField(max_length=50, default="1st Years")
    strand = models.CharField(max_length=50, default="")
    school = models.CharField(max_length=50, default="")


class FinancialAssistanceInfoRepository(models.Model):
    control_number = models.CharField(unique=True, max_length=50)
    status = models.CharField(
        max_length=20, choices=(("Accepted", "Accepted"), ("Rejected", "Rejected"))
    )

    fullname = models.CharField(max_length=250, default="")

    date_of_birth = models.DateField(default="01-01-2001")
    place_of_birth = models.CharField(max_length=100, default="")
    gender = models.CharField(max_length=50)
    religion = models.CharField(max_length=100, default="")

    blkstr = models.CharField(max_length=100, default="")
    barangay = models.CharField(max_length=100, default="Unknown")
    province = models.CharField(max_length=100, default="Unknown")
    city = models.CharField(max_length=100, default="Unknown")

    email_address = models.EmailField(max_length=100, default="")
    contact_no = models.CharField(max_length=25, default="")
    general_average = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    school = models.CharField(max_length=100, default="")
    school_address = models.CharField(max_length=100, default="")

    track = models.CharField(max_length=100, default="")
    strand = models.CharField(max_length=100, default="")

    # family data
    father_name = models.CharField(max_length=100, default="")
    father_age = models.SmallIntegerField(default="")
    father_occupation = models.CharField(max_length=100, default="")
    father_employer = models.CharField(max_length=100, default="")
    father_income = models.IntegerField(default="")

    mother_name = models.CharField(max_length=100, default="")
    mother_age = models.SmallIntegerField(default="")
    mother_occupation = models.CharField(max_length=100, default="")
    mother_employer = models.CharField(max_length=100, default="")
    mother_income = models.IntegerField(default="")

    sibling_count = models.SmallIntegerField(default="")

    a_sibling_name = models.CharField(max_length=100, default="")
    a_sibling_DOB = models.DateField(default="01-01-2001")
    a_sibling_age = models.SmallIntegerField(default=0)
    a_sibling_address = models.CharField(max_length=100, default="")

    b_sibling_name = models.CharField(max_length=100, default="")
    b_sibling_DOB = models.DateField(default="01-01-2001")
    b_sibling_age = models.SmallIntegerField(default=0)
    b_sibling_address = models.CharField(max_length=100, default="")

    c_sibling_name = models.CharField(max_length=100, default="")
    c_sibling_DOB = models.DateField(default="01-01-2001")
    c_sibling_age = models.SmallIntegerField(default=0)
    c_sibling_address = models.CharField(max_length=100, default="")

    d_sibling_name = models.CharField(max_length=100, default="")
    d_sibling_DOB = models.DateField(default="01-01-2001")
    d_sibling_age = models.SmallIntegerField(default=0)
    d_sibling_address = models.CharField(max_length=100, default="")

    e_sibling_name = models.CharField(max_length=100, default="")
    e_sibling_DOB = models.DateField(default="01-01-2001")
    e_sibling_age = models.SmallIntegerField(default=0)
    e_sibling_address = models.CharField(max_length=100, default="")

    def __str__(self):
        return self.fullname


# ---------------------------------------------------------------
# admin
class ApplicantTracker(models.Model):
    year = models.IntegerField(default=0)
    admitted_applicants = models.IntegerField(default=0)
    applied_applicants = models.IntegerField(default=0)
    
class INBScholars(models.Model):
    year = models.IntegerField(default=0)
    total_applicants = models.IntegerField(default=0)
    total_accepted_applicants = models.IntegerField(default=0)
    total_failed_applicants = models.IntegerField(default=0)
    total_rejected_applicants = models.IntegerField(default=0)

class INBSchool(models.Model):
    school = models.CharField(max_length=100)

    def __str__(self):
        return self.school

    def delete(self, *args, **kwargs):
        INBCourse.objects.filter(school_id=self.id).delete()
        super().delete(*args, **kwargs)


class INBCourse(models.Model):
    course = models.CharField(max_length=100)
    acronym = models.CharField(max_length=100, default="")
    school = models.ManyToManyField(INBSchool)
    school_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.course


class StudentGrade(models.Model):
    student = models.ForeignKey(
        CollegeStudentAccepted, on_delete=models.CASCADE, related_name="grades"
    )
    subject = models.CharField(max_length=255)
    grade = models.CharField(max_length=255)


class Subject(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)
