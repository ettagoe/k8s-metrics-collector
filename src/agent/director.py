import json
import os
import time

from enum import Enum

from src.agent import repository
from src.agent.data_sender import DataSender
from src.agent.metrics_retriever import MetricsRetriever
from src.agent.offset_manager import OffsetManager
from src.agent.time import Interval
from src.agent.transformer import Transformer


class Stages:
    RETRIEVE = 'retrieve'
    TRANSFORM = 'transform'
    SEND = 'send'


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
        self.metrics_dir = self.state.get('metrics_dir')
        self.grouped_metrics_dir = self.state.get('grouped_metrics_dir')
        self.metric_queries = metric_queries

    @property
    def stage(self) -> str:
        return self.state['stage']

    @stage.setter
    def stage(self, stage: str):
        self.state['stage'] = stage

    @property
    def metrics_to_fetch(self) -> dict:
        return self.state['metrics_to_fetch'] if 'metrics_to_fetch' in self.state else self.metric_queries

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
    def _get_state() -> dict:
        # todo test empty config
        if state := repository.get_state():
            return state
        state = {
            'stage': Stages.RETRIEVE,
        }
        repository.save_state(state)
        return state

    def _retrieve(self):
        self.metrics_dir = self.metrics_retriever.fetch_metrics(self.metrics_to_fetch, self.interval)
        self._increment_stage()

    def _transform(self):
        self.grouped_metrics_dir = self.transformer.group_metrics(self.metrics_dir)
        self._increment_stage()

    def _send(self):
        for file_name, group in self._load_grouped_metrics().items():
            self.data_sender.send(group)
            self._delete_sent_group(file_name)
        self._increment_stage()

    def _load_grouped_metrics(self) -> dict:
        for file in os.listdir(self.grouped_metrics_dir):
            with open(os.path.join(self.grouped_metrics_dir, file), 'r') as f:
                yield file, json.load(f)

    def _delete_sent_group(self, file_name: str):
        os.remove(os.path.join(self.grouped_metrics_dir, file_name))

    def _increment_stage(self):
        # todo add other things to state?
        if self.stage == Stages.RETRIEVE:
            self.stage = Stages.TRANSFORM
        elif self.stage == Stages.TRANSFORM:
            self.stage = Stages.SEND
        elif self.stage == Stages.SEND:
            self.stage = Stages.RETRIEVE
        repository.save_state(self.state)
