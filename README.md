# Fixed-Width File CLI & Library

## Overview

This project consists of a Command Line Interface (CLI) and a Python library
designed to manage and process fixed-width files.
The library provides a suite of tools for file structure validation, 
field value editing and retrieval, transaction management, 
and setting field immutability. The CLI offers an interface to 
access these tools directly from the command line.

## Installation
1. Clone this repository with git
2. Run ```pip install -e .```

## Library Features
The Python library offers a variety of features:

1. Validation of fixed-width file structure.
2. Retrieving and editing field values within the file.
3. Appending transactions to the file.
4. Managing immutable fields to prevent unintended modifications.

## CLI Commands
The CLI tool allows easy access to the library functionalities using
various commands. It is built using `argparse` to handle command-line arguments.

## Command-Line Arguments
The CLI supports several command-line arguments to specify the operations:

1. `--file-path`: Specify the path to the fixed-width file.
2. `--validate`: Perform validation on the structure and content of the file(you 
can add it to all commands where --file-path is specified to validate the file).
3. `--record-type`: Define the record type for operations (header, transaction, footer).
4. `--transaction-counter`: The counter for a transaction record.
5. `--field`: Specify the field name for retrieval or editing.
6. `--new-value`: Define a new value for the specified field.
7. `--add-transaction`: Add a new transaction to the file.
8. `--amount`: Specify the amount for a new transaction.
9. `--currency`: Set the currency for a new transaction.
10. `--block-field-from-changes`: Make a field immutable.
11. `--unblock-field-from-changes`: Remove the immutability from a field.
12. `--log` : Set the logging level (debug, info, warning, error, critical).
(you can add it to absolutely all commands, usage of `--log` will set 
log-level into INFO by default, if you want to change logging level 
you can write like this, for example `--log debug`)

## File structure
The fixed-width file consists of three record types: Header, Transaction, 
and Footer. Each record is delimited by a line ending symbol,
and the file has the following structure:
1. Header (mandatory)
2. Transaction (can be repeated from 1 to 20,000 times)
3. Footer (mandatory)

### Fields Description
#### Header
1. Field ID (1-2): string, fixed value "01"
2. Name (3-30): string, the name field
3. Surname (31-60): string, the surname field
4. Patronymic (61-90): string, the patronymic field
5. Address (91-120): string, the address field
##### Transaction
1. Field ID (1-2): string, fixed value "02"
2. Counter (3-8): string, format "000001" - "020000", should be auto-incremented
3. Amount (9-20): string, format "000000000200" (last two digits are decimal), contains leading zeros
4. Currency (21-23): string, fixed list of possible values (now it contains "USD", "EUR", "GBP")
5. Reserved (24-120): string, spaces
#### Footer
1. Field ID (1-2): string, fixed value "03"
2. Total Counter (3-8): number, format "000001" - "020000", the overall number of transactions in the file
3. Control Sum (9-20): number, format "000000000200", the total amount of all transactions in the file
4. Reserved (21-120): string, spaces

Each line should be 120 characters long, with the unused space filled with spaces.

### Example .csv File
```text
01,natalia                     ,sabl1na                       ,dnit                          ,Doprikuwa2                   
02,000001,000000009000,gbp,                                                                                                 
02,000002,000000034000,eur,                                                                                                 
02,000003,000000001000,gbp,                                                                                                 
02,000004,000000001000,gbp,                                                                                                 
02,000005,000000011000,gbp,                                                                                                 
02,000006,000000031000,gbp,                                                                                                 
02,000007,000000032000,usd,                                                                                                 
02,000008,000000001000,gbp,                                                                                                 
02,000009,000000001000,gbp,                                                                                                 
02,000010,000000001000,usd,                                                                                                 
02,000011,000000001000,usd,                                                                                                 
02,000012,000000001000,usd,                                                                                                 
02,000013,000000011000,USD,                                                                                                 
03,000013,000000135000,                                                                                                    
```

## CLI usage

`/home/user/test_data.csv` - example of path to the file with data. 
The CLI can be used with the following commands:
1. `fintech_file_cli --file-path /home/user/test_data.csv` - This command will execute the default action for the provided file.
2. `fintech_file_cli --file-path /home/user/test_data.csv --log debug` - This command will process the file and output logs at the debug level.
3. `fintech_file_cli --file-path /home/user/test_data.csv --validate` - This command validates the file structure, length, and values.
4. `fintech_file_cli --file-path /home/user/test_data.csv --record-type "header" --field "name" --log warning` - Retrieve the 'name' field from the header of the file with logs level warning.
5. `fintech_file_cli --file-path /home/user/test_data.csv --record-type "footer" --field "control sum"` - Retrieve the 'control sum' field from the footer of the file.
6. `fintech_file_cli --file-path /home/user/test_data.csv --record-type "header" --field "name" --new-value "warsaw"` - Edit the 'name' field of the header with new value "warsaw".
7. `fintech_file_cli --file-path /home/user/test_data.csv --record-type "transaction" --transaction-counter "000005" --field "amount"`- Retrieve the 'amount' field from the transaction with counter=000005 of the file.
8. `fintech_file_cli --file-path /home/user/test_data.csv --record-type "transaction" --transaction-counter "000005" --field "amount" --new-value "000000011000"` - Edit the 'amount' field of the transaction with counter=000005 to "000000011000"(if you edit transaction 'amount' field, then the footer control sum will be recalculated automatically).
9. `fintech_file_cli --unblock-field-from-changes "control sum"` - Remove the immutable status from the 'control sum' field, allowing edits.
10. `fintech_file_cli --block-field-from-changes "amount"` - Mark the 'amount' field as immutable to prevent editing.
11. `fintech_file_cli --file-path /home/user/test_data.csv --add-transaction --amount "000000011000" --currency USD` - Append a new transaction with the amount "000000011000" in USD to the file.(footer control sum and total counter will be recalculated automatically)


## Local development
Local development and testing are facilitated by a Makefile, which provides 
commands for running tests and linters:

1. `make linters` - run linters for both cli and library
2. `make tests` - run tests for both cli and library
3. `make tests-coverage` - check tests coverage for both cli and library
4. `make tests-library` - run tests only for the library
5. `make tests-cli` - run tests only for the cli
6. `make tests-library-coverage` - check tests coverage only for the library
7. `make tests-cli-coverage` - check tests coverage only for the cli
