import logging
from abc import ABC
from typing import List, Optional


logger = logging.getLogger(__name__)


class FileIOBase(ABC):
    """
    Abstract base class for file input/output operations.

    This class provides a framework for reading and
     initializing lines from a file or directly from a list
      of strings provided at object creation.

    Attributes:
        lines (List[str]): List of lines from the file
                            or directly passed as an argument.
        file_path (str): Path to the file from which to read lines.
    """

    def __init__(
        self,
        lines: Optional[List[str]] = None,
        file_path: Optional[str] = None,
    ) -> None:
        """
        Initialize with either a list of lines or a file path.
        Throws ValueError if both or neither arguments are provided.
        """
        self.lines = self._initialize_lines(lines, file_path)
        self.file_path = file_path if file_path is not None else ""

    def _initialize_lines(
        self,
        lines: Optional[List[str]] = None,
        file_path: Optional[str] = None,
    ) -> List[str]:
        """Read lines from a file or use the provided list."""
        if (lines is None) == (
            file_path is None
        ):  # Checks if exactly one of them is provided
            raise ValueError(
                "Exactly one of 'lines' or 'file_path' must be provided."
            )
        if file_path:
            try:
                return self._read_file(file_path)
            except Exception as e:
                logger.exception(f"Failed to read file at {file_path}.")
                raise e
        else:
            return lines if lines else []

    def _read_file(self, file_path: str) -> List[str]:
        """Read lines from the specified file. Handles file-related errors."""
        try:
            with open(file_path, "r") as file:
                lines = [
                    line.rstrip("\n").rstrip("\r") for line in file.readlines()
                ]
            if not lines:
                raise ValueError("File is empty.")
            return lines

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except PermissionError:
            logger.error(f"Permission denied for file: {file_path}")
            raise
        except Exception as e:
            logger.exception(f"An error occurred while reading the file: {e}")
            raise
