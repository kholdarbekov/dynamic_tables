from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import DynamicModel
from .serializers import DynamicModelSerializer
from .utils import check_model_fields, get_model


class CreateDynamicModelView(generics.CreateAPIView, generics.UpdateAPIView):
    serializer_class = DynamicModelSerializer
    queryset = DynamicModel.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ("post", "put")
    lookup_field = "id"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class GetDynamicSerializer:
    def get_serializer_class(self):
        class DynamicModelSerializer(serializers.ModelSerializer):
            class Meta:
                model = self.model
                fields = "__all__"

        return DynamicModelSerializer


class AddRowsDynamicModelView(GetDynamicSerializer, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        model, model_object = get_model(kwargs.get("id"))
        self.model = model

        serializer = self.get_serializer(data=request.data["rows"], many=True)
        serializer.is_valid(raise_exception=True)

        fields_names_are_valid = check_model_fields(
            model_object, request.data.get("rows")
        )
        if not fields_names_are_valid:
            raise serializers.ValidationError(
                f"field names are not valid for model {model_object.name}"
            )

        row_ids = []
        for row in request.data.get("rows"):
            row_object = model.objects.create(**row)
            row_ids.append(row_object.id)

        return Response(row_ids, status=status.HTTP_201_CREATED)


class ListDynamicTableRowsView(GetDynamicSerializer, generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get the list of items for this view.
        This must be an iterable, and may be a queryset.
        Defaults to using `self.queryset`.

        This method should always be used rather than accessing `self.queryset`
        directly, as `self.queryset` gets evaluated only once, and those results
        are cached for all subsequent requests.

        You may want to override this if you need to provide different
        querysets depending on the incoming request.

        (Eg. return a list of items that is specific to the user)
        """
        model, model_object = get_model(self.kwargs.get("id"))
        self.model = model
        return model.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
