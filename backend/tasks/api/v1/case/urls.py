from django.urls import path

from .views import (
    CaseListApi,
    CaseCreateApi,
    CaseDetailApi,
    CaseUpdateApi,
    CaseDeleteApi,
    ResourceListApi,
    ResourceCreateApi,
    ResourceDetailApi,
    ResourceUpdateApi,
    ResourceDeleteApi,
    CaseActivateApi,
    CaseDeactivateApi,
)

app_name = "case"

urlpatterns = [
    path("", CaseListApi.as_view(), name="case-list"),
    path("create/", CaseCreateApi.as_view(), name="case-create"),
    path("<int:pk>/", CaseDetailApi.as_view(), name="case-detail"),
    path("<int:pk>/update/", CaseUpdateApi.as_view(), name="case-update"),
    path("<int:pk>/delete/", CaseDeleteApi.as_view(), name="case-delete"),
    path(
        "resources/",
        ResourceListApi.as_view(),
        name="resource-list",
    ),

    path(
        "resources/create/",
        ResourceCreateApi.as_view(),
        name="resource-create",
    ),

    path(
        "resources/<int:pk>/",
        ResourceDetailApi.as_view(),
        name="resource-detail",
    ),

    path(
        "resources/<int:pk>/update/",
        ResourceUpdateApi.as_view(),
        name="resource-update",
    ),

    path(
        "resources/<int:pk>/delete/",
        ResourceDeleteApi.as_view(),
        name="resource-delete",
    ),
    
    path(
        "<int:pk>/activate/",
        CaseActivateApi.as_view(),
        name="case-activate",
    ),

    path(
        "<int:pk>/deactivate/",
        CaseDeactivateApi.as_view(),
        name="case-deactivate",
    ),
]