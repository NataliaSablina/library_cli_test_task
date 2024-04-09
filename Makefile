APP_FOLDER=.
LIBRARY_FOLDER=fixed_width_struct_io
CLI_FOLDER=fintech_file_cli

linters:
	python -m black --line-length=79 --exclude='(\.venv|$(CLI_FOLDER)/tests/|$(LIBRARY_FOLDER)/tests/)' $(APP_FOLDER)
	python -m flake8 --exclude=./.venv,*/tests/* $(APP_FOLDER)
	python -m bandit --exclude=./.venv,*/tests/* -r $(APP_FOLDER) --skip "B101" --recursive
	python -m mypy --exclude='(\.venv|$(CLI_FOLDER)/tests/|$(LIBRARY_FOLDER)/tests/)' --ignore-missing-imports --disallow-untyped-defs $(APP_FOLDER)

tests:
	python -m pytest $(APP_FOLDER) -vv

tests-coverage:
	python -m pytest --cov=$(APP_FOLDER) -vv

tests-library:
	python -m pytest $(LIBRARY_FOLDER) -vv

tests-cli:
	python -m pytest $(CLI_FOLDER) -vv

tests-library-coverage:
	python -m pytest --cov=$(LIBRARY_FOLDER) -vv

tests-cli-coverage:
	python -m pytest --cov=$(CLI_FOLDER) -vv
