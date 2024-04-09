import logging
import re
from typing import Any, Optional

from fixed_width_struct_io.constants import (
    CURRENCIES_LIST,
    FIELD_FORMATS,
    FIELD_ID_LENGTH,
    FOOTER_ID,
    HEADER_ID,
    RECORD_TYPE_NAMES,
    TRANSACTION_ID,
)
from fixed_width_struct_io.validators.base import BaseValidator


logger = logging.getLogger(__name__)


class ValuesValidator(BaseValidator):
    """
    Validates values within records of a fixed-width
    file based on predefined formats.
    """

    @staticmethod
    def validate_field(
        record_type: str,
        field_name: str,
        field_value: Any,
        line_number: Optional[int] = None,
    ) -> bool:
        """
        Validates a field's value according to its expected
         data type, length, and format.
        Args:
            record_type: The type of record (header, transaction, footer).
            field_name: Name of the field being validated.
            field_value: Actual value of the field to validate.
            line_number: Line number for logging context.
        Returns:
            True if the field value passes all validation criteria.
        Raises:
            ValueError: If any validation criterion is not met.
        """
        try:
            field_spec = FIELD_FORMATS[record_type][field_name.lower()]
            expected_type = field_spec.data_type

            if not isinstance(field_value, expected_type):
                record_type_name = RECORD_TYPE_NAMES.get(
                    record_type, record_type
                )
                error_message = (
                    f"Field '{field_name}' in record type "
                    f"'{record_type_name}' expects "
                    f"data type {expected_type}."
                )
                if line_number is not None:
                    error_message += f" Found on line {line_number}."
                raise ValueError(error_message)

            start_pos = field_spec.start_position
            end_pos = field_spec.end_position

            if len(field_value) != (end_pos - start_pos + 1):
                record_type_name = RECORD_TYPE_NAMES.get(
                    record_type, record_type
                )
                error_message = (
                    f"Field '{field_name}' in record type "
                    f"'{record_type_name}' should have "
                    f"length {end_pos - start_pos + 1}."
                )
                if line_number is not None:
                    error_message += f" Line {line_number}."
                raise ValueError(error_message)

            if field_spec.fixed_value is not None and field_value != str(
                field_spec.fixed_value
            ):
                record_type_name = RECORD_TYPE_NAMES.get(
                    record_type, record_type
                )
                error_message = (
                    f"Field '{field_name}' in record type "
                    f"'{record_type_name}' should have "
                    f"fixed value '{field_spec.fixed_value}'."
                )
                if line_number is not None:
                    error_message += f" Line {line_number}."
                raise ValueError(error_message)

            if (
                field_name == "currency"
                and field_value.lower() not in CURRENCIES_LIST
            ):
                record_type_name = RECORD_TYPE_NAMES.get(
                    record_type, record_type
                )
                error_message = (
                    f"Invalid currency value '{field_value}'"
                    f" in record type '{record_type_name}'."
                    f"This currency isn't added "
                    f"to the currencies list."
                )
                if line_number is not None:
                    error_message += f" Line {line_number}."
                raise ValueError(error_message)

            if field_spec.regex_value is not None and not re.match(
                str(field_spec.regex_value), field_value
            ):
                record_type_name = RECORD_TYPE_NAMES.get(
                    record_type, record_type
                )
                error_message = (
                    f"Invalid value '{field_value}' for field"
                    f" '{field_name}' in record type "
                    f"'{record_type_name}'."
                )
                if line_number is not None:
                    error_message += f" Line {line_number}."
                raise ValueError(error_message)
            message = (
                f"Field '{field_name}' in '{RECORD_TYPE_NAMES[record_type]}'"
                f" with value '{field_value}' validated successfully."
            )
            if line_number:
                message += f" Line {line_number}."
            logger.debug(message)

            return True
        except ValueError:
            error_message = f"Validation error for field '{field_name}'"
            if line_number:
                error_message += f" Line {line_number}."
            logger.error(error_message)
            raise
        except KeyError:
            error_message = f"Unknown field '{field_name}'"
            if line_number:
                error_message += f"Line {line_number}."
            logger.error(error_message)
            raise

    def _validate_footer_control_digits(
        self,
        footer_fields: dict,
        calculated_total_counter: float,
        control_sum: float,
    ) -> bool:
        """
        Validates the control digits in the footer according
        to calculated values.
        Args:
            footer_fields: A dictionary of footer field names and values.
            calculated_total_counter: The calculated total counter value.
            control_sum: The calculated control sum.
        Returns:
            True if the footer control digits match the calculated values.
        Raises:
            ValueError: If there's a mismatch between
             footer and calculated values.
        """
        try:
            logger.debug("Validation of footer control digits is started.")
            total_counter = int(footer_fields["total counter"])
            if calculated_total_counter != total_counter:
                calculated_total_counter_str = str(
                    calculated_total_counter
                ).zfill(6)
                total_counter_str = str(total_counter).zfill(6)
                raise ValueError(
                    f"Total counter in the footer does not match the last"
                    f" transaction counter.It should be "
                    f"{calculated_total_counter_str}, "
                    f"but it is {total_counter_str}."
                )

            footer_control_sum = float(footer_fields["control sum"]) / 100

            if abs(control_sum - footer_control_sum) > 0:
                control_sum *= 100
                control_sum_str = str(int(control_sum)).zfill(12)
                footer_control_sum *= 100
                footer_control_sum_str = str(int(footer_control_sum)).zfill(12)
                raise ValueError(
                    f"Control sum in the footer does not match "
                    f"the sum of transaction amounts. It should be"
                    f" {control_sum_str}, but it is {footer_control_sum_str}."
                )
            logger.debug(
                "Validation of footer control digits is successfully finished."
            )
            return True
        except ValueError as e:
            logger.error(f"Footer control digit validation error: {e}")
            raise

    def validate_record(
        self,
        record_type: str,
        line: str,
        line_number: Optional[int] = None,
        calculated_total_counter: Optional[float] = None,
        control_sum: Optional[float] = None,
    ) -> bool:
        """
        Validates a single record line according to predefined criteria.
        Args:
            record_type: The type of record
                        (e.g., header, transaction, footer).
            line: The record line to validate.
            line_number: Optional line number for context.
            calculated_total_counter: The calculated
                                    total counter for footer validation.
            control_sum: The calculated control sum for footer validation.
        Returns:
            True if the record passes all value validations.
        Raises:
            ValueError: If any value validation fails.
        """
        try:
            if record_type == HEADER_ID:
                header_fields = dict(
                    zip(
                        FIELD_FORMATS[HEADER_ID].keys(),
                        self.lines[0].split(","),
                    )
                )
                for field_name, field_value in header_fields.items():
                    ValuesValidator.validate_field(
                        record_type, field_name, field_value, line_number
                    )

            elif record_type == TRANSACTION_ID:
                transaction_fields = dict(
                    zip(FIELD_FORMATS[TRANSACTION_ID].keys(), line.split(","))
                )
                for field_name, field_value in transaction_fields.items():
                    ValuesValidator.validate_field(
                        record_type, field_name, field_value, line_number
                    )

            elif record_type == FOOTER_ID:
                footer_fields = dict(
                    zip(
                        FIELD_FORMATS[FOOTER_ID].keys(),
                        self.lines[-1].split(","),
                    )
                )
                for field_name, field_value in footer_fields.items():
                    ValuesValidator.validate_field(
                        record_type, field_name, field_value, line_number
                    )

                if (
                    calculated_total_counter is not None
                    and control_sum is not None
                ):
                    self._validate_footer_control_digits(
                        footer_fields, calculated_total_counter, control_sum
                    )
            else:
                raise ValueError(
                    f"Unknown record type found on line {line_number}"
                )
            logger.debug(
                f"Values of record type '{record_type}' "
                f"validated successfully."
            )

            return True
        except ValueError as e:
            logger.error(f"Validation error on line {line_number}: {e}")
            raise

    def validate(self) -> bool:
        """
        Validates all records in the fixed-width file
         according to predefined criteria.
        Returns:
            True if all records pass value validations.
        Raises:
            ValueError: If any record fails value validation.
        """
        try:
            previous_counter = None
            calculated_total_counter = 0
            control_sum = 0.0

            for line_number, line in enumerate(self.lines, start=1):
                record_type = line[:FIELD_ID_LENGTH]

                self.validate_record(
                    record_type=record_type,
                    line=line,
                    line_number=line_number,
                    calculated_total_counter=calculated_total_counter,
                    control_sum=control_sum,
                )

                if record_type == TRANSACTION_ID:
                    transaction_fields = dict(
                        zip(
                            FIELD_FORMATS[TRANSACTION_ID].keys(),
                            line.split(","),
                        )
                    )
                    current_counter = int(transaction_fields["counter"])
                    if (
                        previous_counter is not None
                        and current_counter != previous_counter + 1
                    ):
                        current_counter_str = str(current_counter).zfill(
                            6
                        )  # Assuming counter is always 6 digits
                        expected_counter_str = str(previous_counter + 1).zfill(
                            6
                        )
                        raise ValueError(
                            f"Transaction counter is not auto-incremented"
                            f" on line {line_number}. It should be "
                            f"{expected_counter_str},"
                            f" but it is {current_counter_str}."
                        )
                    previous_counter = current_counter

                    calculated_total_counter = current_counter
                    control_sum += (
                        float(transaction_fields["amount"]) / 100
                    )  # Assuming "Amount" is in cents
            logger.info(
                "===== All records values validated successfully. ====="
            )
            return True
        except ValueError as e:
            logger.error(f"File validation failed: {e}")
            raise
