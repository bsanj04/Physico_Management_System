from collections.abc import Callable
from functools import wraps
from typing import Any

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse


def user_is_admin(user: Any) -> bool:
    return bool(
        user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(name="Admin").exists()
        )
    )


def user_is_doctor(user: Any) -> bool:
    return bool(
        user.is_authenticated
        and user.groups.filter(name="Doctor").exists()
    )


def user_is_staff_member(user: Any) -> bool:
    return bool(
        user.is_authenticated
        and user.groups.filter(name="Staff").exists()
    )


def admin_required(
    view_function: Callable[..., HttpResponse],
) -> Callable[..., HttpResponse]:
    @login_required
    @wraps(view_function)
    def wrapped_view(
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        if not user_is_admin(request.user):
            raise PermissionDenied

        return view_function(request, *args, **kwargs)

    return wrapped_view

def doctor_required(
    view_function: Callable[..., HttpResponse],
) -> Callable[..., HttpResponse]:
    @login_required
    @wraps(view_function)
    def wrapped_view(
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        if not user_is_doctor(request.user):
            raise PermissionDenied

        return view_function(request, *args, **kwargs)

    return wrapped_view
