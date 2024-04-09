import logging
from typing import Any, Optional

from fixed_width_struct_io.constants import (
    FIELD_ID_LENGTH,
    FIELD_LENGTHS,
    FIELD_ORDER,
    LINE_LENGTH,
)
from fixed_width_struct_io.validators.base import BaseValidator


logger = logging.getLogger(__name__)


class StringLengthValidator(BaseValidator):
    """
    Validates string lengths and field orders within
     lines of a fixed-width file.
    """

    def validate_record_type(
        self, record_type: str, line_number: Optional[int] = None
    ) -> None:
        """
        Validates the record type exists in the FIELD_LENGTHS mapping.
        Args:
            record_type: The record type to validate.
            line_number: Optional line number for logging.
        Raises:
            ValueError: If the record type is unknown.
        """
        if record_type not in FIELD_LENGTHS:
            error_message = f"Unknown record type: {record_type}."
            if line_number is not None:
                error_message += f" Found on line {line_number}."
            logger.error(error_message)
            raise ValueError(error_message)

    def validate_field_order(
        self, record_type: str, line_number: Optional[int] = None
    ) -> None:
        """
        Validates that the record_type exists in the FIELD_ORDER mapping.
        """
        if record_type not in FIELD_ORDER:
            error_message = (
                f"No field order defined for "
                f"record type: {record_type} on line {line_number}."
            )
            logger.error(error_message)
            raise ValueError(error_message)

    def validate_fields_count(
        self,
        fields: list,
        ordered_field_names: list,
        record_type: str,
        line_number: Optional[int] = None,
    ) -> None:
        """
        Validates the number of fields matches the expected count
        for the given record type.
        Args:
            fields: The list of fields to validate.
            ordered_field_names: The list of ordered field names
                                for validation.
            record_type: The record type to validate.
            line_number: Optional line number for logging.
        Raises:
            ValueError: If the number of fields does not match
             the expected count.
        """
        if len(fields) != len(ordered_field_names):
            if line_number is not None:
                error_message = (
                    f"Line {line_number} does not have the correct number "
                    f"of fields for record type: {record_type}."
                )
                logger.error(error_message)
                raise ValueError(error_message)
            else:
                error_message = (
                    f"Line does not have the correct number "
                    f"of fields for record type: {record_type}."
                )
                logger.error(error_message)
                raise ValueError(error_message)

    @staticmethod
    def validate_individual_field_length(
        record_type: str,
        field_name: str,
        field_value: Any,
        line_number: Optional[int] = None,
    ) -> bool:
        """
        Validates the length of an individual field according
         to its specification.
        Args:
            record_type: The record type to validate.
            field_name: The field name to validate.
            field_value: The field value to validate.
            line_number: Optional line number for logging.
        Returns:
            True if the field length is as expected.
        Raises:
            ValueError: If the field length does not match
            the expected length.
        """
        logger.debug(
            f"Validating field length for field {field_name} "
            f"with value={field_value } and record type "
            f"{record_type} is started."
        )
        try:
            if field_name.lower() not in FIELD_LENGTHS[record_type]:
                error_message = (
                    f"Unknown field name: "
                    f"'{field_name}' for record type: {record_type}."
                )
                if line_number is not None:
                    error_message += f" Found on line {line_number}."
                    logger.error(error_message)
                logger.error(error_message)
                raise ValueError(error_message)

            field_spec = FIELD_LENGTHS[record_type][field_name]
            expected_length = (
                field_spec.end_position - field_spec.start_position + 1
            )
            actual_length = len(field_value)

            if actual_length != expected_length:
                error_message = (
                    f"Field '{field_name}' has incorrect length. "
                    f"Expected {expected_length}, "
                    f"found {actual_length}."
                )
                if line_number is not None:
                    error_message += f" Error found on line {line_number}."
                    logger.error(error_message)
                logger.error(error_message)
                raise ValueError(error_message)
            logger.debug(
                f"Validating field length for field {field_name} "
                f"with value={field_value} and record type "
                f"{record_type} is successfully finished."
            )
            return True
        except KeyError as e:
            logger.error(
                f"Validation error for '{field_name}' "
                f"on line {line_number}: {e}"
            )
            raise ValueError(
                f"Unknown field '{field_name}' "
                f"for record type '{record_type}'."
            ) from e

    def validate_total_line_length(
        self, line: str, line_number: Optional[int] = None
    ) -> None:
        """
        Validates the total length of all field values in
        a line matches the expected LINE_LENGTH.
        """
        logger.debug(f"Validate total line length for line '{line}'.")
        total_value_length = sum(len(value) for value in line.split(","))
        if total_value_length != LINE_LENGTH:
            error_msg = (
                f"Total length of field values does not match "
                f"the expected length. Found {total_value_length}, "
                f"expected {LINE_LENGTH}."
            )
            if line_number:
                error_msg += f" Error found on line {line_number}."
                logger.error(error_msg)
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.debug(
            f"Total line length validation for line '{line}' is finished."
        )

    def validate_line(
        self, line: str, line_number: Optional[int] = None
    ) -> bool:
        """
        Validates a single line from the fixed-width file,
        including record type, field order, and field lengths.
        Args:
            line: The line to validate.
            line_number: The line number for context.
        Returns:
            True if all validations pass for the line.
        Raises:
            ValueError: If any validation fails.
        """
        try:
            record_type = line[:FIELD_ID_LENGTH]

            self.validate_record_type(record_type, line_number)
            self.validate_field_order(record_type, line_number)

            fields = line.split(",")

            ordered_field_names = FIELD_ORDER[record_type]
            self.validate_fields_count(
                fields, ordered_field_names, record_type, line_number
            )

            for field_name, field_value in zip(ordered_field_names, fields):
                StringLengthValidator.validate_individual_field_length(
                    record_type, field_name, field_value, line_number
                )

            self.validate_total_line_length(line, line_number)

            info_message = (
                "The length of line and its " "fields is as expected."
            )
            if line_number:
                info_message += f" Line number {line_number}."
            logger.debug(info_message)
            return True
        except ValueError as e:
            logger.error(f"Line {line_number} validation error: {e}")
            raise

    def validate(self) -> bool:
        """
        Validates the entire fixed-width file against
        the string length and field order rules.
        Returns:
            True if the file passes all validations.
        Raises:
            ValueError: If any line in the file fails validation.
        """
        try:
            for line_number, line in enumerate(self.lines, start=1):
                self.validate_line(line, line_number)
            logger.info(
                "===== All lines and their fields in the file passed "
                "length validation. ====="
            )
            return True
        except ValueError as e:
            logger.error(f"File validation error: {e}")
            raise
