from django.db import models


class ClinicSettings(models.Model):
    clinic_name = models.CharField(
        max_length=200,
        default="Physiotherapy Clinic",
    )

    def __str__(self) -> str:
        return self.clinic_name