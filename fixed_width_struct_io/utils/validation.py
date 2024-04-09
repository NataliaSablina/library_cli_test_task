import logging
from typing import Any

from fixed_width_struct_io.constants import RECORD_TYPES
from fixed_width_struct_io.validators import StringLengthValidator
from fixed_width_struct_io.validators.values_validator import ValuesValidator


logger = logging.getLogger(__name__)


def validate_field(
    record_type: str, field_name: str, field_value: Any
) -> bool:
    """
    Validates a field value against defined constraints
    for its record type and field name. This function checks if the
    field value adheres to the specified length and value constraints.
    Args:
        record_type: The type of record
                    (e.g., 'header', 'transaction', 'footer').
        field_name: The name of the field to be validated.
        field_value: The value of the field to be validated.

    Returns:
        bool: True if the field value passes
        all validations, False otherwise.
    Raises:
        KeyError: If the record type or field name does not exist.
        ValueError: If the field value does not
        meet length or value constraints.
    """
    try:
        record_type_id = RECORD_TYPES[record_type]
    except KeyError as e:
        logger.error(f"Invalid record type '{record_type}': {e}")
        raise ValueError(f"Invalid record type '{record_type}'.") from e

    try:
        length_valid = StringLengthValidator.validate_individual_field_length(
            record_type=record_type_id,
            field_name=field_name,
            field_value=field_value,
        )
        value_valid = ValuesValidator.validate_field(
            record_type=record_type_id,
            field_name=field_name,
            field_value=field_value,
        )
        if length_valid and value_valid:
            return True
        else:
            logger.info(
                f"Field '{field_name}' in record type"
                f" '{record_type}' failed validation."
            )
            return False
    except Exception as e:
        logger.exception(
            f"Error validating field '{field_name}' "
            f"in record type '{record_type}': {e}"
        )
        raise ValueError(
            f"Error validating field '{field_name}' "
            f"in record type '{record_type}'."
        ) from e
