from rest_framework import generics, serializers, status
from rest_framework.response import Response

from .models import DynamicModel
from .serializers import DynamicModelSerializer
from .utils import check_model_fields, get_model


class CreateUpdateDynamicModelView(generics.CreateAPIView, generics.UpdateAPIView):
    serializer_class = DynamicModelSerializer
    queryset = DynamicModel.objects.all()
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
    """
    Base class for getting Dynamic Serializer class for Dynamic Model
    """

    def get_serializer_class(self):
        class DynamicTableSerializer(serializers.ModelSerializer):
            class Meta:
                model = self.model
                fields = "__all__"

        return DynamicTableSerializer


class AddRowsDynamicModelView(GetDynamicSerializer, generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        model, model_object = get_model(kwargs.get("id"))
        self.model = model

        serializer = self.get_serializer(data=request.data["rows"], many=True)
        serializer.is_valid(raise_exception=True)

        # We need to do validations here, as we are dealing with dynamic models
        # Serializer for dynamic model is also created on the fly
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
    def get_queryset(self):
        # Get dynamic model and query it
        model, model_object = get_model(self.kwargs.get("id"))
        self.model = model
        return model.objects.all()
