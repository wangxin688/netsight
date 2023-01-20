from pathlib import Path

from fastapi_babel import Babel, BabelConfigs

configs = BabelConfigs(
    ROOT_DIR=Path(__file__).parent,
    BABEL_DEFAULT_LOCALE="en_US",
    BABEL_TRANSLATION_DIRECTORY="lang",
)

babel: Babel = Babel(configs=configs)
