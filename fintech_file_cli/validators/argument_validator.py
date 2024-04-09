import argparse
import logging

logger = logging.getLogger(__name__)


class ArgumentValidator:
    """
    Validates command-line arguments for the CLI application.

    This validator checks for mandatory arguments,
    exclusive use of certain flags, logical grouping and
    conflicts among provided flags, ensuring that provided
    arguments match the expected operations of the CLI.
    """

    def __init__(self, args: argparse.Namespace) -> None:
        """Initializes the ArgumentValidator with command-line arguments."""
        self.args = args

    def validate(self) -> None:
        """Performs validation on the provided command-line arguments."""
        self._validate_mandatory_file_path()
        self._validate_exclusive_field_blocking()
        self._validate_transaction_logic()
        self._validate_transaction_addition()
        self._validate_field_editing()
        self._validate_retrieve_logic()

    def _validate_mandatory_file_path(self) -> None:
        """
        Validates that --file-path is provided for
        operations that require a file.
        """
        if not self.args.file_path:
            if (
                self.args.block_field_from_changes
                or self.args.unblock_field_from_changes
            ):
                logger.info(
                    "--file-path is not required for "
                    "field blocking/unblocking."
                )
            else:
                logger.error("The --file-path argument is mandatory.")
                raise ValueError("The --file-path argument is mandatory.")

    def _validate_exclusive_field_blocking(self) -> None:
        if (
            self.args.block_field_from_changes
            or self.args.unblock_field_from_changes
        ):
            for arg in vars(self.args):
                if getattr(self.args, arg) not in [
                    None,
                    False,
                ] and arg not in [
                    "block_field_from_changes",
                    "unblock_field_from_changes",
                    "log",
                ]:
                    logger.error(
                        "--block-field-from-changes and --unblock-field-from"
                        "-changes must be used exclusively without other"
                        " flags except of --log flag."
                    )
                    raise ValueError(
                        "--block-field-from-changes and "
                        "--unblock-field-from-changes"
                        " must be used exclusively without"
                        " other flags except of --log flag."
                    )

    def _validate_transaction_logic(self) -> None:
        """
        Validates the logic related to transaction actions,
         ensuring correct flag usage.
        """
        try:
            if (
                self.args.record_type
                and self.args.record_type.lower() == "transaction"
                and not self.args.transaction_counter
            ):
                raise ValueError(
                    "--transaction-counter is required when "
                    "--record-type is 'transaction'."
                )

            if self.args.transaction_counter and (
                not self.args.record_type
                or self.args.record_type.lower() != "transaction"
            ):
                raise ValueError(
                    "--transaction-counter can only be used when"
                    " --record-type is 'transaction'."
                )

            if self.args.transaction_counter and not self.args.record_type:
                raise ValueError(
                    "--record-type must be specified and set to"
                    " 'transaction' when using --transaction-counter."
                )

            if self.args.transaction_counter and not self.args.field:
                raise ValueError(
                    "--field must be specified and set to "
                    "'transaction' when using --transaction-counter."
                )
            logger.debug("Transaction logic validated successfully.")
        except ValueError as e:
            logger.error(f"Transaction logic validation error: {e}")
            raise

    def _validate_transaction_addition(self) -> None:
        """
        Validates the logic for adding a new transaction,
        ensuring required flags are present and no conflicting flags are used.
        """
        try:
            if self.args.add_transaction:
                if not (self.args.amount and self.args.currency):
                    raise ValueError(
                        "--amount and --currency are required"
                        " when adding a new transaction."
                    )
                if not self.args.file_path:
                    raise ValueError(
                        "--file-path is required when "
                        "--add-transaction is used."
                    )
                conflicting_args = [
                    "record_type",
                    "field",
                    "new_value",
                    "block_field_from_changes",
                    "transaction_counter",
                    "unblock_field_from_changes",
                ]
                conflicts = [
                    arg
                    for arg in conflicting_args
                    if getattr(self.args, arg) not in [None, False]
                ]
                if conflicts:
                    formatted_conflicts = self._format_arg_names(conflicts)
                    raise ValueError(
                        f"Cannot combine --add-transaction with"
                        f" other operation flags: {formatted_conflicts}."
                    )

            if self.args.amount or self.args.currency:
                conflicting_args = [
                    "record_type",
                    "field",
                    "new_value",
                    "block_field_from_changes",
                    "transaction_counter",
                    "unblock_field_from_changes",
                ]
                conflicts = [
                    arg
                    for arg in conflicting_args
                    if getattr(self.args, arg) not in [None, False]
                ]
                if conflicts:
                    formatted_conflicts = self._format_arg_names(conflicts)
                    raise ValueError(
                        f"Cannot combine --amount or --currency"
                        f" with other operation flags: {formatted_conflicts}."
                    )
                if not self.args.add_transaction:
                    raise ValueError(
                        "--add-transaction is required when using"
                        " --amount and --currency."
                    )
            logger.debug("Transaction addition logic validated successfully.")
        except ValueError as e:
            logger.error(f"Transaction addition validation error: {e}")
            raise

    def _format_arg_names(self, arg_names: list) -> str:
        """Converts argument names from snake_case to --flag-format."""
        return ", ".join([f"--{arg.replace('_', '-')}" for arg in arg_names])

    def _validate_field_editing(self) -> None:
        """
        Validates the logic for editing a field value,
         ensuring required flags are present and no conflicting flags are used.
        """
        try:
            if self.args.new_value:
                required_args = ["file_path", "record_type", "field"]
                for arg in required_args:
                    if not getattr(self.args, arg):
                        raise ValueError(
                            f"--{arg.replace('_', '-')} is required "
                            f"when using --new-value."
                        )
                if (
                    self.args.add_transaction
                    or self.args.amount
                    or self.args.currency
                    or self.args.block_field_from_changes
                    or self.args.unblock_field_from_changes
                ):
                    raise ValueError(
                        "--new-value cannot be combined with "
                        "transaction addition or field blocking/unblocking."
                    )
                logger.debug("Field editing logic validated successfully.")
        except ValueError as e:
            logger.error(f"Field editing validation error: {e}")
            raise

    def _validate_retrieve_logic(self) -> None:
        """
        Validates the logic for retrieving field values,
         ensuring that necessary flags are present.
        """
        try:
            if self.args.field:
                if not self.args.record_type:
                    raise ValueError(
                        "--record-type is required when --field is specified."
                    )
            if self.args.record_type:
                if not self.args.field:
                    raise ValueError(
                        "--field is required when --record-type is specified."
                    )
            logger.debug("Retrieve logic validated successfully.")
        except ValueError as e:
            logger.error(f"Retrieve logic validation error: {e}")
            raise
