from typing import Union, Any
from django.contrib import admin
from django.db import connection, models
from django.db.models.query import QuerySet
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from .models import DynamicModel, DynamicModelField


def prepare_fields(
    fields: Union[list[dict], QuerySet],
    single_field_name: str = "",
    remove_extra_options: bool = False,
) -> Union[dict, models.Field]:
    """
    Parse fields and create models Fields
    :param fields:
    :param single_field_name:
    :param remove_extra_options:
    :return:
    """
    model_fields = {}
    if isinstance(fields, QuerySet):
        for field in fields:
            model_field = None
            field.options = field.options or {}
            if not remove_extra_options:
                field.options["name"] = field.name
                field.options["db_column"] = field.name

            if field.type == "string":
                model_field = models.CharField(**field.options)
            elif field.type == "int":
                model_field = models.IntegerField(**field.options)
            elif field.type == "float":
                model_field = models.FloatField(**field.options)
            elif field.type == "bool":
                model_field = models.BooleanField(**field.options)

            if single_field_name == field.name:
                return model_field

            model_fields[field.name] = model_field

    else:
        for field in fields:
            model_field = None
            field["options"] = field.get("options") or {}
            if not remove_extra_options:
                field.get("options")["name"] = field.get("name")
                field.get("options")["db_column"] = field.get("name")

            if field.get("type") == "string":
                model_field = models.CharField(**field.get("options"))
            elif field.get("type") == "int":
                model_field = models.IntegerField(**field.get("options"))
            elif field.get("type") == "float":
                model_field = models.FloatField(**field.get("options"))
            elif field.get("type") == "bool":
                model_field = models.BooleanField(**field.get("options"))

            if single_field_name == field.get("name"):
                return model_field

            model_fields[field.get("name")] = model_field

    return model_fields


def create_model(
    name: str, fields: dict = None, options: dict = None, admin_opts: dict = None
) -> Any:
    """
    Create specified model, with base class models.Model
    :param name:
    :param fields:
    :param options:
    :param admin_opts:
    :return:
    """

    class Meta:
        app_label = "tables"

    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.items():
            setattr(Meta, key, value)

    # Set up a dictionary to simulate declarations within a class
    attrs = {"__module__": "tables.models", "Meta": Meta}

    # Add in any fields that were provided
    if fields:
        attrs.update(fields)

    # Create the class, which automatically triggers ModelBase processing
    try:
        model = type(name, (models.Model,), attrs)
    except TypeError as exc:
        raise serializers.ValidationError(str(exc))

    # Create an Admin class if admin options were provided
    if admin_opts is not None:

        class Admin(admin.ModelAdmin):
            pass

        for key, value in admin_opts.items():
            setattr(Admin, key, value)
        admin.site.register(model, Admin)

    return model


def get_model(model_id: int) -> tuple[Any, DynamicModel]:
    """
    Get dynamic model and model_object that represents it
    :param model_id:
    :return:
    """
    try:
        model_object = DynamicModel.objects.get(id=model_id)
        model_fields = prepare_fields(
            model_object.fields.all(), remove_extra_options=True
        )

        model = create_model(
            name=model_object.name,
            fields=model_fields,
            options=model_object.options,
            admin_opts=model_object.admin_opts,
        )
    except ObjectDoesNotExist as exc:
        # raise Validation here, this function is used in many places including view functions
        raise serializers.ValidationError(str(exc))

    return model, model_object


def get_model_fields_names(model_object: DynamicModel) -> dict:
    """
    Retrieve model_object.fields names
    :param model_object:
    :return:
    """
    model_fields = {}
    for field_name in model_object.fields.values_list("name", "id"):
        model_fields[field_name[1]] = field_name[0]

    return model_fields


def get_input_fields_names(
    fields: Union[dict, list[dict]], rows_object: bool = True
) -> dict:
    """
    Get field names of input rows or fields
    :param fields:
    :param rows_object:
    :return:
    """
    input_fields = {}
    if rows_object:
        for field in fields:
            # in case rows object assign id negative values
            input_fields.update(
                dict((-idx - 1, key) for idx, key in enumerate(field.keys()))
            )
    else:
        # if id is not provided assign negative value
        negative_idx = -1
        for field in fields:
            field_name = field["name"]
            field_id = field.get("id", negative_idx)
            if field_id < 0:
                negative_idx -= 1
            input_fields[field_id] = field_name
    return input_fields


def get_single_input_field(
    input_fields: list[dict], name: str, remove_extra_options: bool = True
) -> dict:
    """
    Get single field by name from list of fields
    :param input_fields:
    :param name:
    :param remove_extra_options:
    :return:
    """
    for field in input_fields:
        if field.get("name") == name:
            if remove_extra_options:
                field.get("options", {}).pop("db_column", None)
                field.get("options", {}).pop("name", None)
            return field


def get_single_model_field(model_fields: QuerySet, name: str) -> DynamicModelField:
    """
    Get single field by name from dynamic model fields
    :param model_fields:
    :param name:
    :return:
    """
    for field in model_fields:
        if field.name == name:
            return field


def check_model_fields(model_object: DynamicModel, rows: list) -> bool:
    """
    Checks if field names in rows are valid model fields
    :param model_object:
    :param rows:
    :return:
    """
    model_fields = get_model_fields_names(model_object)
    input_fields = get_input_fields_names(rows)

    for field in input_fields.values():
        if field not in model_fields.values():
            return False

    return True


def create_model_db(model: models.Model):
    """
    Create model in DB, uses schema_editor to perform DB query
    :param model:
    :return:
    """
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(model)


