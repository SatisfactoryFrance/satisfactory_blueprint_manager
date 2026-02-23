import os
import json
import uuid


class ConfigService:

    def __init__(self):
        self.path = os.path.join(os.getenv("LOCALAPPDATA"),"satisfactory_blueprint_manager.json")

        self.data = {}
        self.load()

    # -------------------------
    # Chargement / sauvegarde
    # -------------------------

    def load(self):
        if os.path.isfile(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)

            # Migration anciennes configs sans id
            if "id" not in self.data:
                self.data["id"] = str(uuid.uuid4())
                self.save()

        else:
            self.data = {
                "lang": "fr",
                "game_folder": "undefined",
                "id": str(uuid.uuid4())
            }
            self.save()

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    # -------------------------
    # Helpers
    # -------------------------

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def get(self, key, default=None):
        return self.data.get(key, default)

    # -------------------------
    # Shortcuts SBM
    # -------------------------

    def get_lang(self):
        return self.get("lang", "fr")

    def set_lang(self, lang):
        self.set("lang", lang)

    def get_game_folder(self):
        return self.get("game_folder")

    def set_game_folder(self, folder):
        self.set("game_folder", folder)

    def get_id(self):
        return self.get("id")
