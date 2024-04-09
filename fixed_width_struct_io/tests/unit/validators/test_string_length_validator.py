import pytest
from unittest.mock import patch
from fixed_width_struct_io.validators.string_length_validator import StringLengthValidator

RECORD_TYPE_HEADER_ID = "01"
RECORD_TYPE_TRANSACTION_ID = "02"
RECORD_TYPE_FOOTER_ID = "03"
RECORD_TYPE_HEADER = "header"
RECORD_TYPE_UNKNOWN = "04"
VALID_LINE = "01,nnnnnn                      ,ooooooo                       ,dnit                          ,street4567                    "
INVALID_LINE_TOO_SHORT = "01,nnnnnn                      ,ooooooo                       "
INVALID_LINE_TOO_LONG = "01,nnnnnn            test          ,ooooooo                       ,dnit                          ,street4567        test            "
FIELD_ORDER = {
    RECORD_TYPE_HEADER_ID: ["field id", "name", "surname", "patronymic", "address"],
    RECORD_TYPE_TRANSACTION_ID: ["field id", "counter", "amount", "currency", "reserved"],
    RECORD_TYPE_FOOTER_ID: ["field id", "total counter", "control sum", "reserved"],
}


@pytest.mark.parametrize("known_record_types", [
    RECORD_TYPE_TRANSACTION_ID,
    RECORD_TYPE_HEADER_ID,
    RECORD_TYPE_FOOTER_ID,

])
def test_validate_record_type_known(known_record_types):
    """Test that known record types pass validation."""
    validator = StringLengthValidator(lines=[VALID_LINE])
    try:
        validator.validate_record_type(known_record_types)
    except ValueError:
        pytest.fail("validate_record_type raised ValueError unexpectedly!")


def test_validate_record_type_unknown():
    """Test that unknown record types raise ValueError."""
    validator = StringLengthValidator(lines=[VALID_LINE])
    with pytest.raises(ValueError):
        validator.validate_record_type(RECORD_TYPE_UNKNOWN)


def test_validate_total_line_length_correct():
    """Test that lines of correct total length pass validation."""
    validator = StringLengthValidator(lines=[VALID_LINE])
    try:
        validator.validate_total_line_length(VALID_LINE)
    except ValueError:
        pytest.fail("validate_total_line_length raised ValueError unexpectedly!")


def test_validate_total_line_length_incorrect():
    """Test that lines of incorrect total length raise ValueError."""
    validator = StringLengthValidator(lines=[VALID_LINE])
    with pytest.raises(ValueError):
        validator.validate_total_line_length(INVALID_LINE_TOO_LONG)


def test_validate_line_valid():
    """Test that a valid line passes all validations."""
    validator = StringLengthValidator(lines=[VALID_LINE])
    validator.lines = [VALID_LINE]
    assert validator.validate_line(VALID_LINE, line_number=1) == True


def test_validate_field_order_valid(string_length_validator):
    """Test validation passes with a valid record type."""
    try:
        string_length_validator.validate_field_order(RECORD_TYPE_HEADER_ID)
    except ValueError:
        pytest.fail("Unexpected ValueError for valid field order.")


def test_validate_field_order_invalid(string_length_validator):
    """Test validation fails with an unknown record type."""
    with pytest.raises(ValueError):
        string_length_validator.validate_field_order(RECORD_TYPE_UNKNOWN)


def test_validate_fields_count_correct(string_length_validator):
    """Test validation passes with correct number of fields."""
    fields = VALID_LINE.split(",")
    ordered_field_names = FIELD_ORDER[RECORD_TYPE_HEADER_ID]
    try:
        string_length_validator.validate_fields_count(fields, ordered_field_names, RECORD_TYPE_HEADER_ID)
    except ValueError:
        pytest.fail("Unexpected ValueError for correct number of fields.")


def test_validate_fields_count_incorrect(string_length_validator):
    """Test validation fails with incorrect number of fields."""
    fields = INVALID_LINE_TOO_SHORT.split(",")
    ordered_field_names = FIELD_ORDER[RECORD_TYPE_HEADER_ID]
    with pytest.raises(ValueError):
        string_length_validator.validate_fields_count(fields, ordered_field_names, RECORD_TYPE_HEADER_ID)


@pytest.mark.parametrize("field_name, field_value, expected", [
    ("name", "nnnnnn                      ", True),
    ("surname", "ooooooo2222222222222                       ", False),
])
def test_validate_individual_field_length(field_name, field_value, expected):
    """Test individual field length validation."""
    if expected:
        assert StringLengthValidator.validate_individual_field_length(RECORD_TYPE_HEADER_ID, field_name,
                                                                      field_value) is True
    else:
        with pytest.raises(ValueError):
            StringLengthValidator.validate_individual_field_length(RECORD_TYPE_HEADER, field_name, field_value)


def test_validate_whole_file_valid():
    """Test file validation passes with all valid lines."""
    lines = [VALID_LINE, VALID_LINE]
    validator = StringLengthValidator(lines=lines)
    validator.lines = lines
    assert validator.validate() is True


def test_validate_whole_file_invalid():
    """Test file validation fails with any invalid line."""
    lines = [VALID_LINE, INVALID_LINE_TOO_LONG]
    validator = StringLengthValidator(lines=lines)
    validator.lines = lines
    with pytest.raises(ValueError):
        validator.validate()
