from django.urls import path
from . import views

urlpatterns = [
    path("patient/create/", views.patient_create, name="patient_create",) ,
    path("<int:patient_id>/",
        views.patient_info,
        name="patient_info",
        ),
]