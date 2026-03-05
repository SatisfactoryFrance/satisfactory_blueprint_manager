import os


def get_blueprints_base():
    return os.path.join(
        os.getenv("LOCALAPPDATA"),
        "FactoryGame",
        "Saved",
        "SaveGames",
        "blueprints"
    )
