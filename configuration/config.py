import yaml
import os

CONFIG_FILE_LOCATION = os.path.join(os.path.dirname(__file__), 'config.yaml')

config = None

with open(CONFIG_FILE_LOCATION) as f:
    config = yaml.safe_load(f)

BOT_TOKEN = config['bot']
ADDRESSES = config['addresses']