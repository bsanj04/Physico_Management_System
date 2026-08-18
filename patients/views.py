from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from accounts.decorators import doctor_required

from .models import Patient
from accounts.models import ClinicSettings
from .forms import PatientForm, TreatmentForm


@doctor_required
def patient_create(
    request: HttpRequest,
) -> HttpResponse:

    if request.method == "POST":
        patient_form = PatientForm(request.POST)
        treatment_form = TreatmentForm(request.POST)

        if patient_form.is_valid() and treatment_form.is_valid():
            patient = patient_form.save(commit=False)
            patient.created_by = request.user
            patient.save()

            treatment = treatment_form.save(commit=False)
            treatment.patient = patient
            treatment.created_by = request.user
            treatment.save()

            return redirect("dashboard")

    else:
        patient_form = PatientForm()
        treatment_form = TreatmentForm()

    return render(
        request,
        "patients/patient_form.html",
        {
            "patient_form": patient_form,
            "treatment_form": treatment_form,
            "page_title": "Create Patient",
            "submit_label": "Create Patient",
        },
    )

def patient_info(request, patient_id):

    patient = get_object_or_404(
        Patient,
        id=patient_id,
    )

    is_doctor = request.user.groups.filter(
        name="Doctor"
    ).exists()

    return render(
        request,
        "patients/patient_info.html",
        {
            "patient": patient,
            "is_doctor": is_doctor,
        },
    )

def dashboard(request):

    clinic_settings = ClinicSettings.objects.first()

    return render(
        request,
        "dashboard.html",
        {
            "clinic_name": (
                clinic_settings.clinic_name
                if clinic_settings
                else "Physiotherapy Clinic"
            ),
        },
    )

@doctor_required
def treatment_create(request: HttpRequest, patient_id: int) -> HttpResponse:
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == "POST":
        form = TreatmentForm(request.POST)

        if form.is_valid():
            treatment = form.save(commit=False)

            treatment.patient = patient
            treatment.created_by = request.user

            treatment.save()

            return redirect("patient_info", patient_id=patient.id)

    return redirect("patient_info", patient_id=patient.id)