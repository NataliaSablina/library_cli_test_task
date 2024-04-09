import os

import pytest
from unittest.mock import Mock, patch
import argparse

from fintech_file_cli.executors import CommandExecutor
from fintech_file_cli.validators import ArgumentValidator


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
def args(sample_file):
    return argparse.Namespace(
        file_path=sample_file,
        validate=True,
        add_transaction=False,
        new_value=None,
        block_field_from_changes=None,
        unblock_field_from_changes=None,
        record_type="header",
        field="name",
        amount="000000001000",
        currency="USD",
        transaction_counter=None,
    )


@pytest.fixture
def command_executor(args):
    with patch('fixed_width_struct_io.access_control.immutable_field_setter', Mock()), \
         patch('fixed_width_struct_io.readers.FieldRetriever', Mock()), \
         patch('fixed_width_struct_io.validators.FileStructureValidator', Mock()), \
         patch('fixed_width_struct_io.validators.StringLengthValidator', Mock()), \
         patch('fixed_width_struct_io.validators.ValuesValidator', Mock()), \
         patch('fixed_width_struct_io.writers.FieldEditor', Mock()), \
         patch('fixed_width_struct_io.writers.TransactionAppender', Mock()) as mocked_transaction_appender:

        executor = CommandExecutor(
            args=args,
            file_structure_validator=Mock(),
            length_validator=Mock(),
            values_validator=Mock(),
            field_retriever=Mock(),
            field_editor=Mock(),
            transaction_appender=mocked_transaction_appender,
            immutable_field_setter=Mock(),
        )
    return executor, mocked_transaction_appender


@pytest.fixture
def args_none(sample_file):
    return argparse.Namespace(
        file_path=sample_file,
        block_field_from_changes=None,
        unblock_field_from_changes=None,
        record_type=None,
        field=None,
        transaction_counter=None,
        new_value=None,
        add_transaction=None,
        amount=None,
        currency=None,
        log=None,
    )


@pytest.fixture
def validator(args_none):
    return ArgumentValidator(args_none)
