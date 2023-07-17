import pytest
from django.db import models

from tables import utils


def test_prepare_fields(dummy_fields):
    prepared_fields = utils.prepare_fields(dummy_fields)

    assert prepared_fields["dummy_field_1"] is not None
    assert isinstance(prepared_fields["dummy_field_1"], models.CharField)
    assert prepared_fields["dummy_field_1"].max_length == 128
    assert prepared_fields["dummy_field_1"].name == "dummy_field_1"

    assert prepared_fields["dummy_field_2"] is not None
    assert isinstance(prepared_fields["dummy_field_2"], models.IntegerField)
    assert prepared_fields["dummy_field_2"].name == "dummy_field_2"

    assert prepared_fields["dummy_field_3"] is not None
    assert isinstance(prepared_fields["dummy_field_3"], models.FloatField)
    assert prepared_fields["dummy_field_3"].null is True
    assert prepared_fields["dummy_field_3"].name == "dummy_field_3"

    assert prepared_fields["dummy_field_4"] is not None
    assert isinstance(prepared_fields["dummy_field_4"], models.BooleanField)
    assert prepared_fields["dummy_field_4"].default is True
    assert prepared_fields["dummy_field_4"].name == "dummy_field_4"

    # test retrieving single field
    prepared_field = utils.prepare_fields(
        dummy_fields, single_field_name="dummy_field_1"
    )

    assert prepared_field is not None
    assert isinstance(prepared_field, models.CharField)
    assert prepared_field.max_length == 128
    assert prepared_field.name == "dummy_field_1"


@pytest.mark.django_db
def test_create_model(dummy_fields, mocker):
    model_name = "dummy_model_1"
    prepared_fields = utils.prepare_fields(dummy_fields)
    options = {"ordering": ["dummy_field_1"], "verbose_name": "Dummy objects"}
    model = utils.create_model(model_name, prepared_fields, options)

    assert model.__name__ == model_name
    assert model.__bases__ == (models.Model,)
    assert model._meta.ordering == options["ordering"]
    assert model._meta.verbose_name == options["verbose_name"]
    for model_field, dummy_field in zip(model._meta.fields[1:], dummy_fields):
        assert model_field.name == dummy_field["name"]

    with mocker.patch("django.db.connection"):
        assert utils.create_model_db(model) is None


def test_get_input_fields_names(dummy_fields):
    input_field_names = utils.get_input_fields_names(dummy_fields, rows_object=False)
    for input_field_name, dummy_field in zip(input_field_names.values(), dummy_fields):
        assert input_field_name == dummy_field.get("name")


def test_get_single_input_field(dummy_fields):
    dummy_field_1 = utils.get_single_input_field(dummy_fields, "dummy_field_1")
    assert dummy_field_1.get("name") == "dummy_field_1"
    assert dummy_field_1.get("type") == "string"
    assert dummy_field_1.get("options") == {"max_length": 128}
