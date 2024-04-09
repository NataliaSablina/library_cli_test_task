import pytest


def test_validate_mandatory_file_path_missing(args_none, validator):
    args_none.record_type = 'header'
    args_none.file_path = None
    with pytest.raises(ValueError) as excinfo:
        validator.validate()
    assert "The --file-path argument is mandatory." in str(excinfo.value)


def test_validate_mandatory_file_path_present(args_none, validator):
    args_none.file_path = 'some_path'
    validator._validate_mandatory_file_path()


def test_validate_exclusive_field_blocking_conflict(args_none, validator):
    args_none.block_field_from_changes = 'some_field'
    args_none.unblock_field_from_changes = 'some_field'
    args_none.new_value = 'new_value'
    with pytest.raises(ValueError) as excinfo:
        validator.validate()
    assert "--block-field-from-changes and --unblock-field-from-changes must be used exclusively" in str(excinfo.value)


def test_validate_exclusive_field_blocking_no_conflict(args, validator):
    args.block_field_from_changes = 'some_field'
    validator._validate_exclusive_field_blocking()


def test_validate_transaction_logic_valid(args, validator):
    args.record_type = 'transaction'
    args.transaction_counter = '1'
    validator._validate_transaction_logic()


def test_validate_transaction_addition_missing_amount_currency(args_none, validator):
    args_none.add_transaction = True
    with pytest.raises(ValueError) as excinfo:
        validator.validate()
    assert "--amount and --currency are required when adding a new transaction." in str(excinfo.value)


def test_validate_transaction_addition_valid(args, validator):
    args.add_transaction = True
    args.amount = '100'
    args.currency = 'USD'
    validator._validate_transaction_addition()


def test_validate_field_editing_missing_record_type(args_none, validator):
    args_none.new_value = 'new_value'
    with pytest.raises(ValueError) as excinfo:
        validator.validate()
    assert "--record-type is required when using --new-value." in str(excinfo.value)


def test_validate_field_editing_valid(args, validator):
    args.new_value = 'new_value'
    args.field = 'some_field'
    args.record_type = 'header'
    validator._validate_field_editing()


def test_validate_retrieve_logic_missing_field(args_none, validator):
    args_none.record_type = 'header'
    with pytest.raises(ValueError) as excinfo:
        validator.validate()
    assert "--field is required when --record-type is specified." in str(excinfo.value)


def test_validate_retrieve_logic_valid(args, validator):
    args.field = 'some_field'
    args.record_type = 'header'
    validator._validate_retrieve_logic()
