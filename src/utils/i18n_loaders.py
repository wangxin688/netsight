from collections import defaultdict
from functools import reduce
from operator import getitem
from typing import Callable, Literal, Union

from src.utils.i18n_trans import locale


class I18n:
    def __init__(self, locales: dict = locale) -> None:
        self.locales = locales

    def gettext(
        self, path: str, language: Literal["en_US", "zh_CN"] = "en_US", **kwargs
    ) -> Union[dict, str]:
        founded: Union[dict, str] = self.__find(language, path)

        if len(kwargs) > 0 and isinstance(founded, str):
            try:
                return founded.format_map(defaultdict(str, **kwargs))
            except KeyError:
                return founded
        return founded

    def __find(
        self, language: Literal["en_US", "zh_CN"], path: str
    ) -> Union[dict, str]:
        try:
            return reduce(getitem, path.split("."), self.locales[language])
        except (KeyError, TypeError):
            return f"missing translation for {language}"


_i18n: I18n = I18n()
_: Callable = _i18n.gettext

# print(_("dcim.site.name_not_found", name="CNCTU06"))
