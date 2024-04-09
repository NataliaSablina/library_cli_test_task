import argparse


def parse_arguments() -> argparse.Namespace:
    """
    Parses command line arguments for the fixed-width file validator CLI.

    This function defines the command line arguments available for use with
    the CLI. It uses argparse to handle command line argument parsing.

    Returns:
        Namespace: An argparse.Namespace object containing
         the parsed arguments and their values.
    """
    parser = argparse.ArgumentParser(
        description="CLI tool for managing fixed-width files. It supports "
        "validating file structure, editing/retrieving field "
        "values, managing transactions, and configuring field access."
    )
    parser.add_argument(
        "--file-path",
        type=str,
        help="Path to the fixed-width file for processing or validation.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Performs validation on the structure and"
        " content of the specified fixed-width file.",
    )
    parser.add_argument(
        "--record-type",
        choices=["header", "transaction", "footer"],
        help="Specifies the record type for operations that require it."
        " Choose from header, transaction, or footer.",
    )
    parser.add_argument(
        "--transaction-counter",
        type=str,
        help="Specifies the counter for a transaction. Required when "
        "editing or querying transaction-specific fields.",
    )
    parser.add_argument(
        "--field",
        help="Specifies the field name for retrieval or editing operations.",
    )
    parser.add_argument(
        "--new-value",
        help="Specifies the new value for the field being edited.",
    )
    parser.add_argument(
        "--add-transaction",
        action="store_true",
        help="Adds a new transaction record to the file. "
        "Requires --amount and --currency.",
    )
    parser.add_argument(
        "--amount",
        help="Specifies the transaction amount in the format 000000002000,"
        " where the last two digits are the decimal part. "
        "Required for adding a new transaction.",
    )
    parser.add_argument(
        "--currency",
        choices=["USD", "EUR", "GBP"],
        help="Specifies the currency of a new transaction."
        " Required for adding a new transaction.",
    )
    parser.add_argument(
        "--block-field-from-changes",
        help="Marks a field as immutable, preventing future edits.",
    )
    parser.add_argument(
        "--unblock-field-from-changes",
        help="Removes the immutable flag from a field, allowing edits.",
    )
    parser.add_argument(
        "--log",
        nargs="?",
        const="info",
        default="warning",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Sets the logging level for both CLI and library components. "
        "Defaults to 'warning'. Options include debug, info, warning, "
        "error, and critical. Use it if you want to see the steps of"
        " file processing or if you want to see the "
        "result of retrieve operations.",
    )

    return parser.parse_args()
