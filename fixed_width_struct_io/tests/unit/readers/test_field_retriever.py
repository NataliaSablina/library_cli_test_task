import pytest

from fixed_width_struct_io.constants import FieldLength


def test_retrieve_header_field_valid(field_retriever):
    expected_value = "nnnnnn                      "
    retrieved_value = field_retriever.retrieve("header", "name")
    assert retrieved_value == expected_value, "Header field value mismatch."


def test_retrieve_header_field_invalid(field_retriever):
    with pytest.raises(ValueError):
        field_retriever.retrieve("HEADER", "invalid_field")


def test_retrieve_transaction_field_valid(field_retriever):
    expected_value = "000000009000"
    retrieved_value = field_retriever.retrieve("transaction", "amount", transaction_index="000001")
    assert retrieved_value == expected_value, "Transaction field value mismatch."


def test_retrieve_transaction_field_invalid_index(field_retriever):
    with pytest.raises(ValueError):
        field_retriever.retrieve("transaction", "amount", transaction_index="0000011")


def test_retrieve_transaction_field_no_index(field_retriever):
    with pytest.raises(ValueError):
        field_retriever.retrieve("transaction", "amount")


def test_retrieve_footer_field_valid(field_retriever):
    expected_value = "000012"
    retrieved_value = field_retriever.retrieve("footer", "total counter")
    assert retrieved_value == expected_value, "Footer field value mismatch."


def test_retrieve_invalid_record_type(field_retriever):
    with pytest.raises(ValueError):
        field_retriever.retrieve("unknown", "unknown")


@pytest.mark.parametrize("line,field_sizes,expected", [
    ("02,000003,000000001000,gbp,                                                                                                 ", {
        "field id": FieldLength(1, 2),
        "counter": FieldLength(3, 8),
        "amount": FieldLength(9, 20),
        "currency": FieldLength(21, 23),
        "reserved": FieldLength(24, 120),
    }, {"field id": "02", "counter": "000003", "amount": "000000001000", "currency": "gbp", "reserved": "                                                                                                 "}),
])
def test_extract_fields(line, field_sizes, expected, field_retriever):
    assert field_retriever._extract_fields(line, field_sizes) == expected


def test_process_file_lines(field_retriever):
    header, transactions, footer = field_retriever._process_file_lines()

    assert header is not None
    assert len(transactions) == 3
    assert footer is not None
