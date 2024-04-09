import logging


def setup_logger() -> logging.Logger:
    """
    Sets up and configures the logger for the fintech_file_cli application.
    """
    logger = logging.getLogger("fintech_file_cli")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - [fintech_file_cli] - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
    return logger


fintech_file_cli_logger = setup_logger()
