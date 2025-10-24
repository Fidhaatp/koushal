from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = "boardreg"

urlpatterns = [
    path("", views.boardreg, name="boardreg"),
]    