from setuptools import setup, find_packages

setup(
    name="fintech_file_cli",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    tests_require=[
        "pytest",
    ],
    entry_points={
        "console_scripts": [
            "fintech_file_cli=fintech_file_cli.cli.main:main",
        ],
    },
)
