import logging
from typing import Any, Optional

from fixed_width_struct_io.constants import (
    FIELD_LENGTHS,
    FOOTER,
    FOOTER_ID,
    HEADER,
    HEADER_ID,
    RECORD_TYPES,
    TRANSACTION,
    TRANSACTION_ID,
)
from fixed_width_struct_io.readers.base import BaseRetriever


logger = logging.getLogger(__name__)


class FieldRetriever(BaseRetriever):
    """
    Concrete class for retrieving fields from a fixed-width
    file based on record type and field name.
    """

    def retrieve(
        self,
        record_type: str,
        field_name: str,
        transaction_index: Optional[str] = None,
    ) -> Any:
        """
        Retrieves the value of a specified field from a fixed-width file.
        Args:
            record_type: The type of records
                        (e.g., HEADER, TRANSACTION, FOOTER).
            field_name: The name of the field to retrieve.
            transaction_index: The index of the transaction
                                to retrieve (if applicable).
        Returns:
            The value of the specified field.
        Raises:
            ValueError: If record_type or field_name is
             invalid or if the specified field is not found.
        """
        try:
            field_name = field_name.lower()

            if record_type.lower() not in RECORD_TYPES:
                raise ValueError(f"Invalid record type: {record_type}")

            if (
                field_name
                not in FIELD_LENGTHS[RECORD_TYPES[record_type.lower()]]
            ):
                raise ValueError(
                    f"{record_type.capitalize()} record "
                    f"doesn't have field '{field_name}'"
                )

            # Process file lines once, collecting required information.
            header_values, transaction_values, footer_values = (
                self._process_file_lines()
            )
            if record_type == HEADER:
                if header_values is None:
                    raise ValueError("Header not found.")
                return_value = header_values.get(field_name)
                logger.info(f"{field_name} for header is '{return_value}'.")
                print(f"'{return_value}'")
                return return_value

            elif record_type == TRANSACTION:
                if transaction_index is not None:
                    if (
                        int(transaction_index) > len(transaction_values)
                        or int(transaction_index) < 1
                    ):
                        raise ValueError(
                            f"Transaction not found for the "
                            f"specified counter '{transaction_index}'."
                        )
                    return_value = transaction_values[
                        int(transaction_index) - 1
                    ].get(field_name)
                    logger.info(
                        f"{field_name} for transaction with "
                        f"transaction_index={transaction_index}"
                        f" is '{return_value}'."
                    )
                    print(f"'{return_value}'")
                    return return_value
                raise ValueError(
                    "Transaction counter must be provided "
                    "for transaction records."
                )

            elif record_type == FOOTER:
                if footer_values is None:
                    raise ValueError("Footer not found.")
                return_value = footer_values.get(field_name)
                logger.info(f"{field_name} for footer is '{return_value}'.")
                print(f"'{return_value}'")
                return return_value

        except ValueError as e:
            logger.error(e)
            raise

    def _process_file_lines(self) -> tuple:
        """
        Processes lines from the fixed-width file and categorizes
         them by record type.
        Returns:
            A tuple containing dictionaries of values for
            headers, transactions, and footers.
        """
        try:
            header_values, footer_values, transaction_values = None, None, []
            current_transaction = 0
            for line in self.lines:
                if line.startswith(HEADER_ID):
                    header_values = self._extract_fields(
                        line, FIELD_LENGTHS[HEADER_ID]
                    )
                elif line.startswith(TRANSACTION_ID):
                    current_transaction += 1
                    transaction_fields = self._extract_fields(
                        line, FIELD_LENGTHS[TRANSACTION_ID]
                    )
                    transaction_values.append(transaction_fields)

                elif line.startswith(FOOTER_ID):
                    footer_values = self._extract_fields(
                        line, FIELD_LENGTHS[FOOTER_ID]
                    )

            return header_values, transaction_values, footer_values

        except Exception as e:
            logger.exception(f"Failed to process file lines: {e}")
            raise

    def _extract_fields(self, line: str, field_sizes: dict) -> dict:
        """
        Extracts fields from a line based on the provided field sizes.
        Args:
            line: A single line from the fixed-width file.
            field_sizes: A dictionary mapping field names
                        to their start and end positions.
        Returns:
            A dictionary of field values extracted from the line.
        """
        fields = dict()
        try:
            substrings = line.split(",")

            for field_index, field_name in enumerate(field_sizes.keys()):
                fields[field_name] = substrings[field_index]
            return fields
        except Exception as e:
            logger.exception(f"Failed to extract fields from line: {e}")
            raise
