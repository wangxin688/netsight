import csv
from functools import lru_cache
from pathlib import Path

# source data from https://github.com/umpirsky/country-list/tree/4d8f87526c891a7b110b530eabf910c3f7468ad6
# ISO 3166-1 codes
data_dir = Path(__file__).parent / "country_data" / "data"


@lru_cache(1)
def available_languages() -> list[str]:
    return sorted(x.name for x in data_dir.iterdir() if (x / "country.csv").exists())


@lru_cache
def countries_for_language(lang: str) -> list[tuple[str, str]]:
    path = data_dir / _clean_lang(lang) / "country.csv"
    with path.open(encoding="utf-8") as file_:
        return [(row["id"], row["value"]) for row in csv.DictReader(file_)]


def _clean_lang(lang: str) -> str:
    cleaned_lang = lang.replace("-", "_").lower()
    for language in available_languages():
        if cleaned_lang == language.lower():
            return language
    msg = f"Language {lang} not found"
    raise ValueError(msg)
