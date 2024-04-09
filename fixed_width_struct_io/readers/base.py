from abc import abstractmethod
from typing import Any

from fixed_width_struct_io.core import FileIOBase


class BaseRetriever(FileIOBase):
    """
    Abstract base class for retrieving data from a fixed-width file.
    """

    @abstractmethod
    def retrieve(self, *args: Any, **kwargs: Any) -> Any:
        """
        Abstract method to retrieve data from a fixed-width file.
        This method must be implemented by subclasses to handle
        the specifics of field retrieval.
        Returns:
            The retrieved field value.
        Raises:
            NotImplementedError: If the subclass
            does not implement this method.
        """
        raise NotImplementedError
