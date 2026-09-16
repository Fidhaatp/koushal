from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = "boardreg"

urlpatterns = [
    path("", views.boardreg, name="boardreg"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("success/<int:registration_id>/", views.registration_success, name="registration_success"),
    path("download/<int:registration_id>/", views.download_registration_pdf, name="download_pdf"),
    path("download-appraisal/<int:registration_id>/", views.download_appraisal_form, name="download_appraisal"),
    # API endpoints for cascading dropdowns
    path("api/get-courses/", views.get_courses_by_coursetype, name="api_get_courses"),
    path("api/get-streams/", views.get_streams_by_course, name="api_get_streams"),
    path("api/get-sessions/", views.get_sessions_by_course, name="api_get_sessions"),
    path("api/get-modes/", views.get_modes_by_course, name="api_get_modes"),
    path("api/get-durations/", views.get_durations_by_course, name="api_get_durations"),
    path("api/get-faculty/", views.get_faculty_by_course, name="api_get_faculty"),
    # Debug endpoint
    path("api-test/", views.api_test, name="api_test"),
]    