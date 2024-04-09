import logging
from collections import namedtuple
from typing import Optional

_FieldFormatBase = namedtuple(
    "_FieldFormatBase", ["start_position", "end_position", "data_type"]
)


logger = logging.getLogger(__name__)


class FieldFormat(_FieldFormatBase):
    """Represents the format of a field within a fixed-width file.

    Attributes:
        start_position (int): The start position of the field in the file.
        end_position (int): The end position of the field in the file.
        data_type (object): The Python data type expected for the field.
        fixed_value (Optional[str]): The fixed value of the field,
                                    if applicable.
        regex_value (Optional[str]): A regex pattern that the field's value
                                    should match, if applicable.
    """

    def __new__(
        cls,
        start_position: int,
        end_position: int,
        data_type: object,
        fixed_value: Optional[str] = None,
        regex_value: Optional[str] = None,
    ) -> "FieldFormat":
        """Create a new FieldFormat instance."""
        return super().__new__(cls, start_position, end_position, data_type)

    def __init__(
        self,
        start_position: int,
        end_position: int,
        data_type: object,
        fixed_value: Optional[str] = None,
        regex_value: Optional[str] = None,
    ) -> None:
        """Initialize a FieldFormat instance."""
        super().__init__()
        self._fixed_value = fixed_value  # Hidden field
        self._regex_value = regex_value  # Hidden field
        # logger.debug(f"Initialized FieldFormat instance: {self}")

    @property
    def fixed_value(self) -> Optional[str]:
        """Get the fixed value for the field."""
        return self._fixed_value

    @property
    def regex_value(self) -> Optional[str]:
        """Get the regex pattern for the field."""
        return self._regex_value
