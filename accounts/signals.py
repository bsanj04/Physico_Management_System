from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_default_groups(sender, **kwargs) -> None:
    """
    ensure the required application roles exist after migrations.
    """

    if sender.name != "accounts":
        return

    Group.objects.get_or_create(name="Doctor")
    Group.objects.get_or_create(name="Staff")
    Group.objects.get_or_create(name="Admin")