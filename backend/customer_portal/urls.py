from django.urls import include, path

urlpatterns = [
    path("api/v1/", include("customer_portal.api.v1.urls")),
]
