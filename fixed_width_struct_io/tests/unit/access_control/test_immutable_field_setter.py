import json
from unittest.mock import patch, mock_open

import pytest


def test_load_immutable_fields_success(immutable_field_setter_mock):
    with open(immutable_field_setter_mock.config_path, "w") as config_file:
        config_file.write('{"immutable_fields": ["amount"]}')

    fields = immutable_field_setter_mock._load_immutable_fields()
    assert fields == {"amount"}


def test_make_field_immutable(immutable_field_setter_mock):
    assert 'name' not in immutable_field_setter_mock._immutable_fields
    immutable_field_setter_mock.make_field_immutable('name')
    assert 'name' in immutable_field_setter_mock._immutable_fields


def test_make_field_mutable(immutable_field_setter_mock):
    immutable_field_setter_mock.make_field_immutable('name')
    assert 'name' in immutable_field_setter_mock._immutable_fields
    immutable_field_setter_mock.make_field_mutable('name')
    assert 'name' not in immutable_field_setter_mock._immutable_fields


def test_is_field_immutable(immutable_field_setter_mock):
    immutable_field_setter_mock.make_field_immutable('counter')
    assert immutable_field_setter_mock.is_field_immutable('counter') is True
    assert immutable_field_setter_mock.is_field_immutable('field id') is False


def test_load_immutable_fields_file_not_found(immutable_field_setter_mock):
    immutable_field_setter_mock.config_path = "non_existent_file.json"
    with patch('os.path.exists', return_value=False):
        fields = immutable_field_setter_mock._load_immutable_fields()
    assert fields == set()


def test_load_immutable_fields_json_decode_error(immutable_field_setter_mock):
    with patch('json.load', side_effect=json.JSONDecodeError("Err", "doc", 0)):
        fields = immutable_field_setter_mock._load_immutable_fields()
    assert fields == set()


def test_field_does_not_exist(immutable_field_setter_mock):
    with pytest.raises(ValueError):
        immutable_field_setter_mock._field_exists("nonexistent_field")


def test_save_immutable_fields_io_error(immutable_field_setter_mock):
    with patch('builtins.open', mock_open()) as mocked_file:
        mocked_file.side_effect = IOError("Test error")
        with pytest.raises(IOError):
            immutable_field_setter_mock._save_immutable_fields()
