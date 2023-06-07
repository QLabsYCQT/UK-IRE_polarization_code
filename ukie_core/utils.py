import os
import questionary
import json
import re


# patterns from https://docs.python.org/3/library/re.html#simulating-scanf
int_pattern = r'[-+]?\d+'
float_pattern = r'[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?'


def load_config():
    config_path = os.environ.get('UKIE_CONFIG_FILE')
    if config_path is None:
        config_path = questionary.path(
            'Please provide the path to the config file: ',
            default='config.json'
        ).ask()
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config


def validate_int(value):
    return re.fullmatch(int_pattern, value)


def validate_float(value):
    return re.fullmatch(float_pattern, value)
