import argparse
import logging

from fixed_width_struct_io.access_control.immutable_field_setter import (
    ImmutableFieldSetter,
)
from fixed_width_struct_io.readers import FieldRetriever
from fixed_width_struct_io.validators import (
    FileStructureValidator,
    StringLengthValidator,
)
from fixed_width_struct_io.validators.values_validator import ValuesValidator
from fixed_width_struct_io.writers import FieldEditor, TransactionAppender

logger = logging.getLogger(__name__)


class CommandExecutor:
    """
    Executes commands based on the parsed arguments for the CLI.

    Attributes:
        args: Parsed command-line arguments.
        file_path: Path to the file.
        file_structure_validator: Validator for the file structure.
        length_validator: Validator for the length of file content.
        values_validator: Validator for the values within the file.
        field_retriever: Utility to retrieve field values.
        field_editor: Utility to edit field values.
        transaction_appender: Utility to append transactions.
        immutable_field_setter: Utility to change field immutability.
    """

    def __init__(
        self,
        args: argparse.Namespace,
        file_structure_validator: FileStructureValidator,
        length_validator: StringLengthValidator,
        values_validator: ValuesValidator,
        field_retriever: FieldRetriever,
        field_editor: FieldEditor,
        transaction_appender: TransactionAppender,
        immutable_field_setter: ImmutableFieldSetter,
    ) -> None:
        """Initializes the CommandExecutor with the necessary
        validators and utilities."""
        self.args = args
        self.file_structure_validator = file_structure_validator
        self.length_validator = length_validator
        self.values_validator = values_validator
        self.field_retriever = field_retriever
        self.field_editor = field_editor
        self.transaction_appender = transaction_appender
        self.immutable_field_setter = immutable_field_setter

    def execute(self) -> None:
        """Executes the appropriate actions based on the provided arguments."""
        try:
            if self.args.file_path:
                self._handle_file_path_actions()

            if self.args.block_field_from_changes:
                self.immutable_field_setter.make_field_immutable(
                    self.args.block_field_from_changes
                )
                logger.info(
                    f"Field {self.args.block_field_from_changes}"
                    f" is now immutable."
                )

            if self.args.unblock_field_from_changes:
                self.immutable_field_setter.make_field_mutable(
                    self.args.unblock_field_from_changes
                )
                logger.info(
                    f"Field {self.args.unblock_field_from_changes}"
                    f" is now mutable."
                )
        except Exception as e:
            logger.error(f"An error occurred during command execution: {e}")
            raise

    def _handle_file_path_actions(self) -> None:
        """Handles actions that require the file path argument."""
        try:
            if self.args.validate:
                self._validate_file()

            if self.args.add_transaction:
                self._add_transaction()

            if self.args.new_value is not None:
                self._edit_field_value()

            # Run validations if no specific action is triggered
            if (
                not self.args.add_transaction
                and self.args.new_value is None
                and self.args.record_type
                and self.args.field
            ):
                self._retrieve_field()
        except Exception as e:
            logger.error(f"Error handling file path actions: {e}")
            raise

    def _validate_file(self) -> None:
        """Validates the structure, length, and values of the file."""
        try:
            logger.info("Validating file structure, length, and values.")
            self.file_structure_validator.validate()
            self.length_validator.validate()
            self.values_validator.validate()
            logging.info("File is valid.")
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise

    def _add_transaction(self) -> None:
        """Appends a new transaction to the file."""
        try:
            logger.info("Appending a new transaction.")
            self.transaction_appender.append_transaction(
                self.args.amount, self.args.currency
            )
            logger.info("Transaction successfully appended.")
        except Exception as e:
            logger.error(f"Failed to append transaction: {e}")
            raise

    def _edit_field_value(self) -> None:
        """Edits a field value within the file."""
        try:
            logger.info(
                f"Editing field '{self.args.field}' "
                f"with new value '{self.args.new_value}'."
            )
            self.field_editor.edit_field_value(
                record_type=self.args.record_type,
                field_name=self.args.field,
                transaction_index=self.args.transaction_counter,
                new_value=self.args.new_value,
            )
            logger.info(
                f"Field '{self.args.field}' edited successfully"
                f" with value '{self.args.new_value}'."
            )
        except Exception as e:
            logger.error(f"Failed to edit field value: {e}")
            raise

    def _retrieve_field(self) -> None:
        """Retrieves a field value from the file."""
        try:
            logger.info(f"Retrieving field '{self.args.field}'.")
            value = self.field_retriever.retrieve(
                record_type=self.args.record_type,
                field_name=self.args.field,
                transaction_index=self.args.transaction_counter,
            )
            logger.info(f"Retrieved value for '{self.args.field}': {value}")
        except Exception as e:
            logger.error(f"Failed to retrieve field value: {e}")
            raise
