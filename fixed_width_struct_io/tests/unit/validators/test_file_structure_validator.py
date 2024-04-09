import pytest

HEADER = "01,nnnnnn                      ,ooooooo                       ,dnit                          ,street4567                    "
FOOTER = "03,000012,000000044000,                                                                                                    ."
FIRST_TRANSACTION = "02,000001,000000009000,gbp,                                                                                                 "
SECOND_TRANSACTION = "02,000002,000000034000,eur,                                                                                                 "
THIRD_TRANSACTION = "02,000003,000000001000,gbp,                                                                                                 "
INVALID_LINE = "04,nnnnnn                      ,ooooooo                       ,dnit                          ,street4567                    "


VALID_FILE_LINES = [HEADER, FIRST_TRANSACTION, SECOND_TRANSACTION, THIRD_TRANSACTION, FOOTER]
EXCEEDS_TRANSACTION_LIMIT = [HEADER] + [FIRST_TRANSACTION] * 21000 + [FOOTER]
INVALID_RECORD_TYPE_LINES = [HEADER, INVALID_LINE, FOOTER]
MISSING_HEADER_LINES = [FIRST_TRANSACTION, FOOTER]
MISSING_FOOTER_LINES = [HEADER, FIRST_TRANSACTION]
EXTRA_HEADER_LINES = [HEADER, HEADER, FIRST_TRANSACTION, FOOTER]
EXTRA_FOOTER_LINES = [HEADER, FIRST_TRANSACTION, FOOTER, FOOTER]


@pytest.mark.parametrize("lines,expected_exception", [
    (VALID_FILE_LINES, None),
    (EXCEEDS_TRANSACTION_LIMIT, ValueError),
    (INVALID_RECORD_TYPE_LINES, ValueError),
    (MISSING_HEADER_LINES, ValueError),
    (MISSING_FOOTER_LINES, ValueError),
    (EXTRA_HEADER_LINES, ValueError),
    (EXTRA_FOOTER_LINES, ValueError),
])
def test_validate(lines, expected_exception, validator):
    validator.lines = lines
    if expected_exception:
        with pytest.raises(expected_exception):
            validator.validate()
    else:
        assert validator.validate() is True


def test_validate_transaction_limit(validator):
    validator.lines = EXCEEDS_TRANSACTION_LIMIT
    with pytest.raises(ValueError):
        validator._validate_transaction_limit(validator.lines[1:-1])


def test_validate_record_types(validator):
    validator.lines = INVALID_RECORD_TYPE_LINES
    with pytest.raises(ValueError):
        validator._validate_record_types(validator.lines)


def test_validate_structure_with_missing_header(validator):
    validator.lines = MISSING_HEADER_LINES
    with pytest.raises(ValueError):
        validator._validate_structure(validator.lines)


def test_validate_structure_with_missing_footer(validator):
    validator.lines = MISSING_FOOTER_LINES
    with pytest.raises(ValueError):
        validator._validate_structure(validator.lines)


def test_validate_no_extra_headers_footers_with_extra_header(validator):
    validator.lines = EXTRA_HEADER_LINES
    with pytest.raises(ValueError):
        validator._validate_no_extra_headers_footers(validator.lines)


def test_validate_no_extra_headers_footers_with_extra_footer(validator):
    validator.lines = EXTRA_FOOTER_LINES
    with pytest.raises(ValueError):
        validator._validate_no_extra_headers_footers(validator.lines)


def test_validate_transactions_with_invalid_transactions(validator):
    validator.lines = [HEADER, FIRST_TRANSACTION, INVALID_LINE, SECOND_TRANSACTION, FOOTER]
    with pytest.raises(ValueError):
        transaction_lines = validator.lines[1:-1]
        validator._validate_transactions(transaction_lines)
