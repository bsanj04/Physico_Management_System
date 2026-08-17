from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.login_view,
        name="login",
    ),

    path(
        "dashboard/",
        views.dashboard_view,
        name="dashboard",
    ),

    path(
        "configuration/",
        views.configuration_view,
        name="configuration",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    path(
        "users/",
        views.user_list_view,
        name="user-list",
    ),

    path(
        "users/create/",
        views.user_create_view,
        name="user-create",
    ),

    path(
        "users/<int:user_id>/edit/",
        views.user_edit_view,
        name="user-edit",
    ),

    path(
        "users/<int:user_id>/password/",
        views.user_password_view,
        name="user-password",
    ),

    path(
        "users/<int:user_id>/deactivate/",
        views.user_deactivate_view,
        name="user-deactivate",
    ),

    path(
        "users/<int:user_id>/activate/",
        views.user_activate_view,
        name="user-activate",
    ),

]