import os
import pytest
from unittest.mock import patch
from fixed_width_struct_io.helpers import FieldFormat
from fixed_width_struct_io.readers import FieldRetriever
from fixed_width_struct_io.validators import FileStructureValidator, StringLengthValidator

from fixed_width_struct_io.access_control.immutable_field_setter import ImmutableFieldSetter
from fixed_width_struct_io.writers import FieldEditor, TransactionAppender


@pytest.fixture
def immutable_field_setter_mock():
    mocked_config_file_path = "test_field_immutable_config.json"

    with patch("fixed_width_struct_io.access_control.immutable_field_setter.FIELD_IMMUTABLE_CONFIG_FILE_NAME",
               new=mocked_config_file_path):
        setter = ImmutableFieldSetter()
        yield setter
    if os.path.exists(mocked_config_file_path):
        os.remove(mocked_config_file_path)


@pytest.fixture
def sample_file():
    sample_content = """01,nnnnnn                      ,ooooooo                       ,dnit                          ,street4567                    
02,000001,000000009000,gbp,                                                                                                 
02,000002,000000034000,eur,                                                                                                 
02,000003,000000001000,gbp,                                                                                                 
03,000012,000000044000,                                                                                                    ."""
    file_path = "sample_file.txt"
    with open(file_path, "w") as f:
        f.write(sample_content)
    yield file_path
    os.remove(file_path)


@pytest.fixture
def sample_field_format():
    return FieldFormat(1, 10, str, fixed_value="FixedValue", regex_value=r"\d{3}-\d{2}-\d{4}")


@pytest.fixture
def validator(sample_file):
    validator = FileStructureValidator(file_path=sample_file)
    with open(sample_file, 'r') as file:
        validator.lines = file.readlines()
    return validator


VALID_LINE = "01,nnnnnn                      ,ooooooo                       ,dnit                          ,street4567                    "


@pytest.fixture
def string_length_validator():
    validator = StringLengthValidator(lines=[VALID_LINE])
    return validator


@pytest.fixture
def field_retriever(sample_file):
    retriever = FieldRetriever(file_path=sample_file)
    return retriever


@pytest.fixture
def field_editor(sample_file):
    return FieldEditor(file_path=str(sample_file))


@pytest.fixture
def transaction_appender(sample_file):
    return TransactionAppender(file_path=str(sample_file))
