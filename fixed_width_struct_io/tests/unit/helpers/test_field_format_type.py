from fixed_width_struct_io.helpers import FieldFormat


def test_create_field_format(sample_field_format):
    assert sample_field_format.start_position == 1
    assert sample_field_format.end_position == 10
    assert sample_field_format.data_type == str
    assert sample_field_format.fixed_value == "FixedValue"
    assert sample_field_format.regex_value == r"\d{3}-\d{2}-\d{4}"


def test_create_field_format_without_fixed_value():
    field_format = FieldFormat(1, 10, str)
    assert field_format.fixed_value is None


def test_create_field_format_without_regex_value():
    field_format = FieldFormat(1, 10, str)
    assert field_format.regex_value is None
