import pytest

from src.libs.countries import get_country_by_name


@pytest.mark.parametrize(
    ("name", "language", "expected"),
    [
        ("中国", "zh_CN", {"code": "CN", "name": "中国", "visible_name": "中国 (CN)", "timezone": 8}),
        (
            "United States",
            "en_US",
            {"code": "US", "name": "United States", "visible_name": "United States (US)", "timezone": -6},
        ),
    ],
)
def test_get_country_by_name(name: str, language: str, expected: dict) -> None:
    assert get_country_by_name(name, language) == expected
