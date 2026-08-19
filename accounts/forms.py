from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from .models import ClinicSettings

User = get_user_model()


class UserCreateForm(UserCreationForm):
    ROLE_CHOICES = (
        ("Doctor", "Doctor"),
        ("Staff", "Staff"),
        ("Admin", "Admin"),
    )

    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    email = forms.EmailField(
        required=True,
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "password1",
            "password2",
        )

    def clean_username(self) -> str:
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                "A user with this username already exists."
            )

        return username
    
    def clean_email(self) -> str:
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "A user with this email address already exists."
            )

        return email

    def save(self, commit: bool = True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data["first_name"].strip()
        user.last_name = self.cleaned_data["last_name"].strip()
        user.email = self.cleaned_data["email"].strip()

        # Never grant Django admin privileges through this form.
        user.is_staff = False
        user.is_superuser = False
        user.is_active = True

        if commit:
            user.save()

            role = Group.objects.get(
                name=self.cleaned_data["role"]
            )

            user.groups.set([role])

        return user


class UserEditForm(forms.ModelForm):
    ROLE_CHOICES = (
        ("Doctor", "Doctor"),
        ("Staff", "Staff"),
        ("Admin", "Admin"),
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
        )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            current_group = self.instance.groups.filter(
                name__in=["Admin", "Doctor", "Staff"]
            ).first()

            if current_group:
                self.fields["role"].initial = current_group.name

    def clean_username(self) -> str:
        username = self.cleaned_data["username"].strip()

        duplicate = User.objects.filter(
            username__iexact=username
        ).exclude(pk=self.instance.pk)

        if duplicate.exists():
            raise forms.ValidationError(
                "A user with this username already exists."
            )

        return username

    def save(self, commit: bool = True):
        user = super().save(commit=False)

        # These values must never be enabled by this form.
        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()

            role = Group.objects.get(
                name=self.cleaned_data["role"]
            )

            user.groups.set([role])

        return user
    
class ClinicSettingsForm(forms.ModelForm):
    class Meta:
        model = ClinicSettings
        fields = ("clinic_name",)
        labels = {
            "clinic_name": "Clinic name",
        }
        widgets = {
            "clinic_name": forms.TextInput(
                attrs={
                    "placeholder": "Enter the clinic name",
                    "autocomplete": "organization",
                }
            ),
        }

    def clean_clinic_name(self) -> str:
        clinic_name = self.cleaned_data["clinic_name"].strip()

        if not clinic_name:
            raise forms.ValidationError(
                "Enter the clinic name."
            )

        return clinic_name