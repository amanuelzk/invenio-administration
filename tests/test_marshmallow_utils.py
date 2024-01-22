# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
# Copyright (C) 2023 KTH Royal Institute of Technology.
#
# invenio-administration is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

import pytest
from marshmallow import Schema, fields

from invenio_administration.marshmallow_utils import custom_mapping, jsonify_schema


class CustomField(fields.Field):
    """A custom field class that extends the base Field class."""

    pass


class CustomInheritedField(CustomField):
    """An inherited custom field class derived from CustomField."""

    pass


class UnrecognizedField(fields.Field):
    """A custom field class that is not recognized in the custom mapping."""

    pass


class TestSchema(Schema):
    """Schema class for testing, with various field types."""

    string_field = fields.Str()
    integer_field = fields.Integer()
    custom_field = CustomField()
    inherited_field = CustomInheritedField()


@pytest.fixture
def update_custom_mapping():
    """
    Pytest fixture to temporarily update the custom mapping for field types.
    Restores the original mapping after the test.
    """
    original_mapping = custom_mapping.copy()
    custom_mapping[CustomField] = "custom"
    custom_mapping[CustomInheritedField] = "custom"
    yield
    custom_mapping.clear()
    custom_mapping.update(original_mapping)


def test_jsonify_schema_with_standard_fields(update_custom_mapping):
    """Assert standard field types are correctly identified."""
    schema = TestSchema()
    result = jsonify_schema(schema)
    assert result["string_field"]["type"] == "string"
    assert result["integer_field"]["type"] == "integer"


def test_jsonify_schema_with_custom_field(update_custom_mapping):
    """Assert custom_field is identified as 'custom'."""
    schema = TestSchema()
    result = jsonify_schema(schema)
    assert result["custom_field"]["type"] == "custom"


def test_jsonify_schema_with_inherited_field(update_custom_mapping):
    """
    Assert inherited_field is correctly identified as 'custom'.
    """
    schema = TestSchema()
    result = jsonify_schema(schema)
    assert result["inherited_field"]["type"] == "custom"


def test_jsonify_schema_with_unrecognized_field(update_custom_mapping):
    """
    Assert jsonify_schema raises an exception for an unrecognized field in the schema.
    """

    class UnrecognizedSchema(TestSchema):
        unrecognized_field = UnrecognizedField()

    schema = UnrecognizedSchema()
    with pytest.raises(Exception) as excinfo:
        jsonify_schema(schema)
    assert "Unrecognised schema field" in str(excinfo.value)
