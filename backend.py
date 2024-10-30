import sqlite3
from datetime import datetime
import os
import shutil
from pathlib import Path

def create_database_connection():
    try:
        conn = sqlite3.connect(os.getenv('LOCALAPPDATA') + '/satisfactory_blueprint_manager.db')
        return conn
    except sqlite3.Error as err:
        print(f"Error connecting to the database: {err}")
        return None

def create_config_table():
    try:
        conn = create_database_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                value TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
    except sqlite3.Error as err:
        print(f"Error creating config table: {err}")

def execute_query(query, params=None):
    try:
        conn = create_database_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except sqlite3.Error as err:
        print(f"Error executing query: {err}")
        return []


def create_config(title='', value=''):
    insert_query = "INSERT INTO config (title, value) VALUES (?, ?)"
    params = (title, value)
    execute_query(insert_query, params)
    print("Config created successfully.")

def get_config_by_title(title):
    select_query = "SELECT * FROM config WHERE title = ?"
    params = (title,)
    results = execute_query(select_query, params)
    if len(results) == 1:
        print(f"Retrieved config {title} successfully.")
        result = results[0]
    else:
        print(f"Config {title} not found.")
        result = None
    return result

def update_config(title, new_value):
    print('trying to update')
    update_query = "UPDATE config SET value = ?, updated_at = ? WHERE title = ?"
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    params = (new_value, now, title)
    execute_query(update_query, params)
    print(f"Updated config {title} successfully.")


def list_bp_from_game_folder():
    game_folder_data = get_config_by_title(title='game_folder')
    game_folder = game_folder_data[2]
    fichiers_sbp = []
    i=0
    for f in os.listdir(game_folder):
      if f.endswith('.sbp'):
          fichiers_sbp.append({ 'id': i, 'blueprint': f })
          i += 1
    return fichiers_sbp

def delete_bp_from_game_folder(bp_file):
    game_folder_data = get_config_by_title(title='game_folder')
    game_folder = game_folder_data[2]
    full_file = game_folder + '/' + bp_file
    print(full_file)
    if os.path.isfile(full_file):
        os.remove(full_file)
        print('Removing %s' % full_file)
        # trying the sbpc file
        file_without_extension = Path(full_file).stem
        sbpcfg_file = game_folder + '/' + file_without_extension + '.sbpcfg'
        if os.path.isfile(sbpcfg_file):
            os.remove(sbpcfg_file)
            print('Removing %s' % sbpcfg_file)

def check_upload_blueprints(blueprints):
    game_folder_data = get_config_by_title(title='game_folder')
    game_folder = game_folder_data[2]    
    for bp in blueprints:
      full_file_without_extension = str(Path(bp).parent) + '/' + str(Path(bp).stem)
      sbpcfg_file_source = full_file_without_extension + '.sbpcfg'
      print('Checking if %s exists' % sbpcfg_file_source)
      if not os.path.isfile(sbpcfg_file_source):    
        return False
        break
    return True

def upload_blueprints(blueprints):
    game_folder_data = get_config_by_title(title='game_folder')
    game_folder = game_folder_data[2]    
    for bp in blueprints:
        if os.path.isfile(bp):
          full_file_without_extension = str(Path(bp).parent) + '/' + str(Path(bp).stem)
          file_without_extension = Path(bp).stem
          sbp_file_destination = game_folder + '/' + file_without_extension + '.sbp'
          sbpcfg_file_destination = game_folder + '/' + file_without_extension + '.sbpcfg'
          sbpcfg_file_source = full_file_without_extension + '.sbpcfg'
          shutil.copy(bp, sbp_file_destination)
          shutil.copy(sbpcfg_file_source, sbpcfg_file_destination)