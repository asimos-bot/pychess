# Translate asset paths to useable format for PyInstaller
import os
import sys
from pathlib import Path


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


def get_assets_folder():
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS).joinpath('assets')
    return Path(__file__).parent.parent.joinpath('assets')


ASSETS_FOLDER = get_assets_folder()
