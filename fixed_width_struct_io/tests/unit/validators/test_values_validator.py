import pytest
from unittest.mock import patch
from fixed_width_struct_io.validators.values_validator import ValuesValidator
from fixed_width_struct_io.constants import FIELD_FORMATS

HEADER_ID = '01'
TRANSACTION_ID = '02'
FOOTER_ID = '03'
HEADER_VALID_LINE = '01,nnnnnn                      ,ooooooo                       ,dnit                          ,street4567                    '
TRANSACTION_VALID_LINE = "02,000001,000000009000,gbp,                                                                                                 "
FOOTER_VALID_LINE = "03,000001,000000009000,                                                                                                    "

HEADER_INVALID_LINE = '01,nnnnnn                     ,ooooooo                       ,dnit                          ,street4567                    '
TRANSACTION_INVALID_LINE = "02,000001,000000009000,gui,                                                                                                "
FOOTER_VALID_INLINE = "03,000012,00000044000,                                                                                              "
VALID_LINES = [HEADER_VALID_LINE, TRANSACTION_VALID_LINE, FOOTER_VALID_LINE]
INVALID_LINES = [HEADER_INVALID_LINE, TRANSACTION_INVALID_LINE]


@pytest.mark.parametrize("record_type, field_name, field_value, expected_exception, expected_message", [
    ("01", "name", "nnnnnn                      ", None, None),
    ("01", "unknown", "value", KeyError, "'unknown'"),
])
def test_validate_field(record_type, field_name, field_value, expected_exception, expected_message):
    if expected_exception:
        with pytest.raises(expected_exception) as exc_info:
            ValuesValidator.validate_field(record_type, field_name, field_value)
        assert expected_message in str(exc_info.value)
    else:
        assert ValuesValidator.validate_field(record_type, field_name, field_value) is True


def test_validate_footer_control_digits():
    validator = ValuesValidator(lines=VALID_LINES)
    footer_fields = {"total counter": "000123", "control sum": "00000000100000"}
    calculated_total_counter = 123
    control_sum = 1000.00

    assert validator._validate_footer_control_digits(footer_fields, calculated_total_counter, control_sum)

    with pytest.raises(ValueError):
        validator._validate_footer_control_digits(footer_fields, 124, control_sum)

    with pytest.raises(ValueError):
        validator._validate_footer_control_digits(footer_fields, calculated_total_counter, 999.00)


@pytest.mark.parametrize("record_type, line, expected", [
    (HEADER_ID, "01,nnnnnn                      ,ooooooo                       ,dnit                          ,street4567                    ", True),
    (TRANSACTION_ID, "02,000001,000000009000,gbp,                                                                                                 ", True),
    (FOOTER_ID, "03,000001,000000009000,                                                                                                     ", True),
])
def test_validate_record(record_type, line, expected):
    validator = ValuesValidator(lines=VALID_LINES)
    # validator.lines = VALID_LINES  # Simulate file lines for context

    if expected:
        assert validator.validate_record(record_type, line) is True
    else:
        with pytest.raises(ValueError):
            validator.validate_record(record_type, line)


def test_validate():
    validator = ValuesValidator(lines=VALID_LINES)
    assert validator.validate() is True

    validator.lines = INVALID_LINES
    with pytest.raises(ValueError):
        validator.validate()


@pytest.mark.parametrize("record_type, field_name, field_value, expected_exception, expected_message", [
    (TRANSACTION_ID, "counter", "000001", None, None),
    (TRANSACTION_ID, "amount", "000000009000", None, None),
    (TRANSACTION_ID, "currency", "USD", None, None),
    (TRANSACTION_ID, "currency", "ZZZ", ValueError, "Invalid currency value"),
    (FOOTER_ID, "total counter", "000001", None, None),
    (FOOTER_ID, "control sum", "000000009000", None, None),
])
def test_validate_field_for_transactions_and_footer(record_type, field_name, field_value, expected_exception, expected_message):
    if expected_exception:
        with pytest.raises(expected_exception) as exc_info:
            ValuesValidator.validate_field(record_type, field_name, field_value)
        assert expected_message in str(exc_info.value)
    else:
        assert ValuesValidator.validate_field(record_type, field_name, field_value) is True

