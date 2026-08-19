from datetime import date

from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator


class Patient(models.Model):

    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    name = models.CharField(
        max_length=150,
        verbose_name="Patient's Full Name",
    )

    number = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^\d{10}$",
                message="Phone number must contain exactly 10 digits.",
            )
        ],
        verbose_name="Phone No",
        blank=True,
        default="",
    )

    dob = models.DateField(
        verbose_name="Date of Birth",
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        verbose_name="Gender",
    )

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Weight (kg)",
    )

    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Height (cm)",
    )

    medical_diagnosis = models.TextField(
        verbose_name="Diagnosis",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date Added",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="patients_created",
        verbose_name="Added By",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated",
    )

    @property
    def age(self):
        today = date.today()

        age = today.year - self.dob.year

        if (today.month, today.day) < (self.dob.month, self.dob.day):
            age -= 1

        return age

    def __str__(self):
        return self.name


class Treatment(models.Model):

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="treatments",
    )

    treatment = models.TextField(
        verbose_name="Treatment / Notes",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date Added",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="treatments_created",
        verbose_name="Added By",
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.patient.name} - {self.created_at:%d/%m/%Y}"