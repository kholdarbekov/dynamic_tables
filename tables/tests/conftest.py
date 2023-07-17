import pytest


@pytest.fixture
def dummy_fields():
    fields = [
        {"name": "dummy_field_1", "type": "string", "options": {"max_length": 128}},
        {"name": "dummy_field_2", "type": "int"},
        {"name": "dummy_field_3", "type": "float", "options": {"null": True}},
        {"name": "dummy_field_4", "type": "bool", "options": {"default": True}},
    ]

    return fields
