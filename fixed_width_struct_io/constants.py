from collections import namedtuple

from fixed_width_struct_io.helpers import FieldFormat

HEADER_ID = "01"
TRANSACTION_ID = "02"
FOOTER_ID = "03"

HEADER = "header"
TRANSACTION = "transaction"
FOOTER = "footer"

FIELD_ID_LENGTH = 2
LINE_LENGTH = 120

CURRENCIES_LIST = ["usd", "eur", "gbp"]

MAX_TRANSACTIONS_AMOUNT = 20000

RECORD_TYPES = {
    "header": HEADER_ID,
    "transaction": TRANSACTION_ID,
    "footer": FOOTER_ID,
}

FieldLength = namedtuple("FieldLength", ["start_position", "end_position"])

FIELD_LENGTHS = {
    HEADER_ID: {
        "field id": FieldLength(1, 2),
        "name": FieldLength(3, 30),
        "surname": FieldLength(31, 60),
        "patronymic": FieldLength(61, 90),
        "address": FieldLength(91, 120),
    },
    TRANSACTION_ID: {
        "field id": FieldLength(1, 2),
        "counter": FieldLength(3, 8),
        "amount": FieldLength(9, 20),
        "currency": FieldLength(21, 23),
        "reserved": FieldLength(24, 120),
    },
    FOOTER_ID: {
        "field id": FieldLength(1, 2),
        "total counter": FieldLength(3, 8),
        "control sum": FieldLength(9, 20),
        "reserved": FieldLength(21, 120),
    },
}

FIELD_ORDER = {
    HEADER_ID: ["field id", "name", "surname", "patronymic", "address"],
    TRANSACTION_ID: ["field id", "counter", "amount", "currency", "reserved"],
    FOOTER_ID: ["field id", "total counter", "control sum", "reserved"],
}

FIELD_FORMATS = {
    HEADER_ID: {
        "field id": FieldFormat(
            start_position=1,
            end_position=2,
            data_type=str,
            fixed_value=HEADER_ID,
        ),
        "name": FieldFormat(start_position=3, end_position=30, data_type=str),
        "surname": FieldFormat(
            start_position=31, end_position=60, data_type=str
        ),
        "patronymic": FieldFormat(
            start_position=61, end_position=90, data_type=str
        ),
        "address": FieldFormat(
            start_position=91, end_position=120, data_type=str
        ),
    },
    TRANSACTION_ID: {
        "field id": FieldFormat(
            start_position=1,
            end_position=2,
            data_type=str,
            fixed_value=TRANSACTION_ID,
        ),
        "counter": FieldFormat(
            start_position=3,
            end_position=8,
            data_type=str,
            regex_value=r"^\d{6}$",
        ),
        "amount": FieldFormat(
            start_position=9,
            end_position=20,
            data_type=str,
            regex_value=r"^\d{12}$",
        ),
        "currency": FieldFormat(
            start_position=21,
            end_position=23,
            data_type=str,
            regex_value=r"^[A-Za-z]{3}$",
        ),
        "reserved": FieldFormat(
            start_position=24,
            end_position=120,
            data_type=str,
            regex_value=r"^\s*$",
        ),
    },
    FOOTER_ID: {
        "field id": FieldFormat(
            start_position=1,
            end_position=2,
            data_type=str,
            fixed_value=FOOTER_ID,
        ),
        "total counter": FieldFormat(
            start_position=3,
            end_position=8,
            data_type=str,
            regex_value=r"^\d{6}$",
        ),
        "control sum": FieldFormat(
            start_position=9,
            end_position=20,
            data_type=str,
            regex_value=r"^\d{12}$",
        ),
        "reserved": FieldFormat(
            start_position=21,
            end_position=120,
            data_type=str,
            regex_value=r"^\s*$",
        ),
    },
}

RECORD_TYPE_NAMES = {
    HEADER_ID: "header",
    TRANSACTION_ID: "transaction",
    FOOTER_ID: "footer",
}

LAST_TRANSACTION_LIST_INDEX = -2

FIELD_IMMUTABLE_CONFIG_FILE_NAME = "field_immutable_config.json"
