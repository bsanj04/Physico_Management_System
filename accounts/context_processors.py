from .models import ClinicSettings


def clinic_settings(request) -> dict[str, str]:
    """
    Make the saved clinic name available to all templates.
    """

    settings = ClinicSettings.objects.first()

    return {
        "clinic_name": (
            settings.clinic_name
            if settings
            else "Physiotherapy Clinic"
        ),
    }