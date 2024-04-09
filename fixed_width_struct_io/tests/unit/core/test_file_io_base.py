import os
import stat
import pytest

from fixed_width_struct_io.core import FileIOBase


class TestFileIOBase:
    # Test initialization with file path
    def test_init_with_file_path(self, sample_file):
        file_io = FileIOBase(file_path=sample_file)
        assert file_io.file_path == sample_file
        for line in file_io.lines:
            print(line)
        assert len(file_io.lines) == 5

    def test_init_with_lines(self):
        lines = [
            "01,nnnnnn                      ,ooooooo                       ,dnit                          ,street4567                    ",
            "02,000001,000000009000,gbp,                                                                                                 ",
            "02,000002,000000034000,eur,                                                                                                 ",
            "02,000003,000000001000,gbp,                                                                                                 ",
            "03,000012,000000044000,                                                                                                    "
        ]
        file_io = FileIOBase(lines=lines)
        assert file_io.file_path == ""
        assert file_io.lines == lines

    def test_init_with_invalid_file_path(self):
        with pytest.raises(FileNotFoundError):
            FileIOBase(file_path="non_existent_file.txt")

    def test_init_with_empty_file(self):
        empty_file_path = "empty_file.txt"
        with pytest.raises(ValueError):
            FileIOBase(file_path=empty_file_path)

    def test_init_with_permission_denied(self, sample_file):
        original_permissions = os.stat(sample_file).st_mode
        os.chmod(sample_file, 0o222)
        with pytest.raises(PermissionError):
            FileIOBase(file_path=sample_file)
        os.chmod(sample_file, original_permissions)

    def test_init_with_other_exceptions(self, monkeypatch):
        def mock_read_file(self, file_path):
            raise RuntimeError("Custom error")
        monkeypatch.setattr(FileIOBase, "_read_file", mock_read_file)
        with pytest.raises(RuntimeError):
            FileIOBase(file_path="sample_file.txt")
