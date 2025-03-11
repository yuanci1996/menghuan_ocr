import configparser
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, os.pardir))
config_path = os.path.normpath(os.path.join(project_root, "static", "config", "config.ini"))


def update_config(section, key, value):
    config = configparser.ConfigParser()
    config.read(config_path)
    config.set(section, key, value)
    with open(config_path, 'w') as configfile:
        config.write(configfile)


def read_config(section, key):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config.get(section, key)
