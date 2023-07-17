from django.db import OperationalError, ProgrammingError, models
from rest_framework import serializers

from .models import DynamicModel, DynamicModelField
from .utils import create_model, create_model_db, prepare_fields, update_model


class ModelFieldSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = DynamicModelField
        fields = "__all__"

    def validate_type(self, value):
        if value.lower() not in ("string", "int", "float", "bool"):
            raise serializers.ValidationError("Unsupported field type")
        return value

    def validate(self, data):
        if data["type"] == "string":
            max_length_attr = data.get("options", {}).get("max_length", -1)
            if max_length_attr < 0:
                raise serializers.ValidationError(
                    "String field must have positive max_length attr"
                )
            try:
                if data.get("options"):
                    models.CharField(**data.get("options"))
            except TypeError as exc:
                raise serializers.ValidationError(str(exc))

        if data["type"] == "int":
            try:
                if data.get("options"):
                    models.IntegerField(**data.get("options"))
            except TypeError as exc:
                raise serializers.ValidationError(str(exc))

        if data["type"] == "float":
            try:
                if data.get("options"):
                    models.FloatField(**data.get("options"))
            except TypeError as exc:
                raise serializers.ValidationError(str(exc))

        if data["type"] == "float":
            try:
                if data.get("options"):
                    models.BooleanField(**data.get("options"))
            except TypeError as exc:
                raise serializers.ValidationError(str(exc))

        return data


class DynamicModelSerializer(serializers.ModelSerializer):
    fields = ModelFieldSerializer(many=True)

    class Meta:
        model = DynamicModel
        fields = "__all__"

    def create(self, validated_data):
        fields = prepare_fields(validated_data["fields"], remove_extra_options=True)

        new_model = create_model(
            name=validated_data["name"],
            fields=fields,
            options=validated_data.get("options"),
            admin_opts=validated_data.get("admin_opts"),
        )

        try:
            create_model_db(new_model)
        except (OperationalError, ProgrammingError) as exc:
            raise serializers.ValidationError(str(exc))

        fields_list = []
        for field in validated_data["fields"]:
            new_field, _ = DynamicModelField.objects.get_or_create(
                name=field.get("name"),
                type=field.get("type"),
                options=field.get("options"),
            )
            fields_list.append(new_field)

        model = DynamicModel.objects.create(
            name=validated_data["name"],
            options=validated_data.get("options"),
            admin_opts=validated_data.get("admin_opts"),
        )
        model.fields.set(fields_list)
        return model

    def update(self, instance, validated_data):
        try:
            update_model(instance, validated_data)
        except (OperationalError, ProgrammingError) as exc:
            raise serializers.ValidationError(str(exc))
        return instance
