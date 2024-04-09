from abc import abstractmethod
from typing import Any

from fixed_width_struct_io.core import FileIOBase


class BaseValidator(FileIOBase):
    """
    Abstract base class for validation operations on fixed-width
    file structures. Subclasses should implement the `validate`
     method to perform specific validation tasks.
    """

    @abstractmethod
    def validate(self, *args: Any, **kwargs: Any) -> bool | None:
        """
        Abstract method for performing validation.
        Must be implemented by subclasses.
        Returns:
            A boolean indicating if the validation passed,
             or None if validation is not applicable.
        Raises:
            NotImplementedError: If not overridden in a subclass.
        """
        raise NotImplementedError
