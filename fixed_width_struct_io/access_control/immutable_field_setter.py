import logging
import os

from fixed_width_struct_io.constants import (
    FIELD_LENGTHS,
    FIELD_IMMUTABLE_CONFIG_FILE_NAME,
)
import json


logger = logging.getLogger(__name__)


class ImmutableFieldSetter:
    """Handles setting fields as immutable to prevent changes."""

    def __init__(self) -> None:
        """Initializes the immutable field setter with a config file."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(
            current_dir, FIELD_IMMUTABLE_CONFIG_FILE_NAME
        )
        self._immutable_fields = self._load_immutable_fields()

    def _load_immutable_fields(self) -> set:
        """
        Loads the set of immutable fields from a JSON configuration file.
        Returns an empty set if the file is missing or invalid.
        """
        try:
            with open(self.config_path, "r") as file:
                data = json.load(file)
                return set(data.get("immutable_fields", []))
        except FileNotFoundError:
            logger.warning(
                f"Immutable fields config file not found."
                f" Creating a new one at {self.config_path}."
            )
            return set()
        except json.JSONDecodeError:
            logger.error(
                f"Immutable fields config file is corrupted "
                f"or invalid at {self.config_path}."
            )
            return set()

    def _save_immutable_fields(self) -> None:
        """Save the current state of immutable fields
        to the configuration file."""
        try:
            with open(self.config_path, "w") as file:
                json.dump(
                    {"immutable_fields": list(self._immutable_fields)}, file
                )
            logger.debug("Immutable fields successfully saved.")
        except IOError as e:
            logger.exception(f"Failed to save immutable fields: {e}")
            raise e

    def _field_exists(self, field_name: str) -> bool:
        """
        Checks if the provided field name exists in the
        FIELD_LENGTHS definitions.
        Logs an error if the field does not exist.
        """
        field_exists = any(
            field_name.lower() in fields for fields in FIELD_LENGTHS.values()
        )
        if not field_exists:
            logger.error(
                f"Field '{field_name}' does not "
                f"exist and cannot be blocked."
            )
            raise ValueError(
                f"Field '{field_name}' does not "
                f"exist and cannot be blocked."
            )

        return field_exists

    def make_field_immutable(self, field_name: str) -> bool:
        """
        Marks the specified field as immutable if it exists.
        Returns True if the field was successfully set as immutable.
        """
        if self._field_exists(field_name):
            self._immutable_fields.add(field_name)
            self._save_immutable_fields()
            logger.info(f"Field '{field_name}' marked as immutable.")
            return True
        return False

    def make_field_mutable(self, field_name: str) -> bool:
        """
        Removes the immutable status from the specified
        field if it is currently immutable.
        Returns True if the field's status was successfully changed to mutable.
        """
        if self._field_exists(field_name):
            if field_name in self._immutable_fields:
                self._immutable_fields.remove(field_name)
                self._save_immutable_fields()
                logger.info(f"Field '{field_name}' is now mutable.")
                return True
            else:
                logger.error(f"Field '{field_name}' is not blocked.")
                return False
        return False

    def is_field_immutable(self, field_name: str) -> bool:
        """Check if a field is immutable."""
        if self._field_exists(field_name):
            return field_name in self._immutable_fields
        return False


immutable_field_setter = ImmutableFieldSetter()
