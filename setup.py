from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {
    'packages': [],
    'excludes': [],
    'include_files': [
        'icone.ico',
        'locale/'
    ],
}

base = 'gui'

executables = [
    Executable('run.py', base=base, icon='icone.ico')
]

setup(name='satisfactory_blueprint_manager',
      version='1.2.0',
      description='Blueprint Manager is a tool designed for Satisfactory players to facilitate blueprint management',
      options={'build_exe': build_options},
      executables=executables)
