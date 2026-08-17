from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from accounts.decorators import doctor_required

from .forms import PatientForm
from .models import Patient

@doctor_required
def patient_create(
    request: HttpRequest,
) -> HttpResponse:
    if request.method == "POST":
        form = PatientForm(request.POST)

        if form.is_valid():
            patient = form.save(commit=False)
            patient.created_by = request.user
            patient.save()
            return redirect("dashboard")
    else:
        form = PatientForm()

    return render(
        request,
        "patients/patient_form.html",
        {
            "form": form,
            "page_title": "Create Patient",
            "submit_label": "Create Patient",
        },
    )

def patient_info(
        request: HttpRequest,
        patient_id: int,
    )-> HttpResponse:
        patient = get_object_or_404(
            Patient,
            id=patient_id,
    )

        return render(
            request,
            "patients/patient_info.html",
            {
                "patient": patient,
            },
        )
