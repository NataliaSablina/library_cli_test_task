from unittest.mock import patch

import pytest

from fixed_width_struct_io.constants import FieldLength


def test_extract_fields_success(transaction_appender):
    line = "01,nnnnnn                      ,ooooooo                       ,dnit                          ,street4567                    "
    field_sizes = {
        "field id": FieldLength(1, 2),
        "name": FieldLength(3, 30),
        "surname": FieldLength(31, 60),
        "patronymic": FieldLength(61, 90),
        "address": FieldLength(91, 120),
    }
    extracted_fields = transaction_appender._extract_fields(line, field_sizes)
    assert extracted_fields == {"field id": "01", "name": "nnnnnn                      ",
                                "surname": "ooooooo                       ",
                                "patronymic": "dnit                          ",
                                "address": "street4567                    "}


def test_validate_new_transaction_fields_success(transaction_appender):
    assert transaction_appender._validate_new_transaction_fields("000000001000", "USD") is True


def test_validate_new_transaction_fields_failure(transaction_appender):
    with pytest.raises(ValueError):
        transaction_appender._validate_new_transaction_fields("000000001000", "INVALID")


def test_append_transaction_success(transaction_appender):
    assert transaction_appender.append_transaction("000000002000", "USD") is True


def test_append_transaction_validation_failure(transaction_appender):
    with pytest.raises(ValueError):
        transaction_appender.append_transaction("00000002000", "INVALID")


def test_get_next_counter_no_transactions(transaction_appender):
    lines = [
        "01,nnnnnn                      ,ooooooo                       ,dnit                          ,street4567                    ",
        "03,000012,000000044000,                                                                                                     "
    ]
    with pytest.raises(ValueError):
        transaction_appender._get_next_counter(lines)


def test_new_transaction(transaction_appender):
    result = transaction_appender._new_transaction("000004", "00000002000", "USD")
    assert "02,000004,00000002000,USD,                                                                                                 " in result
