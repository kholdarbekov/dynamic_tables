from django.urls import path

from .views import (
    AddRowsDynamicModelView,
    CreateUpdateDynamicModelView,
    ListDynamicTableRowsView,
)

urlpatterns = [
    path(
        "table",
        CreateUpdateDynamicModelView.as_view(
            http_method_names=[
                "post",
            ]
        ),
        name="table_create",
    ),
    path(
        "table/<int:id>",
        CreateUpdateDynamicModelView.as_view(
            http_method_names=[
                "put",
            ]
        ),
        name="table_update",
    ),
    path(
        "table/<int:id>/row",
        AddRowsDynamicModelView.as_view(),
        name="table_create_rows",
    ),
    path(
        "table/<int:id>/rows",
        ListDynamicTableRowsView.as_view(),
        name="table_retrieve_rows",
    ),
]
