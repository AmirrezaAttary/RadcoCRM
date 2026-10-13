from django.urls import include, path

urlpatterns = [
    path(
        "user/",
        include("accounts.api.v1.user.urls"),
    ),

    path(
            "employee/",
            include("accounts.api.v1.employee.urls"),
        ),

    path(
        "auth/",
        include(
            "accounts.api.v1.auth.urls",
        ),
    ),

    path(
        "profile/",
        include(
            "accounts.api.v1.profile.urls",
        ),
    ),
]