import logging

from fixed_width_struct_io.constants import (
    FIELD_ID_LENGTH,
    MAX_TRANSACTIONS_AMOUNT,
    RECORD_TYPES,
)
from fixed_width_struct_io.validators.base import BaseValidator

logger = logging.getLogger(__name__)


class FileStructureValidator(BaseValidator):
    """
    Validates the structure of a fixed-width file including headers, footers,
    and transactions according to predefined rules.
    """

    def validate(self) -> bool:
        """
        Validates the fixed-width file's structure.
        Returns:
            True if all structural validations pass.
        Raises:
            ValueError: If any structural validations fail.
        """
        try:
            self._validate_record_types(self.lines)
            self._validate_structure(self.lines)

            transaction_lines = [
                line
                for line in self.lines[1:-1]
                if line.startswith(RECORD_TYPES["transaction"])
            ]

            self._validate_transaction_limit(transaction_lines)
            self._validate_transactions(transaction_lines)
            logger.info(" ===== File structure successfully validated. ===== ")
            return True
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            raise

    def _validate_transaction_limit(self, transaction_lines: list) -> None:
        """
        Validates that the number of transaction records
        does not exceed the maximum allowed.
        Args:
            transaction_lines: A list of transaction lines to be validated.
        Raises:
            ValueError: If the number of transactions exceeds
            MAX_TRANSACTIONS_AMOUNT.
        """
        if len(transaction_lines) > MAX_TRANSACTIONS_AMOUNT:
            error_message = (
                f"The number of transactions exceeds the limit of 20,000."
                f" You have {len(transaction_lines)}"
            )
            logger.error(error_message)
            raise ValueError(error_message)
        logger.info("Transactions count is in valid range.")

    def _validate_record_types(self, lines: list) -> None:
        """
        Validates that all lines in the file start
        with a valid record type identifier.
        Args:
            lines: A list of all lines in the file to be validated.
        Raises:
            ValueError: If any lines start with an invalid
             record type identifier.
        """
        invalid_lines = [
            i
            for i, line in enumerate(lines, start=1)
            if line[:FIELD_ID_LENGTH] not in RECORD_TYPES.values()
        ]
        if invalid_lines:
            error_message = (
                f"Unknown record type found"
                f" on line(s): {', '.join(map(str, invalid_lines))}."
            )
            logger.error(error_message)
            raise ValueError(error_message)
        logger.info("No unknown record types found.")

    def _validate_structure(self, lines: list) -> None:
        """
        Validates the file structure including the presence
         and placement of headers and footers.
        Args:
            lines: A list of all lines in the file to be validated.
        Raises:
            ValueError: If headers or footers are missing or misplaced.
        """
        try:
            self._validate_header_footer_presence(lines=lines)
            self._validate_no_extra_headers_footers(lines=lines)
        except ValueError as e:
            logger.error(f"Structure validation error: {e}")
            raise

    def _validate_header_footer_presence(self, lines: list) -> None:
        """
        Validates the presence of a header at the beginning
         and a footer at the end of the file.
        Args:
            lines: A list of all lines in the file.
        Raises:
            ValueError: If the first line is not a header or
            the last line is not a footer.
        """
        if not lines[0].startswith(RECORD_TYPES["header"]):
            raise ValueError("The first line must be a header.")
        if not lines[-1].startswith(RECORD_TYPES["footer"]):
            raise ValueError("The last line must be a footer.")
        logger.info(
            "File containing headers and footers validated successfully."
        )

    def _validate_no_extra_headers_footers(self, lines: list) -> None:
        """
        Validates that there are no extra headers or footers within the file.
        Args:
            lines: A list of all lines in the file.
        Raises:
            ValueError: If extra headers or footers are found.
        """
        extra_headers = [
            i
            for i, line in enumerate(lines[1:], start=2)
            if line.startswith(RECORD_TYPES["header"])
        ]
        extra_footers = [
            i
            for i, line in enumerate(lines[:-1], start=1)
            if line.startswith(RECORD_TYPES["footer"])
        ]

        if extra_headers:
            raise ValueError(
                f"Extra header(s) found at line(s):"
                f" {', '.join(map(str, extra_headers))}."
            )
        if extra_footers:
            raise ValueError(
                f"Extra footer(s) found at line(s):"
                f" {', '.join(map(str, extra_footers))}."
            )
        logger.info("No extra headers or footers found.")

    def _validate_transactions(self, transaction_lines: list) -> None:
        """
        Validates that each transaction line in the provided
        list starts with the correct transaction record type.
        Args:
            transaction_lines (list): A list of transaction
                            lines extracted from the file to be validated.
        Raises:
            ValueError: If any transaction lines do not
             start with the correct transaction record type.
        """
        try:
            invalid_transactions = [
                i
                for i, line in enumerate(transaction_lines, start=2)
                if not line.startswith(RECORD_TYPES["transaction"])
            ]
            if invalid_transactions:
                error_message = (
                    f"Invalid transaction record type on line(s): "
                    f"{', '.join(map(str, invalid_transactions))}."
                )
                logger.error(error_message)
                raise ValueError(error_message)
            else:
                logger.info("All transactions validated successfully.")

        except ValueError as e:
            logger.exception("Error during transaction validation.")
            raise e
