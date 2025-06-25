# File: tests/utils/test_reporting.py

import pytest

from src.utils.reporting import parse_keywords_from_string


@pytest.mark.parametrize(
    ("input_string", "expected_output"),
    [
        ("key1:10, key2:20", {"key1": 10, "key2": 20}),
        ("  key1 : 10 ,  key2:20  ", {"key1": 10, "key2": 20}),
        ("key1:10, invalid_item, key2:20", {"key1": 10, "key2": 20}),
        ("key1:10, key2:val, key3:30", {"key1": 10, "key3": 30}),
        ("", {}),
        ("key1:100", {"key1": 100}),
    ],
)
def test_parse_keywords_from_string(input_string, expected_output):
    """Memastikan fungsi parsing kata kunci bekerja dengan benar untuk berbagai input."""
    assert parse_keywords_from_string(input_string) == expected_output