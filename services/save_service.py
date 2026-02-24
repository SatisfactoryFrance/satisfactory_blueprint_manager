import os
from core.paths import get_blueprints_base


class SaveService:

    def __init__(self, config):
        self.config = config

    def list_saves(self):

        base = get_blueprints_base()

        if not os.path.exists(base):
            return []

        return [
            d for d in os.listdir(base)
            if os.path.isdir(os.path.join(base, d))
        ]

    def get_current(self):

        folder = self.config.get_game_folder()

        if not folder or folder == "undefined":
            return None

        return os.path.basename(folder)

    def set_current(self, name):

        base = get_blueprints_base()
        path = os.path.join(base, name)

        if os.path.isdir(path):
            self.config.set_game_folder(path)
            return True

        return False
