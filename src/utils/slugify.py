import re
from unicodedata import normalize

_punctuation_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim="-") -> str:
    """
    Generate an ASCII-only slug
    """
    result = []
    for word in _punctuation_re.split(text.lower()):
        word = normalize("NFKD", word).encode("ascii", "ignore").decode("utf-8")
        if word:
            result.append(word)
    return delim.join(result)
