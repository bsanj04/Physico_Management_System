from django import forms

from .models import Patient, Treatment


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "name",
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