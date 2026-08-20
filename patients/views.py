from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from accounts.decorators import (
    doctor_required,
    user_is_doctor,
    user_is_staff_member,
)

from .models import Patient, Diagnosis
from accounts.models import ClinicSettings
from .forms import PatientForm, TreatmentForm, StaffPatientForm, DiagnosisForm



def patient_create(
    request: HttpRequest,
) -> HttpResponse:

    is_doctor = user_is_doctor(request.user)
    is_staff = user_is_staff_member(request.user)

    if not is_doctor and not is_staff:
        return redirect("dashboard")

    if request.method == "POST":
        if is_doctor:
            patient_form = PatientForm(request.POST)
        else:
            patient_form = StaffPatientForm(request.POST)

        if is_doctor:
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
            treatment_form = None

            if patient_form.is_valid():
                patient = patient_form.save(commit=False)
                patient.created_by = request.user
                patient.save()

                return redirect("dashboard")

    else:
        if is_doctor:
            patient_form = PatientForm()
        else:
            patient_form = StaffPatientForm()

        if is_doctor:
            treatment_form = TreatmentForm()
        else:
            treatment_form = None

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


@doctor_required
def diagnosis_create(request: HttpRequest, patient_id: int) -> HttpResponse:
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == "POST":
        form = DiagnosisForm(request.POST)

        if form.is_valid():
            diagnosis = form.save(commit=False)

            diagnosis.patient = patient
            diagnosis.created_by = request.user

            diagnosis.save()

            return redirect("patient_info", patient_id=patient.id)

    return redirect("patient_info", patient_id=patient.id)