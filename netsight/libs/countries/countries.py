import json
from functools import lru_cache
from pathlib import Path
from typing import TypedDict


class Country(TypedDict):
    code: str
    name: str
    visible_name: str
    timezone: int


# source data from https://github.com/umpirsky/country-list/tree/4d8f87526c891a7b110b530eabf910c3f7468ad6
# ISO 3166-1 codes
data_dir = Path(__file__).parent


@lru_cache
def countries_for_language(language: str) -> list[Country]:
    """Returns a list of countries for a given language."""
    country_data_path = data_dir / f"{language}.json"
    time_zone_data_path = data_dir / "timezone.json"
    with country_data_path.open(encoding="utf-8") as file:
        country_data = json.load(file)

    with time_zone_data_path.open(encoding="utf-8") as file:
        time_zone_data = json.load(file)

    countries: list[Country] = []
    for country_code, country_name in country_data.items():
        countries.append(
            Country(
                code=country_code,
                name=country_name,
                visible_name=f"{country_name} ({country_code})",
                timezone=time_zone_data.get(country_code),
            )
        )

    return countries


@lru_cache
def get_country_by_name(country_name: str, language: str) -> Country | None:
    """Returns a country by its ISO 3166-1 alpha-2 code."""
    countries = countries_for_language(language)
    return next((country for country in countries if country["name"] == country_name), None)
