from django.urls import path

from .views import (
    AddRowsDynamicModelView,
    CreateDynamicModelView,
    ListDynamicTableRowsView,
)

urlpatterns = [
    path(
        "table",
        CreateDynamicModelView.as_view(
            http_method_names=[
                "post",
            ]
        ),
        name="table_create",
    ),
    path(
        "table/<int:id>",
        CreateDynamicModelView.as_view(
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
