import logging


def setup_logger() -> logging.Logger:
    """
    Sets up and configures the logger for the fixed_width_struct_io library.
    """
    logger = logging.getLogger("fixed_width_struct_io")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
    return logger


fixed_width_struct_io_logger = setup_logger()
