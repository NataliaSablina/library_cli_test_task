import logging
from typing import Any

from fixed_width_struct_io.access_control import immutable_field_setter
from fixed_width_struct_io.constants import (
    RECORD_TYPES,
    FIELD_LENGTHS,
    HEADER_ID,
    FOOTER_ID,
    TRANSACTION_ID,
    FIELD_ID_LENGTH,
    FIELD_FORMATS,
    HEADER,
    FOOTER,
    TRANSACTION,
)
from fixed_width_struct_io.core import FileIOBase
from fixed_width_struct_io.utils import validate_field


logger = logging.getLogger(__name__)


class FieldEditor(FileIOBase):
    """
    Provides functionalities to edit field values in fixed-width file records,
    including header, transaction, and footer records.
    """

    def _extract_fields(self, line: str, field_sizes: dict) -> dict:
        """
        Extracts fields from a line based on provided field sizes.
        Args:
            line (str): The line from which to extract fields.
            field_sizes (dict): A dictionary specifying the sizes of fields.
        Returns:
            dict: A dictionary of field names and their corresponding values.
        """
        fields = dict()
        try:
            substrings = line.split(",")

            for field_index, field_name in enumerate(field_sizes.keys()):
                fields[field_name] = substrings[field_index]
        except Exception as e:
            logger.error(f"Failed to extract fields from line: {e}")
            raise
        return fields

    def _validate_new_value(
        self, record_type: str, field_name: str, new_value: Any
    ) -> bool:
        """
        Validates the new value for a given field against predefined criteria.
        Args:
            record_type (str): The type of record
                                (e.g., HEADER, FOOTER, TRANSACTION).
            field_name (str): The name of the field to validate.
            new_value (Any): The new value to be validated.
        Returns:
            bool: True if the new value is valid, False otherwise.
        Raises:
            ValueError: If record type or field name is invalid.
        """
        field_name = field_name.lower()
        try:
            if record_type.lower() not in RECORD_TYPES:
                raise ValueError(f"Invalid record type: {record_type}")

            if (
                field_name
                not in FIELD_LENGTHS[RECORD_TYPES[record_type.lower()]]
            ):
                raise ValueError(
                    f"{record_type.capitalize()} record doesn't"
                    f" have field '{field_name}'"
                )

            if validate_field(
                record_type=record_type,
                field_name=field_name,
                field_value=new_value,
            ):
                logger.info("New field value is validated successfully")
                return True
            logger.error(
                f"Invalid value '{new_value}' for field "
                f"'{field_name}' in record type '{record_type}'."
            )
            return False
        except ValueError as e:
            logger.error(
                f"Validation error for new value in _validate_new_value: {e}"
            )
            raise

    def _calculate_new_control_sum(self, updated_lines: list[str]) -> str:
        """
        Calculates a new control sum based on updated lines.
        Args:
            updated_lines (list[str]): A list of updated lines.
        Returns:
            str: The new control sum.
        """
        new_control_sum_int = 0
        try:
            for line in updated_lines:
                if line[:FIELD_ID_LENGTH] == TRANSACTION_ID:
                    transaction_fields = dict(
                        zip(
                            FIELD_FORMATS[TRANSACTION_ID].keys(),
                            line.split(","),
                        )
                    )
                    new_control_sum_int += int(transaction_fields["amount"])
            new_control_sum = str(new_control_sum_int).zfill(12)
            logger.debug(
                "Calculation of the new control sum "
                "for footer is finished successfully."
            )
            return new_control_sum
        except Exception as e:
            logger.error(f"Failed to calculate new control sum: {e}")
            raise

    def edit_field_value(
        self,
        record_type: str,
        field_name: str,
        transaction_index: str | int,
        new_value: Any,
    ) -> bool:
        """
        Edits the value of a specified field in a record.
        Args:
            record_type (str): The type of record to edit
                                (HEADER, FOOTER, TRANSACTION).
            field_name (str): The name of the field to edit.
            transaction_index (str | int): The index of the transaction
                                        to edit (for TRANSACTION records).
            new_value (Any): The new value to set for the field.
        Returns:
            bool: True if the field value was successfully edited,
             False otherwise.
        Raises:
            ValueError: If the field is immutable or the new value is invalid.
        """
        if immutable_field_setter.is_field_immutable(field_name):
            logger.error(f"Attempt to edit immutable field '{field_name}'.")
            raise ValueError(f"Field '{field_name}' is immutable.")
        field_name = field_name.lower()
        try:
            if self._validate_new_value(
                record_type=record_type,
                field_name=field_name,
                new_value=new_value,
            ):
                updated_lines = []

                for line in self.lines:
                    if (
                        line.startswith(HEADER_ID)
                        and record_type.lower() == HEADER
                    ) or (
                        line.startswith(FOOTER_ID)
                        and record_type.lower() == FOOTER
                    ):
                        fields = self._extract_fields(
                            line,
                            field_sizes=FIELD_LENGTHS[
                                RECORD_TYPES[record_type.lower()]
                            ],
                        )
                        fields[field_name] = new_value
                        updated_line = ",".join(
                            [
                                fields[field]
                                for field in FIELD_LENGTHS[
                                    RECORD_TYPES[record_type.lower()]
                                ].keys()
                            ]
                        )
                        updated_lines.append(updated_line + "\n")

                    elif line.startswith(HEADER_ID) or line.startswith(
                        FOOTER_ID
                    ):
                        if (
                            record_type.lower() == TRANSACTION
                            and field_name.lower() == "amount"
                            and line.startswith(FOOTER_ID)
                        ):
                            new_control_sum = self._calculate_new_control_sum(
                                updated_lines
                            )
                            footer_fields = self._extract_fields(
                                line, field_sizes=FIELD_LENGTHS[FOOTER_ID]
                            )
                            footer_fields["control sum"] = new_control_sum
                            updated_line = ",".join(
                                [
                                    footer_fields[field]
                                    for field in FIELD_LENGTHS[
                                        FOOTER_ID
                                    ].keys()
                                ]
                            )
                            updated_lines.append(updated_line + "\n")

                        else:
                            updated_lines.append(line + "\n")
                    elif (
                        line.startswith(TRANSACTION_ID)
                        and record_type.lower() == TRANSACTION
                    ):
                        if transaction_index is not None:
                            current_transaction = self._extract_fields(
                                line, FIELD_LENGTHS[TRANSACTION_ID]
                            )
                            if (
                                current_transaction.get("counter", -1)
                                == transaction_index
                            ):
                                current_transaction[field_name] = new_value
                                updated_line = ",".join(
                                    [
                                        current_transaction[field]
                                        for field in FIELD_LENGTHS[
                                            TRANSACTION_ID
                                        ].keys()
                                    ]
                                )
                                updated_lines.append(updated_line + "\n")
                                continue
                            else:
                                updated_lines.append(line + "\n")

                    elif line.startswith(TRANSACTION_ID):
                        updated_lines.append(line + "\n")

                with open(self.file_path, "w") as file:
                    file.writelines(updated_lines)
                logger.info(
                    f"Field '{field_name}' in record type "
                    f"'{record_type}' successfully edited."
                )
                return True
            else:
                raise ValueError(
                    f"New value '{new_value}' for the field"
                    f" '{field_name}' is invalid."
                )
        except Exception as e:
            logger.error(f"Failed to edit field value: {e}")
            raise
