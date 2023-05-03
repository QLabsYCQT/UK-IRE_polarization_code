import os
import questionary
import json


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
