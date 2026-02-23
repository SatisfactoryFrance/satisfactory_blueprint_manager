import os
import shutil
from pathlib import Path


class BlueprintService:

    def __init__(self):
        pass

    # -------------------------
    # Listing
    # -------------------------

    def list_blueprints(self, game_folder):
        """
        Retourne une liste de blueprints présents dans le dossier jeu
        """
        results = []

        if not game_folder or not os.path.isdir(game_folder):
            return results

        i = 0
        for f in os.listdir(game_folder):
            if f.endswith(".sbp"):
                results.append({
                    "id": i,
                    "blueprint": f
                })
                i += 1

        return results

    # -------------------------
    # Suppression
    # -------------------------

    def delete_blueprint(self, game_folder, bp_file):
        """
        Supprime un blueprint + son .sbpcfg
        """
        sbp = os.path.join(game_folder, bp_file)

        if os.path.isfile(sbp):
            os.remove(sbp)

            stem = Path(bp_file).stem
            cfg = os.path.join(game_folder, f"{stem}.sbpcfg")

            if os.path.isfile(cfg):
                os.remove(cfg)

    # -------------------------
    # Upload
    # -------------------------

    def upload_blueprints(self, files, game_folder):
        """
        Copie sbp + sbpcfg dans le dossier du jeu
        """
        for bp in files:

            if not os.path.isfile(bp):
                continue

            stem = Path(bp).stem
            src_cfg = Path(bp).with_suffix(".sbpcfg")

            dest_sbp = os.path.join(game_folder, f"{stem}.sbp")
            dest_cfg = os.path.join(game_folder, f"{stem}.sbpcfg")

            if not src_cfg.exists():
                raise Exception("Fichier .sbpcfg manquant")

            shutil.copy(bp, dest_sbp)
            shutil.copy(src_cfg, dest_cfg)

    # -------------------------
    # Vérifications
    # -------------------------

    def check_sbpcfg_exists(self, files):
        """
        Vérifie que chaque sbp possède son sbpcfg
        """
        for bp in files:
            cfg = Path(bp).with_suffix(".sbpcfg")
            if not cfg.exists():
                return False
        return True

    def check_duplicates(self, files, game_folder):
        """
        Vérifie qu'aucun blueprint n'existe déjà
        """
        for bp in files:
            stem = Path(bp).stem
            dest = os.path.join(game_folder, f"{stem}.sbp")
            if os.path.isfile(dest):
                return False
        return True

    def get_blueprint_folders(self):
        base = os.path.join(
            os.getenv("LOCALAPPDATA"),
            "FactoryGame",
            "Saved",
            "SaveGames",
            "blueprints"
        )

        if not os.path.isdir(base):
            return []

        return [
            d for d in os.listdir(base)
            if os.path.isdir(os.path.join(base, d))
        ]