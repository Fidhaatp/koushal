# admin.py (in boardreg app)
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Faculty, CourseType, Course, Stream, Branch, BoardRegistration, Duration, Session, ModeOfStudy

@admin.register(Faculty)
class FacultyAdmin(ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    list_filter = ['name']

@admin.register(CourseType)
class CourseTypeAdmin(ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ['name', 'course_type', 'faculty', 'application_fee', 'duration']
    list_filter = ['course_type', 'faculty']
    search_fields = ['name']

@admin.register(Stream)
class StreamAdmin(ModelAdmin):
    list_display = ['name', 'course']
    list_filter = ['course']
    search_fields = ['name']

@admin.register(Branch)
class BranchAdmin(ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(BoardRegistration)
class BoardRegistrationAdmin(ModelAdmin):
    list_display = ['candidate_name', 'email', 'course_type', 'created_at']
    list_filter = ['course_type',  'gender', 'category', 'created_at']
    search_fields = ['candidate_name', 'email', 'contact_number']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Personal Details', {
            'fields': ('candidate_name', 'father_name', 'mother_name', 'date_of_birth', 'photo', 'gender', 'category', 'employed', 'register_no', 'internship_id', 'hostel_facility')
        }),
        ('ID Proof', {
            'fields': ('id_proof_type', 'id_proof_no', 'aadhaar_front', 'aadhaar_back')
        }),
        ('Communication Details', {
            'fields': ('contact_number', 'email', 'father_contact', 'mother_contact', 'country', 'nationality')
        }),
        ('Address Information', {
            'fields': ('House_Building_Name_or_Number', 'Street_Name', 'post_office_name', 'village_town_city', 'district', 'State', 'pincode')
        }),
        ('Previous Qualifications', {
            'fields': ('secondary_board', 'secondary_year', 'secondary_percentage', 'secondary_doc',
                       'srsecondary_board', 'srsecondary_year', 'srsecondary_percentage', 'srsecondary_doc',
                       'graduation_board', 'graduation_year', 'graduation_percentage', 'graduation_doc',
                       'postgraduation_board', 'postgraduation_year', 'postgraduation_percentage', 'postgraduation_doc',
                       'other_board', 'other_year', 'other_percentage', 'other_doc')
        }),
        ('Programme Details', {
            'fields': ('date_of_join', 'academic_delivery_end', 'course_type', 'course', 'stream', 'branch', 'month_session', 'session', 'mode_of_study', 'application_fee', 'duration')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Duration)
class DurationAdmin(ModelAdmin):
    list_display = ['name', 'course']
    list_filter = ['course']
    search_fields = ['name']

@admin.register(Session)
class SessionAdmin(ModelAdmin):
    list_display = ['name', 'course']
    list_filter = ['course']
    search_fields = ['name']


@admin.register(ModeOfStudy)
class ModeOfStudyAdmin(ModelAdmin):
    list_display = ['name', 'course']
    list_filter = ['course']
    search_fields = ['name']