def update_model(old_model: DynamicModel, new_model: dict):
    """
    Performs dynamic model update in DB
    Rename table, Update model options, Update model fields

    :param old_model:
    :param new_model:
    :return:
    """
    if old_model.name != new_model.get("name"):
        rename_model_table(old_model.name, new_model.get("name"))
        old_model.name = new_model.get("name")

    if old_model.options != new_model.get("options"):
        old_model.options = new_model.get("options")

    old_model.save()
    model, model_object = get_model(old_model.id)

    if old_model.fields.count() != len(new_model.get("fields")):
        update_model_fields(model, model_object, new_model.get("fields"))
    else:
        for model_field, input_field in zip(
            old_model.fields.all(), new_model.get("fields")
        ):
            is_same = compare_fields(model_field, input_field)
            if not is_same:
                update_model_fields(model, model_object, new_model.get("fields"))
                break

    old_model.save()


def compare_fields(model_field: DynamicModelField, input_field: dict) -> bool:
    is_name_equal = model_field.name == input_field.get("name")
    is_type_equal = model_field.type == input_field.get("type")
    is_options_equal = model_field.options == input_field.get("options")

    return is_name_equal and is_type_equal and is_options_equal


def update_model_fields(
    model: models.Model, model_object: DynamicModel, new_fields: list[dict]
):
    """
    Update dynamic model fields in DB.
    Rename, Remove, Alter, Add model's table column
    :param model:
    :param model_object:
    :param new_fields:
    :return:
    """
    model_fields = get_model_fields_names(model_object)
    input_fields = get_input_fields_names(new_fields, rows_object=False)

    for field_id, model_field_name in model_fields.items():
        if model_field_name not in input_fields.values():
            if field_id in input_fields.keys():
                rename_model_field(model, model_field_name, input_fields[field_id])
                model_fields[field_id] = input_fields[field_id]
                new_field = get_single_input_field(new_fields, input_fields[field_id])

                model_old_field, _ = DynamicModelField.objects.get_or_create(
                    name=model_field_name,
                    type=new_field.get("type"),
                    options=new_field.get("options"),
                )
                model_object.fields.remove(model_old_field)

                model_new_field, _ = DynamicModelField.objects.get_or_create(
                    name=new_field.get("name"),
                    type=new_field.get("type"),
                    options=new_field.get("options"),
                )
                model_object.fields.add(model_new_field)
                model_object.save()
            else:
                field = prepare_fields(
                    model_object.fields.all(), single_field_name=model_field_name
                )
                model_remove_table_field(model, field)
                old_field_object = get_single_model_field(
                    model_object.fields.all(), model_field_name
                )
                field, _ = DynamicModelField.objects.get_or_create(
                    name=old_field_object.name,
                    type=old_field_object.type,
                    options=old_field_object.options,
                )

                model_object.fields.remove(field)

    for new_field in input_fields.values():
        new_field_object = get_single_input_field(
            new_fields, new_field, remove_extra_options=True
        )
        old_field_object = get_single_model_field(model_object.fields.all(), new_field)
        field = prepare_fields(new_fields, single_field_name=new_field)
        model_field = prepare_fields(
            model_object.fields.all(), single_field_name=new_field
        )

        if new_field in model_fields.values():
            model_alter_table_field(model, model_field, field)
            old_field, _ = DynamicModelField.objects.get_or_create(
                name=old_field_object.name,
                type=old_field_object.type,
                options=old_field_object.options,
            )
            model_object.fields.remove(old_field)
            new_field, _ = DynamicModelField.objects.get_or_create(
                name=new_field_object.get("name"),
                type=new_field_object.get("type"),
                options=new_field_object.get("options"),
            )
            model_object.fields.add(new_field)
        else:
            model_add_table_field(model, field)

            field, _ = DynamicModelField.objects.get_or_create(
                name=new_field_object.get("name"),
                type=new_field_object.get("type"),
                options=new_field_object.get("options"),
            )

            model_object.fields.add(field)
            model_object.save()


def rename_model_table(old_model_name: str, new_model_name: str):
    with connection.schema_editor() as schema_editor:
        sql = "ALTER TABLE %(old_table)s RENAME TO %(new_table)s" % {
            "old_table": f'"tables_{old_model_name}"',
            "new_table": f'"tables_{new_model_name}"',
        }

        schema_editor.execute(sql)


def rename_model_field(model: models.Model, old_field_name: str, new_field_name: str):
    with connection.schema_editor() as schema_editor:
        sql = "ALTER TABLE %(table)s RENAME COLUMN %(old_column)s TO %(new_column)s" % {
            "table": f'"tables_{model.__name__}"',
            "old_column": f'"{old_field_name}"',
            "new_column": f'"{new_field_name}"',
        }

        schema_editor.execute(sql)


def model_alter_table_field(
    model: models.Model, old_field: models.Field, new_field: models.Field
):
    with connection.schema_editor() as schema_editor:
        old_field.column = old_field.db_column
        new_field.column = new_field.db_column
        schema_editor.alter_field(model, old_field, new_field)


def model_add_table_field(model: models.Model, field: models.Field):
    with connection.schema_editor() as schema_editor:
        # Without concrete schema_editor.add_field is raising error
        field.concrete = True
        field.column = field.db_column
        schema_editor.add_field(model, field)


def model_remove_table_field(model: models.Model, field: models.Field):
    with connection.schema_editor() as schema_editor:
        field.column = field.db_column
        schema_editor.remove_field(model, field)
