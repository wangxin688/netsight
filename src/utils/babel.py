from fastapi_babel import Babel, BabelConfigs

configs = BabelConfigs(
    ROOT_DIR=__file__,
    BABEL_DEFAULT_LOCALE="en",
    BABEL_TRANSLATION_DIRECTORY="lang",
)

babel: Babel = Babel(configs=configs)

if __name__ == "__main__":
    babel.run_cli()
