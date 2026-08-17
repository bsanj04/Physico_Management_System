from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
)

from .decorators import (
    admin_required,
    user_is_admin,
    user_is_doctor,
    user_is_staff_member,
)
from .forms import (
    ClinicSettingsForm,
    UserCreateForm,
    UserEditForm,
)
from .models import ClinicSettings
from patients.models import Patient


User = get_user_model()


@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    """
    Authenticate users and redirect them according to role.

    Admin or Django superuser:
        Configuration page

    Doctor or Staff:
        Normal dashboard
    """

    if request.user.is_authenticated:
        if user_is_admin(request.user):
            return redirect("configuration")

        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            messages.error(
                request,
                "Enter both your username and password.",
            )

            return render(
                request,
                "accounts/login.html",
                {"username": username},
                status=400,
            )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:
            messages.error(
                request,
                "Invalid username or password.",
            )

            return render(
                request,
                "accounts/login.html",
                {"username": username},
                status=401,
            )

        login(request, user)

        if user_is_admin(user):
            return redirect("configuration")

        return redirect("dashboard")

    return render(request, "accounts/login.html")


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """
    Display the normal Doctor or Staff dashboard.

    Admin users are redirected to system configuration.
    """

    if user_is_admin(request.user):
        return redirect("configuration")
    
    search_query = request.GET.get("search", "").strip()
    patients = Patient.objects.all()

    if search_query:
        patients = patients.filter(name__icontains=search_query)

    return render(
        request,
        "accounts/dashboard.html",
        {
            "is_doctor": user_is_doctor(request.user),
            "is_staff_member": user_is_staff_member(request.user),
            "patients": patients,
            "search_query": search_query,
        },
    )


@require_POST
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)

    return redirect("login")


@admin_required
@require_http_methods(["GET", "POST"])
def configuration_view(
    request: HttpRequest,
) -> HttpResponse:
    """
    Allow Admin users to configure the clinic name.
    """

    clinic_settings, _ = ClinicSettings.objects.get_or_create(
        pk=1,
        defaults={
            "clinic_name": "Physiotherapy Clinic",
        },
    )

    if request.method == "POST":
        form = ClinicSettingsForm(
            request.POST,
            instance=clinic_settings,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Clinic configuration was saved.",
            )

            return redirect("configuration")
    else:
        form = ClinicSettingsForm(
            instance=clinic_settings,
        )

    return render(
        request,
        "accounts/configuration.html",
        {
            "form": form,
        },
    )


@admin_required
def user_list_view(request: HttpRequest) -> HttpResponse:
    """
    Display all non-superuser Admin, Doctor and Staff accounts.
    """

    users = (
        User.objects
        .filter(is_superuser=False)
        .prefetch_related("groups")
        .order_by(
            "first_name",
            "last_name",
            "username",
        )
    )

    return render(
        request,
        "accounts/user_list.html",
        {
            "users": users,
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def user_create_view(
    request: HttpRequest,
) -> HttpResponse:
    """
    Create a new Admin, Doctor or Staff user.
    """

    if request.method == "POST":
        form = UserCreateForm(request.POST)

        if form.is_valid():
            user = form.save()

            messages.success(
                request,
                f"User '{user.username}' was created successfully.",
            )

            return redirect("user-list")
    else:
        form = UserCreateForm()

    return render(
        request,
        "accounts/user_form.html",
        {
            "form": form,
            "page_title": "Create user",
            "submit_label": "Create user",
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def user_edit_view(
    request: HttpRequest,
    user_id: int,
) -> HttpResponse:
    """
    Edit a non-superuser account.
    """

    managed_user = get_object_or_404(
        User,
        pk=user_id,
        is_superuser=False,
    )

    if request.method == "POST":
        form = UserEditForm(
            request.POST,
            instance=managed_user,
        )

        if form.is_valid():
            if managed_user == request.user:
                selected_role = form.cleaned_data["role"]
                selected_active = form.cleaned_data["is_active"]

                if selected_role != "Admin" or not selected_active:
                    form.add_error(
                        None,
                        (
                            "You cannot remove your own Admin role "
                            "or deactivate your own account."
                        ),
                    )
                else:
                    user = form.save()

                    messages.success(
                        request,
                        f"User '{user.username}' was updated successfully.",
                    )

                    return redirect("user-list")
            else:
                user = form.save()

                messages.success(
                    request,
                    f"User '{user.username}' was updated successfully.",
                )

                return redirect("user-list")
    else:
        form = UserEditForm(
            instance=managed_user,
        )

    return render(
        request,
        "accounts/user_form.html",
        {
            "form": form,
            "managed_user": managed_user,
            "page_title": "Edit user",
            "submit_label": "Save changes",
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def user_password_view(
    request: HttpRequest,
    user_id: int,
) -> HttpResponse:
    """
    Set a new password for a non-superuser account.
    """

    managed_user = get_object_or_404(
        User,
        pk=user_id,
        is_superuser=False,
    )

    if request.method == "POST":
        form = SetPasswordForm(
            managed_user,
            request.POST,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                f"Password changed for '{managed_user.username}'.",
            )

            return redirect("user-list")
    else:
        form = SetPasswordForm(managed_user)

    return render(
        request,
        "accounts/user_password.html",
        {
            "form": form,
            "managed_user": managed_user,
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def user_deactivate_view(
    request: HttpRequest,
    user_id: int,
) -> HttpResponse:
    """
    Deactivate a non-superuser account.
    """

    managed_user = get_object_or_404(
        User,
        pk=user_id,
        is_superuser=False,
    )

    if managed_user == request.user:
        raise PermissionDenied(
            "You cannot deactivate your own account."
        )

    if request.method == "POST":
        managed_user.is_active = False
        managed_user.save(
            update_fields=["is_active"],
        )

        messages.success(
            request,
            f"User '{managed_user.username}' was deactivated.",
        )

        return redirect("user-list")

    return render(
        request,
        "accounts/user_deactivate_confirm.html",
        {
            "managed_user": managed_user,
        },
    )


@admin_required
@require_POST
def user_activate_view(
    request: HttpRequest,
    user_id: int,
) -> HttpResponse:
    """
    Reactivate a non-superuser account.
    """

    managed_user = get_object_or_404(
        User,
        pk=user_id,
        is_superuser=False,
    )

    managed_user.is_active = True
    managed_user.save(
        update_fields=["is_active"],
    )

    messages.success(
        request,
        f"User '{managed_user.username}' was activated.",
    )

    return redirect("user-list")

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