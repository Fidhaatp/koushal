# models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from tinymce.models import HTMLField


class Faculty(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Faculty Name")

    class Meta:
        verbose_name = "Faculty"
        verbose_name_plural = "Faculties"

    def __str__(self):
        return self.name


class CourseType(models.Model):
    name = models.CharField(max_length=50, verbose_name="Course Type")

    class Meta:
        verbose_name = "Course Type"
        verbose_name_plural = "Course Types"

    def __str__(self):
        return self.name


# ✅ FIXED COURSE MODEL
class Course(models.Model):
    course_type = models.ForeignKey(
        CourseType,
        on_delete=models.CASCADE,
        verbose_name="Course Type"
    )
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, verbose_name="Faculty", null=True, blank=True)
    name = models.CharField(max_length=255, verbose_name="Course Name")
    application_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00, blank=True, null=True, verbose_name="Application Fee")
    duration = models.CharField(max_length=50, default="3 Years", verbose_name="Duration")
    description = models.TextField(blank=True, verbose_name="Course Description")
    pargraph = HTMLField()

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return self.name


class Duration(models.Model):
    name = models.CharField(max_length=255, verbose_name="Duration Name")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_durations")

    class Meta:
        verbose_name = "Duration"
        verbose_name_plural = "Durations"
        unique_together = ('name', 'course')

    def __str__(self):
        return f"{self.name} ({self.course.name})"


class Session(models.Model):
    name = models.CharField(max_length=255, verbose_name="Session Name")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_sessions")

    class Meta:
        verbose_name = "Session"
        verbose_name_plural = "Sessions"
        unique_together = ('name', 'course')

    def __str__(self):
        return f"{self.name} ({self.course.name})"


class ModeOfStudy(models.Model):
    name = models.CharField(max_length=255, verbose_name="Mode of Study Name")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_modes")

    class Meta:
        verbose_name = "Mode of Study"
        verbose_name_plural = "Modes of Study"
        unique_together = ('name', 'course')

    def __str__(self):
        return f"{self.name} ({self.course.name})"


class Stream(models.Model):
    name = models.CharField(max_length=255, verbose_name="Stream Name")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Stream"
        verbose_name_plural = "Streams"
        unique_together = ('name', 'course')

    def __str__(self):
        return f"{self.name} ({self.course.name})"


