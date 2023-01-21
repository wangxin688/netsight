from collections import defaultdict
from functools import reduce
from operator import getitem
from typing import Callable, Union

from src.app.netsight.const import LOCALE
from src.utils.i18n_trans import locale


class I18n:
    def __init__(self, locales: dict = locale) -> None:
        self.locales = locales

    def gettext(
        self, path: str, language: LOCALE = "en_US", **kwargs
    ) -> Union[dict, str]:
        founded: Union[dict, str] = self._find(language, path)

        if len(kwargs) > 0 and isinstance(founded, str):
            try:
                return founded.format_map(defaultdict(str, **kwargs))
            except KeyError:
                return founded
        return founded

    def _find(self, language: LOCALE, path: str) -> Union[dict, str]:
        try:
            return reduce(getitem, path.split("."), self.locales[language])
        except (KeyError, TypeError):
            return f"missing translation for {language}"


_i18n: I18n = I18n()
_: Callable[..., Union[dict, str]] = _i18n.gettext
