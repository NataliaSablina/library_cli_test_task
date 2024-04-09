import pytest
from unittest.mock import patch
from fixed_width_struct_io.utils import validate_field


RECORD_TYPES = {
    "header": "01",
    "transaction": "02",
    "footer": "03",
}


@pytest.mark.parametrize(
    "record_type,field_name,field_value,length_valid,value_valid,expected",
    [
        ("header", "name", "20210101", True, True, True),
        ("transaction", "amount", "000000032000", False, True, False),
        ("footer", "control sum", "000000114000", True, False, False),
    ],
)
@patch("fixed_width_struct_io.validators.StringLengthValidator.validate_individual_field_length")
@patch("fixed_width_struct_io.validators.ValuesValidator.validate_field")
def test_validate_field_success_cases(
    mock_validate_field,
    mock_validate_length,
    record_type,
    field_name,
    field_value,
    length_valid,
    value_valid,
    expected
):
    mock_validate_length.return_value = length_valid
    mock_validate_field.return_value = value_valid
    assert validate_field(record_type, field_name, field_value) == expected


@pytest.mark.parametrize(
    "record_type,field_name,field_value,length_valid,value_valid",
    [
        ("unknown", "field", "value", True, True),
    ],
)
@patch("fixed_width_struct_io.validators.StringLengthValidator.validate_individual_field_length")
@patch("fixed_width_struct_io.validators.ValuesValidator.validate_field")
def test_validate_field_exception_cases(
    mock_validate_field,
    mock_validate_length,
    record_type,
    field_name,
    field_value,
    length_valid,
    value_valid,
):
    mock_validate_length.return_value = length_valid
    mock_validate_field.return_value = value_valid
    with pytest.raises(ValueError):
        validate_field(record_type, field_name, field_value)
