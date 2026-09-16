# forms.py
from django import forms
from .models import BoardRegistration, CourseType, Faculty, Course, Stream, Branch, Duration, Session, ModeOfStudy

class BoardRegistrationForm(forms.ModelForm):
    class Meta:
        model = BoardRegistration
        fields = '__all__'
        exclude = ['created_at']
        widgets = {
            'candidate_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter candidate name', 'required': True}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter father's name", 'required': True}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter mother's name", 'required': True}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'required': True}),
            'gender': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'category': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'id_proof_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'id_proof_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ID proof number', 'required': True}),
            'register_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter registration number', 'required': True}),
            'internship_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter internship ID', 'required': True}),
            'aadhaar_front': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'required': True}),
            'aadhaar_back': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'required': True}),
            'employed': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel', 'placeholder': 'Enter your contact number', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address', 'required': True}),
            'father_contact': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel', 'placeholder': "Enter father's contact number"}),
            'mother_contact': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel', 'placeholder': "Enter mother's contact number"}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter country', 'required': True}),
            'nationality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter nationality', 'required': True}),
            'House_Building_Name_or_Number': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'House/Building Name or Number', 'required': True}),
            'Street_Name': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Street / Area / Locality Name', 'required': True}),
            'post_office_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post Office Name', 'required': True}),
            'village_town_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Village / Town / City', 'required': True}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'District', 'required': True}),
            'State': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State', 'required': True}),
            'pincode': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter pincode', 'required': True}),
            'secondary_board': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Board/University', 'required': True}),
            'secondary_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year', 'min': 1900, 'max': 2025, 'required': True}),
            'secondary_percentage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Percentage/CGPA', 'required': True}),
            'secondary_doc': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,image/*', 'required': True}),
            'srsecondary_board': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Board/University'}),
            'srsecondary_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year', 'min': 1900, 'max': 2025}),
            'srsecondary_percentage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Percentage/CGPA'}),
            'srsecondary_doc': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,image/*'}),
            
            
            # Graduation (OPTIONAL ❌ remove required)
            'graduation_board': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'University'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year', 'min': 1900, 'max': 2025}),
            'graduation_percentage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Percentage/CGPA'}),
            'graduation_doc': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,image/*'}),
            'postgraduation_board': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'University'}),
            'postgraduation_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year', 'min': 1900, 'max': 2025}),
            'postgraduation_percentage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Percentage/CGPA'}),
            'postgraduation_doc': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,image/*'}),
            'other_board': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Board/University'}),
            'other_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year', 'min': 1900, 'max': 2025}),
            'other_percentage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Percentage/CGPA'}),
            'other_doc': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,image/*'}),
            'course_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'course':      forms.Select(attrs={'class': 'form-control', 'required': True}),
            'stream':      forms.Select(attrs={'class': 'form-control', 'required': False}),
            'branch':      forms.Select(attrs={'class': 'form-control', 'required': False}),
            'faculty_display': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True,
                'placeholder': 'Will be auto-filled from selected course'
            }),
            'date_of_join': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'academic_delivery_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'month_session': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'session': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'mode_of_study': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'hostel_facility': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'application_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Auto-filled from course', 'readonly': True, 'step': '0.01'}),
            'duration': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select duration'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['register_no'].required = True
        self.fields['internship_id'].required = True
        self.fields['course_type'].queryset = CourseType.objects.all()
        self.fields['course'].queryset = Course.objects.none()
        self.fields['stream'].queryset = Stream.objects.none()
        self.fields['branch'].queryset = Branch.objects.all().order_by('name')
        self.fields['session'].queryset = Session.objects.none()
        self.fields['mode_of_study'].queryset = ModeOfStudy.objects.none()
        self.fields['duration'].queryset = Duration.objects.none()

        # Editing existing record
        if self.instance.pk:
            if self.instance.course_type_id:
                self.fields['course'].queryset = Course.objects.filter(
                    course_type_id=self.instance.course_type_id
                )
            if self.instance.course_id:
                self.fields['stream'].queryset = Stream.objects.filter(
                    course_id=self.instance.course_id
                )
                self.fields['session'].queryset = Session.objects.filter(
                    course_id=self.instance.course_id
                )
                self.fields['mode_of_study'].queryset = ModeOfStudy.objects.filter(
                    course_id=self.instance.course_id
                )
                self.fields['duration'].queryset = Duration.objects.filter(
                    course_id=self.instance.course_id
                )
                # Auto-populate faculty_display from course
                if self.instance.course.faculty:
                    self.initial['faculty_display'] = self.instance.course.faculty

        # Populate from POST data (validation phase)
        if 'course_type' in self.data:
            try:
                ct_id = int(self.data.get('course_type'))
                self.fields['course'].queryset = Course.objects.filter(course_type_id=ct_id)
            except (ValueError, TypeError):
                pass

        if 'course' in self.data:
            try:
                c_id = int(self.data.get('course'))
                self.fields['stream'].queryset = Stream.objects.filter(course_id=c_id)
                self.fields['session'].queryset = Session.objects.filter(course_id=c_id)
                self.fields['mode_of_study'].queryset = ModeOfStudy.objects.filter(course_id=c_id)
                self.fields['duration'].queryset = Duration.objects.filter(course_id=c_id)

                # Auto-populate faculty_display from selected course
                course = Course.objects.filter(id=c_id).first()
                if course and course.faculty:
                    self.initial['faculty_display'] = course.faculty
            except (ValueError, TypeError):
                pass

    def clean_register_no(self):
        register_no = self.cleaned_data.get('register_no')
        if not register_no:
            return register_no
        qs = BoardRegistration.objects.filter(register_no__iexact=register_no.strip())
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('This Register No is already registered.')
        return register_no.strip()

    def clean_internship_id(self):
        internship_id = self.cleaned_data.get('internship_id')
        if not internship_id:
            return internship_id
        qs = BoardRegistration.objects.filter(internship_id__iexact=internship_id.strip())
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('This Internship ID is already registered.')
        return internship_id.strip()

    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        if course:
            cleaned_data['application_fee'] = course.application_fee
        return cleaned_data

