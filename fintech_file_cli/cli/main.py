import logging
import sys

from fintech_file_cli.executors import CommandExecutor
from fintech_file_cli.validators import ArgumentValidator
from fixed_width_struct_io.access_control import immutable_field_setter
from fixed_width_struct_io.readers import FieldRetriever
from fixed_width_struct_io.validators import (
    FileStructureValidator,
    StringLengthValidator,
    ValuesValidator,
)
from fixed_width_struct_io.writers import FieldEditor, TransactionAppender

from fintech_file_cli.setup_logger import configure_logging
from fintech_file_cli.cli.config import parse_arguments


logger = logging.getLogger(__name__)


def main() -> None:
    """
    Main entry point for the fintech_file_cli tool.
    It parses command-line arguments, sets up logging,
     validates arguments, and executes the requested command on a
    fixed-width file according to the provided arguments.
    """
    try:
        args = parse_arguments()
        configure_logging(args.log)

        validator = ArgumentValidator(args)
        validator.validate()

        file_path = args.file_path or ""

        file_structure_validator = FileStructureValidator(file_path=file_path)
        length_validator = StringLengthValidator(file_path=file_path)
        values_validator = ValuesValidator(file_path=file_path)
        field_retriever = FieldRetriever(file_path=file_path)
        field_editor = FieldEditor(file_path=file_path)
        transaction_appender = TransactionAppender(file_path=file_path)

        executor = CommandExecutor(
            args=args,
            file_structure_validator=file_structure_validator,
            length_validator=length_validator,
            values_validator=values_validator,
            field_retriever=field_retriever,
            field_editor=field_editor,
            transaction_appender=transaction_appender,
            immutable_field_setter=immutable_field_setter,
        )
        executor.execute()
    except ValueError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
