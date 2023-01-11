from pathlib import Path

from fastapi_babel import Babel, BabelConfigs

configs = BabelConfigs(
    ROOT_DIR=Path(__file__).parent,
    BABEL_DEFAULT_LOCALE="en-US",
    BABEL_TRANSLATION_DIRECTORY="lang",
)

babel: Babel = Babel(configs=configs)

if __name__ == "__main__":
    babel.run_cli()
