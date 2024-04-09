import logging

from fixed_width_struct_io.constants import (
    FIELD_LENGTHS,
    TRANSACTION_ID,
    LAST_TRANSACTION_LIST_INDEX,
    FIELD_FORMATS,
    TRANSACTION,
    FOOTER_ID,
)
from fixed_width_struct_io.core import FileIOBase
from fixed_width_struct_io.utils import validate_field


logger = logging.getLogger(__name__)


class TransactionAppender(FileIOBase):
    """
    Appends a new transaction to a fixed-width file
    and updates the footer accordingly.
    """

    def _extract_fields(self, line: str, field_sizes: dict) -> dict:
        """
        Extracts fields from a line based on defined sizes.
        Args:
            line (str): The line from which to extract fields.
            field_sizes (dict): A dictionary mapping
                                field names to their sizes.
        Returns:
            dict: A dictionary of field names to their values.
        """
        fields = dict()
        substrings = line.split(",")

        for field_index, field_name in enumerate(field_sizes.keys()):
            fields[field_name] = substrings[field_index]
        return fields

    def _validate_new_transaction_fields(
        self, amount: str, currency: str
    ) -> bool:
        """
        Validates the amount and currency of a new transaction.
        Args:
            amount (str): The transaction amount to validate.
            currency (str): The transaction currency to validate.
        Returns:
            bool: True if both amount and currency are valid, False otherwise.
        Raises:
            ValueError: If amount or currency validation fails.
        """
        try:
            logger.info("Started fields validation for the new transaction.")
            is_amount_valid = validate_field(
                record_type=TRANSACTION,
                field_name="amount",
                field_value=amount,
            )
            is_currency_valid = validate_field(
                record_type=TRANSACTION,
                field_name="currency",
                field_value=currency,
            )
            if not (is_amount_valid and is_currency_valid):
                logger.error(
                    "Invalid transaction fields: amount "
                    "or currency is invalid."
                )
                return False
            logger.info(
                "Fields 'amount' and 'currency' for "
                "the new transaction are valid."
            )
            return True
        except Exception as e:
            logger.exception(
                f"Error validating new " f"transaction fields: {e}"
            )
            raise

    def append_transaction(self, amount: str, currency: str) -> bool:
        """
        Appends a new transaction to the file
        and updates the footer accordingly.
        Args:
            amount (str): The transaction amount.
            currency (str): The transaction currency.
        Returns:
            bool: True if the transaction was appended successfully,
             False otherwise.
        Raises:
            ValueError: If any step in appending the transaction fails.
        """
        try:
            if not self._validate_new_transaction_fields(amount, currency):
                logger.error("Failed to validate new transaction fields.")
                raise ValueError("Amount or currency is invalid")

                # Load all lines from the file
            with open(self.file_path, "r") as file:
                lines = file.readlines()

            footer_index = None
            for i, line in enumerate(self.lines):
                if line.startswith(FOOTER_ID):
                    footer_index = i
                    break

            if footer_index is None:
                logger.error("Footer not found in the file.")
                raise ValueError("Footer not found in the file.")

            new_counter = self._get_next_counter(self.lines[:footer_index])
            new_transaction_line = self._new_transaction(
                new_counter, amount, currency
            )

            lines.insert(footer_index, new_transaction_line)

            transaction_count_increment = 1
            amount_increment = (
                float(amount) / 100
            )  # assuming amount is in cents
            logging.info("Calculate new footer values")

            updated_footer_line = self._update_footer(
                lines[footer_index + 1],
                transaction_count_increment,
                amount_increment,
            )
            lines[footer_index + 1] = updated_footer_line

            with open(self.file_path, "w") as file:
                file.writelines(lines)
            logger.info("New transaction appended successfully.")
            return True
        except ValueError as e:
            logger.error(f"Failed to append new transaction: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error appending transaction: {e}")
            raise

    def _get_next_counter(self, lines_up_to_footer: list[str]) -> str:
        """
        Determines the next transaction counter
        based on the transactions present.
        Args:
            lines_up_to_footer (list[str]): The lines of the
                                            file up to the footer.
        Returns:
            str: The next transaction counter.
        Raises:
            ValueError: If no transactions are found before the footer.
        """
        try:
            last_transaction_line = None
            for line in reversed(lines_up_to_footer):
                if line.startswith(TRANSACTION_ID):
                    last_transaction_line = line
                    break

            if last_transaction_line is None:
                logger.error("No transactions found before the footer.")
                raise ValueError("No transactions found before the footer.")

            last_transaction_fields = self._extract_fields(
                line=self.lines[LAST_TRANSACTION_LIST_INDEX],
                field_sizes=FIELD_LENGTHS[TRANSACTION_ID],
            )
            counter = last_transaction_fields["counter"]
            new_counter_int = int(counter) + 1
            new_counter_str = str(new_counter_int).zfill(6)
            logger.info(
                f"Next transaction counter determined: {new_counter_str}."
            )
            return new_counter_str
        except Exception:
            logger.exception("Failed to calculate next transaction counter.")
            raise

    def _new_transaction(
        self, counter: str, amount: str, currency: str
    ) -> str:
        """
        Creates a new transaction line for the file.
        Args:
            counter (str): The transaction counter.
            amount (str): The transaction amount.
            currency (str): The currency of the transaction.
        Returns:
            str: The new transaction line.
        """
        logger.debug(
            f"Creating new transaction: Counter={counter}, "
            f"Amount={amount}, Currency={currency}."
        )

        reserved_field_format = FIELD_FORMATS[TRANSACTION_ID]["reserved"]
        reserved_spaces = " " * (
            reserved_field_format.end_position
            - reserved_field_format.start_position
            + 1
        )
        logger.info("New transaction line created successfully.")
        return (
            f"{TRANSACTION_ID},{counter},{amount},"
            f"{currency},{reserved_spaces}\n"
        )

    def _update_footer(
        self,
        footer_line: str,
        transaction_count_increment: int,
        amount_increment: float,
    ) -> str:
        """
        Updates the footer line with new transaction count and control sum.
        Args:
            footer_line (str): The current footer line.
            transaction_count_increment (int): The increment
                                            to the transaction count.
            amount_increment (float): The increment to the control sum.
        Returns:
            str: The updated footer line.
        Raises:
            Exception: If footer line update fails.
        """
        try:
            footer_fields = self._extract_fields(
                footer_line, FIELD_FORMATS[FOOTER_ID]
            )

            total_counter = (
                int(footer_fields["total counter"])
                + transaction_count_increment
            )
            footer_fields["total counter"] = str(total_counter).zfill(6)

            # Increment the control sum
            control_sum = int(footer_fields["control sum"]) + int(
                amount_increment * 100
            )  # assuming control sum is also in cents
            footer_fields["control sum"] = str(control_sum).zfill(12)

            # Reconstruct the footer line
            reserved_spaces = " " * (
                FIELD_FORMATS[FOOTER_ID]["reserved"].end_position
                - FIELD_FORMATS[FOOTER_ID]["reserved"].start_position
                + 1
            )
            logger.info("Footer updated successfully.")
            return (
                f"{FOOTER_ID},{footer_fields['total counter']},"
                f"{footer_fields['control sum']},{reserved_spaces}\n"
            )
        except Exception:
            logger.exception("Failed to update the footer.")
            raise
