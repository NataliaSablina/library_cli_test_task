import pytest

from fixed_width_struct_io.access_control import immutable_field_setter
from fixed_width_struct_io.constants import FieldLength, RECORD_TYPES


HEADER = "01,nnnnnn                      ,ooooooo                       ,dnit                          ,street4567                    "
FOOTER = "03,000012,000000044000,                                                                                                    ."
UPDATED_FIRST_TRANSACTION = "02,000001,000000008000,gbp,                                                                                                 "
SECOND_TRANSACTION = "02,000002,000000034000,eur,                                                                                                 "
THIRD_TRANSACTION = "02,000003,000000001000,gbp,                                                                                                 "


def test_extract_fields_success(field_editor):
    line = "01,nnnnnn                      ,ooooooo                       ,dnit                          ,street4567                    "
    field_sizes = {
        "field id": FieldLength(1, 2),
        "name": FieldLength(3, 30),
        "surname": FieldLength(31, 60),
        "patronymic": FieldLength(61, 90),
        "address": FieldLength(91, 120),
    }
    extracted_fields = field_editor._extract_fields(line, field_sizes)
    assert extracted_fields == {"field id": "01", "name": "nnnnnn                      ", "surname": "ooooooo                       ", "patronymic": "dnit                          ", "address": "street4567                    "}


def test_extract_fields_failure(field_editor):
    line = "01,nnnnnn                      ,dnit                          ,street4567                    "
    field_sizes = {
        "field id": FieldLength(1, 2),
        "name": FieldLength(3, 30),
        "surname": FieldLength(31, 60),
        "patronymic": FieldLength(61, 90),
        "address": FieldLength(91, 120),
    }
    with pytest.raises(Exception):
        field_editor._extract_fields(line, field_sizes)


def test_validate_new_value_success(field_editor):
    assert field_editor._validate_new_value('header', 'name', 'kkkkkk                      ')


def test_validate_new_value_failure_invalid_record_type(field_editor):
    with pytest.raises(ValueError):
        field_editor._validate_new_value('unknown', 'name', 'kkkkkk                      ')


def test_validate_new_value_failure_invalid_field_name(field_editor):
    with pytest.raises(ValueError):
        field_editor._validate_new_value('header', 'invalid_field', 'kkkkkk                      ')


def test_calculate_new_control_sum(field_editor):
    updated_lines = [HEADER, UPDATED_FIRST_TRANSACTION, SECOND_TRANSACTION, THIRD_TRANSACTION]
    new_control_sum = field_editor._calculate_new_control_sum(updated_lines)
    assert new_control_sum == '000000043000'


def test_edit_field_value_success_header(field_editor):
    assert field_editor.edit_field_value('header', 'address', None, 'street4567                    ')


def test_edit_field_value_success_transaction(field_editor):
    assert field_editor.edit_field_value('transaction', 'currency', "000001", 'usd')


def test_edit_field_value_failure_immutable_field(field_editor, monkeypatch):
    monkeypatch.setattr(immutable_field_setter, 'is_field_immutable', lambda x: True)
    with pytest.raises(ValueError):
        field_editor.edit_field_value('transaction', 'amount', "000001", '000000009000')


def test_edit_field_value_failure_invalid_new_value(field_editor):
    with pytest.raises(ValueError):
        field_editor.edit_field_value('header', 'name', None, 'InvalidValue')
