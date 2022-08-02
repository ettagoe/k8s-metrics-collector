import os

from agent import repository
from agent.config_provider import config_provider
from agent.logger import logger


class Stages:
    RETRIEVE = 'retrieve'
    TRANSFORM = 'transform'
    SEND = 'send'


class State:
    def __init__(self, stage: str):
        self.stage = stage
        self.items = self._get_items()
        self.grouped_items = self._get_grouped_items()
        self._load_items_state()

    def to_dict(self):
        return {
            'stage': self.stage,
        }

    @staticmethod
    def from_json(json_data: dict):
        return State(json_data['stage'])

    @staticmethod
    def init():
        return State(stage=Stages.RETRIEVE)

    def increment_stage(self):
        if self.stage == Stages.RETRIEVE:
            self.stage = Stages.TRANSFORM
        elif self.stage == Stages.TRANSFORM:
            self.stage = Stages.SEND
        elif self.stage == Stages.SEND:
            self.stage = Stages.RETRIEVE
        self.items = self._get_items()
        repository.save_state(self)
        logger.info(f'Stage changed to {self.stage}')

    def _get_current_stage_dir(self):
        if self.stage == Stages.RETRIEVE:
            return config_provider['metrics_dir']
        elif self.stage in [Stages.TRANSFORM, Stages.SEND]:
            return config_provider['grouped_metrics_dir']

    def _get_items(self) -> dict:
        if self.stage == Stages.RETRIEVE:
            return config_provider['metric_queries']
        elif self.stage in [Stages.TRANSFORM, Stages.SEND]:
            return config_provider['metric_groups']

    @staticmethod
    def _get_grouped_items() -> dict:
        return config_provider['metrics']

    def _load_items_state(self):
        if self.stage == Stages.RETRIEVE:
            for file in os.listdir(self._get_current_stage_dir()):
                if file.endswith('.json'):
                    # todo -5 so so
                    self.items.pop(file[:-5])
        if self.stage == Stages.TRANSFORM:
            for file in os.listdir(self._get_current_stage_dir()):
                self.items.pop(file.split('_')[0])
