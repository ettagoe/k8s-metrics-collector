import json
import os
import time

from src.agent import repository
from src.agent.config_provider import config_provider
from src.agent.data_sender import DataSender
from src.agent.metrics_retriever import MetricsRetriever
from src.agent.offset_manager import OffsetManager
from src.agent.time import Interval
from src.agent.transformer import Transformer


class Stages:
    RETRIEVE = 'retrieve'
    TRANSFORM = 'transform'
    SEND = 'send'


class State:
    def __init__(self, stage: str):
        self.stage = stage
        self.items = self._get_items()
        self._load_items_state()

    def to_dict(self):
        # todo I don't need to keep items? I load them every time
        return {
            'stage': self.stage,
        }

    @staticmethod
    def from_json(json_data: dict):
        return State(json_data['stage'])

    @staticmethod
    def initial_state():
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

    def _get_current_stage_dir(self):
        if self.stage == Stages.RETRIEVE:
            return config_provider['metrics_dir']
        elif self.stage in [Stages.TRANSFORM, Stages.SEND]:
            return config_provider['grouped_metrics_dir']

    def _get_items(self):
        if self.stage == Stages.RETRIEVE:
            return list(config_provider['metric_queries'].keys())
        elif self.stage in [Stages.TRANSFORM, Stages.SEND]:
            return list(config_provider['metric_groups'].keys())

    def _load_items_state(self):
        if self.stage == Stages.RETRIEVE:
            for file in os.listdir(self._get_current_stage_dir()):
                self.items.pop(self.items.index(file))


class Director:
    def __init__(
            self,
            metrics_retriever: MetricsRetriever,
            transformer: Transformer,
            data_sender: DataSender,
            offset_manager: OffsetManager,
            interval: Interval,
            metric_queries: dict,
    ):
        self.state = self._get_state()
        self.interval = interval
        self.metrics_retriever = metrics_retriever
        self.data_sender = data_sender
        self.transformer = transformer
        self.offset_manager = offset_manager
        self.grouped_metrics_dir = config_provider['grouped_metrics_dir']
        self.metric_queries = metric_queries

    @property
    def stage(self) -> str:
        return self.state.stage

    def run(self):
        if self.stage == Stages.RETRIEVE:
            self._retrieve()

        if self.stage == Stages.TRANSFORM:
            self._transform()

        if self.stage == Stages.SEND:
            self._send()

    def should_run(self) -> bool:
        # todo time.time(), potential problems with timezones?
        return (
                self.stage != Stages.RETRIEVE
                or self.offset_manager.get_offset() < time.time() - self.interval.total_seconds()
        )

    @staticmethod
    def _get_state() -> State:
        # todo test empty config
        if state := repository.get_state():
            return state
        state = State.initial_state()
        repository.save_state(state)
        return state

    def _retrieve(self):
        self.metrics_retriever.fetch_metrics(
            config_provider['metric_queries'],
            self.offset_manager.get_offset(),
            self.interval
        )
        self.state.increment_stage()

    def _transform(self):
        metrics = {}
        for file in os.listdir(config_provider['metrics_dir']):
            with open(os.path.join(config_provider['metrics_dir'], file), 'r') as f:
                metrics[file] = json.load(f)

        grouped_metrics = self.transformer.group_metrics(metrics)
        for group, metrics in grouped_metrics.items():
            file_name = os.path.join(
                self.grouped_metrics_dir,
                f'{group}_{self.offset_manager.get_offset()}_{self.interval.total_seconds()}'
            )
            with open(file_name, 'w') as f:
                json.dump(metrics, f)

        self.state.increment_stage()
        self._clear_metrics_dir()

    @staticmethod
    def _clear_metrics_dir():
        for file in os.listdir(config_provider['metrics_dir']):
            os.remove(os.path.join(config_provider['metrics_dir'], file))

    def _send(self):
        for file in os.listdir(self.grouped_metrics_dir):
            self.data_sender.send_file(os.path.join(self.grouped_metrics_dir, file))
            self._delete_sent_file(file)
        self.state.increment_stage()

    def _delete_sent_file(self, file_name: str):
        os.remove(os.path.join(self.grouped_metrics_dir, file_name))