class Branch(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Branch Name")

    class Meta:
        verbose_name = "Branch"
        verbose_name_plural = "Branches"

    def __str__(self):
        return self.name    
        

class BoardRegistration(models.Model):
    # Personal Details
    candidate_name = models.CharField(max_length=255, verbose_name="Candidate Name")
    father_name = models.CharField(max_length=255, verbose_name="Father's Name")
    mother_name = models.CharField(max_length=255, verbose_name="Mother's Name")
    date_of_birth = models.DateField(verbose_name="Date of Birth")
    photo = models.ImageField(upload_to='photos/', verbose_name="Photo")
        # Admission identifiers
    register_no = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Register No")
    internship_id = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Internship ID")
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], verbose_name="Gender")
    category = models.CharField(max_length=10, choices=[('general', 'General'), ('obc', 'OBC'), ('sc', 'SC'), ('st', 'ST'), ('ews', 'EWS')], verbose_name="Category")
    id_proof_type = models.CharField(max_length=20, choices=[('aadhaar', 'Aadhaar Card'), ('pan', 'PAN Card'), ('passport', 'Passport'), ('voter', 'Voter ID')], verbose_name="ID Proof Type")
    id_proof_no = models.CharField(max_length=50, verbose_name="ID Proof Number")
    aadhaar_front = models.FileField(upload_to='id_proofs/', verbose_name="Aadhaar Card Front")
    aadhaar_back = models.FileField(upload_to='id_proofs/', verbose_name="Aadhaar Card Back")
    employed = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], verbose_name="Are You Currently Employed?")
    hostel_facility = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], verbose_name="Hostel Facility Required?")

    # Communication Details
    contact_number = models.CharField(max_length=15, verbose_name="Contact Number")
    email = models.EmailField(verbose_name="Email Address")
    father_contact = models.CharField(max_length=15, blank=True, verbose_name="Father's Contact Number")
    mother_contact = models.CharField(max_length=15, blank=True, verbose_name="Mother's Contact Number")
    # Address Information 
    country = models.CharField(max_length=100, verbose_name="Country")
    nationality = models.CharField(max_length=100, verbose_name="Nationality")
    House_Building_Name_or_Number = models.TextField(verbose_name="House/Building Name or Number")
    Street_Name = models.TextField(verbose_name="Street / Area Name /Locality Name")
    post_office_name = models.TextField(verbose_name="Post Office Name")
    village_town_city = models.CharField(max_length=100, verbose_name="Village / Town / City")
    district = models.CharField(max_length=100, verbose_name="District")
    State = models.CharField(max_length=100, verbose_name="State")
    pincode = models.PositiveIntegerField(verbose_name="Pincode")

 
    # Previous Qualification Details
    # Secondary (MANDATORY) – keep as it is
    secondary_board = models.CharField(max_length=255)
    secondary_year = models.PositiveSmallIntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2025)])
    secondary_percentage = models.CharField(max_length=10)
    secondary_doc = models.FileField(upload_to='qualifications/')


    # Sr Secondary (OPTIONAL)
    srsecondary_board = models.CharField(max_length=255, blank=True, null=True)
    srsecondary_year = models.PositiveSmallIntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2025)],blank=True,null=True)
    srsecondary_percentage = models.CharField(max_length=10, blank=True, null=True)
    srsecondary_doc = models.FileField(upload_to='qualifications/', blank=True, null=True)


    # Graduation (OPTIONAL)
    graduation_board = models.CharField(max_length=255, blank=True, null=True)
    graduation_year = models.PositiveSmallIntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2025)],blank=True,null=True)
    graduation_percentage = models.CharField(max_length=10, blank=True, null=True)
    graduation_doc = models.FileField(upload_to='qualifications/', blank=True, null=True)


    # Post Graduation (OPTIONAL)
    postgraduation_board = models.CharField(max_length=255, blank=True, null=True)
    postgraduation_year = models.PositiveSmallIntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2025)],blank=True,null=True)
    postgraduation_percentage = models.CharField(max_length=10, blank=True, null=True)
    postgraduation_doc = models.FileField(upload_to='qualifications/', blank=True, null=True)


    # Other (OPTIONAL)
    other_board = models.CharField(max_length=255, blank=True, null=True)
    other_year = models.PositiveSmallIntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2025)],blank=True,null=True)
    other_percentage = models.CharField(max_length=10, blank=True, null=True)
    other_doc = models.FileField(upload_to='qualifications/', blank=True, null=True)


    # Programme Details
    date_of_join = models.DateField(verbose_name="Date of Join")
    course_type     = models.ForeignKey(CourseType, on_delete=models.CASCADE)
    course          = models.ForeignKey(Course, on_delete=models.CASCADE)
    stream          = models.ForeignKey(Stream, on_delete=models.CASCADE, null=True, blank=True)
    duration        = models.ForeignKey(Duration, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Duration")
    month_session   = models.CharField(max_length=20, choices=[
        ('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'),
        ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'),
        ('september', 'September'), ('october', 'October'), ('november', 'November'), ('december', 'December')
    ], verbose_name="Month/Session")
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, blank=True)
    mode_of_study = models.ForeignKey(ModeOfStudy, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    academic_delivery_end = models.DateField(verbose_name="Academic Delivery End")
    application_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Application Fee")
    

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return f"Reg - {self.candidate_name}"

    @property
    def faculty(self):
        return self.course.faculty if self.course else None

    @property
    def is_data_science(self):
        """True when course is Data Science (appraisal / placement form applies)."""
        name = (self.course.name if self.course else '') or ''
        return 'data science' in name.strip().lower()

