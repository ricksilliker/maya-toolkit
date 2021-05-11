import os
import json


DRAGONFLY_CONFIG = os.path.join(os.path.expanduser('~'), '.dragonflyrc').replace('\\', '/')
DRAGONFLY_DIR = os.path.join(os.path.expanduser('~'), '.dragonfly').replace('\\', '/')


def get_dragonfly_dir():
    if not os.path.isdir(DRAGONFLY_DIR):
        os.mkdir(DRAGONFLY_DIR)
    return DRAGONFLY_DIR


def get_dragonfly_tmp():
    get_dragonfly_dir()
    tmp_dir = os.path.join(DRAGONFLY_DIR, 'tmp')
    if not os.path.isdir(tmp_dir):
        os.mkdir(tmp_dir)
    return tmp_dir


def get_build_dir():
    build_dir = os.path.join(get_dragonfly_tmp(), '_build')
    if not os.path.isdir(build_dir):
        os.mkdir(build_dir)
    return build_dir


def create_dragonfly_config():
    default_data = dict()
    default_data['plugins'] = []

    if not os.path.isfile(DRAGONFLY_CONFIG):
        with open(DRAGONFLY_CONFIG, 'w') as fp:
            json.dump(default_data, fp, indent=2)


def _unicode_to_str(data, ignore_dicts=False):
    """Converts unicode data to a string type.

    The only point of this is json in python2.7 by default converts strings to unicode when dumping and loading.

    Args:
        data: Some value to try to convert
        ignore_dicts: Skip dictionary objects completely

    Returns:
        Same value converted to string data instead of unicode.
    """
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_unicode_to_str(item, ignore_dicts=True) for item in data]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _unicode_to_str(key, ignore_dicts=True): _unicode_to_str(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data


def load_dragonfly_config():
    if not os.path.isfile(DRAGONFLY_CONFIG):
        create_dragonfly_config()

    with open(DRAGONFLY_CONFIG, 'r') as fp:
        result = json.load(fp, object_hook=_unicode_to_str)
    return result


def get_plugin_paths():
    config = load_dragonfly_config()
    return config['plugins']


def add_plugin_path(paths):
    cfg = load_dragonfly_config()

    for path in paths:
        cfg['plugins'].append(path)

    with open(DRAGONFLY_CONFIG, 'w') as fp:
        json.dump(cfg, fp, indent=2)


if __name__ == '__main__':
    create_dragonfly_config()
