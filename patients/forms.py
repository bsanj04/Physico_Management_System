from django import forms

from .models import Patient, Treatment, Diagnosis


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "name",
            "number",
            "dob",
            "gender",
            "weight",
            "height",
            "medical_diagnosis",
        ]

        widgets = {
            "dob": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }

class StaffPatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "name",
            "number",
            "dob",
            "gender",
            "weight",
            "height",
        ]

        widgets = {
            "dob": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }


class TreatmentForm(forms.ModelForm):
    class Meta:
        model = Treatment
        fields = [
            "treatment",
        ]

        widgets = {
            "treatment": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Enter treatment details or clinical notes...",
                }
            ),
        }


class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = Diagnosis
        fields = [
            "diagnosis",
        ]

        widgets = {
            "diagnosis": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Enter diagnosis...",
                }
            ),
        }