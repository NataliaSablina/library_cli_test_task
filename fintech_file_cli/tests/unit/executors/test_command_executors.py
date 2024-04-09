from unittest.mock import patch


def test_execute_validate_file(command_executor):
    executor, _ = command_executor
    with patch.object(executor.file_structure_validator, 'validate') as mock_validate, \
         patch.object(executor.length_validator, 'validate') as mock_length_validate, \
         patch.object(executor.values_validator, 'validate') as mock_values_validate:
        executor.execute()
        mock_validate.assert_called_once()
        mock_length_validate.assert_called_once()
        mock_values_validate.assert_called_once()


def test_execute_add_transaction(command_executor, args):
    args.add_transaction = True
    executor, transaction_appender_mock = command_executor
    executor.execute()
    transaction_appender_mock.append_transaction.assert_called_once_with(args.amount, args.currency)


def test_execute_edit_field_value(command_executor, args):
    args.new_value = "new_value"
    executor, _ = command_executor
    with patch.object(executor.field_editor, 'edit_field_value') as mock_edit:
        executor.execute()
        mock_edit.assert_called_once_with(
            record_type=args.record_type,
            field_name=args.field,
            transaction_index=args.transaction_counter,
            new_value=args.new_value,
        )


def test_execute_retrieve_field(command_executor, args):
    args.new_value = None
    executor, _ = command_executor
    with patch.object(executor.field_retriever, 'retrieve') as mock_retrieve:
        executor.execute()
        mock_retrieve.assert_called_once_with(
            record_type=args.record_type,
            field_name=args.field,
            transaction_index=args.transaction_counter,
        )


def test_execute_block_field_from_changes(command_executor, args):
    args.block_field_from_changes = "date"
    executor, _ = command_executor
    with patch.object(executor.immutable_field_setter, 'make_field_immutable') as mock_block:
        executor.execute()
        mock_block.assert_called_once_with(args.block_field_from_changes)


def test_execute_unblock_field_from_changes(command_executor, args):
    args.unblock_field_from_changes = "date"
    executor, _ = command_executor
    with patch.object(executor.immutable_field_setter, 'make_field_mutable') as mock_unblock:
        executor.execute()
        mock_unblock.assert_called_once_with(args.unblock_field_from_changes)
