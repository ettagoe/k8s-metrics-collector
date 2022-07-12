import json
import os

from src.agent.config_provider import config_provider


def get_offsets() -> {}:
    offsets_path = config_provider['offset_storage_path']
    if not os.path.isfile(offsets_path):
        with open(offsets_path, 'w'):
            return {}
    with open(offsets_path, 'r') as f:
        # todo what if it's empty?
        if offsets := json.load(f):
            return offsets


def save_offsets(offsets: {}):
    # todo save update time?
    with open(config_provider['offset_storage_path'], 'w') as f:
        json.dump(offsets, f)
