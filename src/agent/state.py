import os
from copy import deepcopy

from agent import repository
from agent.config_provider import config_provider
from agent.logger import logger

METRIC_GROUPS = ['cluster', 'node', 'pod', 'container']


class Stages:
    RETRIEVE = 'retrieve'
    SEND = 'send'


class State:
    def __init__(self, stage: str):
        self.stage = stage
        self.grouped_metrics = self._get_grouped_metrics()
        self.metrics_dir = config_provider['metrics_dir']
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
            self.stage = Stages.SEND
        elif self.stage == Stages.SEND:
            self.stage = Stages.RETRIEVE
            self.grouped_metrics = self._get_grouped_metrics()
        repository.save_state(self)
        logger.info(f'Stage changed to {self.stage}')

    @staticmethod
    def _get_grouped_metrics() -> dict:
        return deepcopy(config_provider['metrics'])

    def _load_items_state(self):
        if self.stage == Stages.RETRIEVE:
            for group in METRIC_GROUPS:
                for file in os.listdir(os.path.join(self.metrics_dir, group)):
                    if file.endswith('.json'):
                        # todo -5 so so
                        self.grouped_metrics[group].pop(file[:-5])
