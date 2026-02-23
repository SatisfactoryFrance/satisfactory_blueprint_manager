import os
import sys
import i18n


class I18nService:
    def __init__(self, locale: str = "fr"):
        self.i18n = i18n
        self._configure(locale)

    def _configure(self, locale: str):
        # Gérer PyInstaller (sys._MEIPASS)
        base_dir = os.getcwd()
        if getattr(sys, "frozen", False):
            base_dir = sys._MEIPASS

        self.i18n.load_path.clear()
        self.i18n.load_path.append(os.path.join(base_dir, "locale"))

        self.i18n.set("file_format", "json")
        self.i18n.set("filename_format", "{locale}.{format}")
        self.i18n.set("skip_locale_root_data", True)
        self.i18n.set("fallback", "en")
        self.set_locale(locale)

    def set_locale(self, locale: str):
        self.i18n.set("locale", str(locale))

    def t(self, key: str, **kwargs) -> str:
        return self.i18n.t(key, **kwargs)
