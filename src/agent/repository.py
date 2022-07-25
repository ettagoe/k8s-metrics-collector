import json
import os

from typing import Optional

from agent import state
from agent.config_provider import config_provider


def get_offset() -> Optional[int]:
    offset_file_path = config_provider['offset_file_path']
    if not os.path.isfile(offset_file_path):
        with open(offset_file_path, 'w'):
            return None

    with open(offset_file_path, 'r') as f:
        return int(res) if (res := f.read()) else None


def save_offset(offset: int):
    # todo save update time?
    with open(config_provider['offset_file_path'], 'w') as f:
        f.write(str(offset))


def get_state() -> Optional[state.State]:
    state_file_path = config_provider['state_file_path']
    if os.path.isfile(state_file_path):
        with open(state_file_path, 'r') as f:
            if state_ := f.read():
                return state.State.from_json(json.loads(state_))
    return None


def save_state(state_: state.State):
    with open(config_provider['state_file_path'], 'w') as f:
        json.dump(state_.to_dict(), f)
