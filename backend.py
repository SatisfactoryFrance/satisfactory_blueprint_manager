﻿import os
import shutil
from pathlib import Path
import json
from tkinter import filedialog
import re


class Backend():

    def __init__(self):
        self.config_file = os.getenv('LOCALAPPDATA') + '\\satisfactory_blueprint_manager.json'

    def check_config_file(self):
        print('Checking config file %s' % self.config_file)
        if os.path.isfile(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            startup_config = {'lang': 'fr', 'game_folder': 'undefined'}
            self.config = startup_config
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(startup_config, f, indent=4, ensure_ascii=False)

    def set_config(self, title, new_value):
        self.config[title] = new_value
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def delete_bp_from_game_folder(self, bp_file):
        game_folder = self.config['game_folder']
        full_file = game_folder + '/' + bp_file
        if os.path.isfile(full_file):
            os.remove(full_file)
            print('Removing %s' % full_file)
            # trying the sbpc file
            file_without_extension = Path(full_file).stem
            sbpcfg_file = game_folder + '/' + file_without_extension + '.sbpcfg'
            if os.path.isfile(sbpcfg_file):
                os.remove(sbpcfg_file)
                print('Removing %s' % sbpcfg_file)

    def check_blueprints_cbpcfg(self, blueprints):
        for bp in blueprints:
            full_file_without_extension = str(Path(bp).parent) + '/' + str(Path(bp).stem)
            sbpcfg_file_source = full_file_without_extension + '.sbpcfg'
            print('Checking if %s exists' % sbpcfg_file_source)
            if not os.path.isfile(sbpcfg_file_source):
                return False
                break
        return True

    def check_if_same_blueprints(self, blueprints):
        game_folder = self.config['game_folder']
        for bp in blueprints:
            file = str(Path(bp).stem) + '.sbp'
            full_file = game_folder + '/' + file
            print('Checking if %s already exists' % full_file)
            if os.path.isfile(full_file):
                return False
                break
        return True

    def upload_blueprints(self, blueprints):
        game_folder = self.config['game_folder']
        for bp in blueprints:
            if os.path.isfile(bp):
                full_file_without_extension = str(Path(bp).parent) + '/' + str(Path(bp).stem)
                file_without_extension = Path(bp).stem
                sbp_file_destination = game_folder + '/' + file_without_extension + '.sbp'
                sbpcfg_file_destination = game_folder + '/' + file_without_extension + '.sbpcfg'
                sbpcfg_file_source = full_file_without_extension + '.sbpcfg'
                shutil.copy(bp, sbp_file_destination)
                shutil.copy(sbpcfg_file_source, sbpcfg_file_destination)

    def get_blueprint_folders(self):
        """Recupere tous les dossiers dans le repertoire blueprints."""
        chemin_base = os.path.join(os.getenv("LOCALAPPDATA"), "FactoryGame", "Saved", "SaveGames", "blueprints")
        if not os.path.exists(chemin_base):
            return []
        return [d for d in os.listdir(chemin_base) if os.path.isdir(os.path.join(chemin_base, d))]

    def sanitize_filename(self, filename):
        """ Python aime pas les caractéres spéciaux"""
        return re.sub(r'[<>:"/\\|?*]', '_', filename)
