from django.urls import include, path

urlpatterns = [
    path(
        "contract/",
        include("hr.api.v1.contract.urls"),
    ),

    path(
        "signature/",
        include("hr.api.v1.signature.urls"),
    ),
]
