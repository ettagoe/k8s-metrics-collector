import os
import time

from agent import repository, monitoring, state
from agent.config_provider import config_provider
from agent.data_sender import DataSender
from agent.logger import logger
from agent.metrics_retriever import MetricsRetriever
from agent.monitoring import monitor_exec_time
from agent.offset_manager import OffsetManager
from agent.state import State
from agent.time import Interval
from agent.transformer import Transformer


class Director:
    def __init__(
            self,
            metrics_retriever: MetricsRetriever,
            transformer: Transformer,
            data_sender: DataSender,
            offset_manager: OffsetManager,
            interval: Interval,
    ):
        self.state = self._get_state()
        self.interval = interval
        self.metrics_retriever = metrics_retriever
        self.data_sender = data_sender
        self.transformer = transformer
        self.offset_manager = offset_manager

    @property
    def stage(self) -> str:
        return self.state.stage

    def run(self):
        if self.stage == state.Stages.RETRIEVE:
            self._retrieve()

        if self.stage == state.Stages.SEND:
            self._send()

        self._increment_offset()

    def _increment_offset(self):
        self.offset_manager.increment_offset()
        repository.save_offset(self.offset_manager.get_offset())
        logger.info(f'Incremented offset to: {self.offset_manager.get_offset()}')

    def should_run(self) -> bool:
        return (
                self.stage != state.Stages.RETRIEVE
                or self.offset_manager.get_offset() < time.time() - self.interval.total_seconds()
        )

    @staticmethod
    def _get_state() -> State:
        if state_ := repository.get_state():
            return state_
        state_ = State.init()
        repository.save_state(state_)
        return state_

    @monitor_exec_time(monitoring.RETRIEVE_STAGE_DURATION)
    def _retrieve(self):
        logger.info('Running stage: retrieve')

        self.metrics_retriever.fetch_groups(
            self.state.grouped_items,
            self.offset_manager.get_offset(),
            self.interval,
            config_provider['metrics_dir']
        )
        self.state.increment_stage()

    @monitor_exec_time(monitoring.SEND_STAGE_DURATION)
    def _send(self):
        logger.info('Running stage: send')

        groups = ['cluster', 'node', 'pod', 'container']
        for group in groups:
            curr_dir = os.path.join(config_provider['metrics_dir'], group)
            self.data_sender.stream_dir_to_file(
                curr_dir,
                f'{group}_{self.offset_manager.get_offset()}_{self.interval.total_seconds()}.json.gz',
            )
            self._clear_directory(curr_dir)

        self.state.increment_stage()

    @staticmethod
    def _clear_directory(directory: str):
        for file in os.listdir(directory):
            os.remove(os.path.join(directory, file))
            logger.info(f'Deleted raw metrics file `{file}`')
