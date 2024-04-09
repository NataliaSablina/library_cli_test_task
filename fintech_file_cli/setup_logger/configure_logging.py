import logging

from fintech_file_cli.setup_logger.logger import fintech_file_cli_logger
from fixed_width_struct_io.logger import fixed_width_struct_io_logger


def configure_logging(level: str) -> None:
    """
    Configures the logging level for both the
    fintech_file_cli and fixed_width_struct_io loggers.

    This function adjusts the logging level based on the input argument.
    It can dynamically set the logging level for both the CLI and
    library components to control the verbosity of the output.
    If no level is specified, logging is disabled by setting the
     log level to a value higher than CRITICAL.

    Parameters:
    - level (str): The logging level to set. Valid levels are
                    'DEBUG', 'INFO', 'WARNING', 'ERROR', and 'CRITICAL'.
                   If None or an invalid level is provided,
                   logging is disabled.

    Raises:
    - ValueError: If the provided logging level is invalid.

    Note:
    - If the loggers do not already have handlers, a StreamHandler
     will be added to ensure that logging output
      goes to stderr.
    """
    if level:
        numeric_level = getattr(logging, level.upper(), None)
        if numeric_level is not None:
            fixed_width_struct_io_logger.setLevel(numeric_level)
            if not fixed_width_struct_io_logger.hasHandlers():
                fixed_width_struct_io_logger.addHandler(
                    logging.StreamHandler()
                )

            fintech_file_cli_logger.setLevel(numeric_level)
            if not fintech_file_cli_logger.hasHandlers():
                fintech_file_cli_logger.addHandler(logging.StreamHandler())

            fintech_file_cli_logger.info(f"Log level set to {level}")
            fixed_width_struct_io_logger.info(
                f"Library log level set to {level}"
            )
        else:
            raise ValueError(f"Invalid log level: {level}")
    else:
        # Disable logging by setting a high log level
        fixed_width_struct_io_logger.setLevel(logging.CRITICAL + 1)
        fintech_file_cli_logger.setLevel(logging.CRITICAL + 1)
