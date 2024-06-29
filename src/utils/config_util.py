import configparser


def update_config(filename, section, key, value):
    config = configparser.ConfigParser()
    config.read(filename)
    config.set(section, key, value)
    with open(filename, 'w') as configfile:
        config.write(configfile)


def read_config(filename, section, key):
    config = configparser.ConfigParser()
    config.read(filename)
    return config.get(section, key)
