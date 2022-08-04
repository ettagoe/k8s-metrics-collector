import os
import shutil
import boto3
import smart_open

from abc import abstractmethod, ABC
from botocore.config import Config
from botocore.exceptions import ClientError
from pathlib import Path

from agent import constants, monitoring
from agent.config_provider import config_provider
from agent.logger import logger


class DataSender(ABC):
    @abstractmethod
    def send_file(self, file_name: str) -> bool:
        pass

    @abstractmethod
    def stream_dir_to_file(self, dir_path: str, target_file: str) -> bool:
        pass


class S3DataSender(DataSender):
    def __init__(self, bucket: str, region_name: str, access_key_id: str, secret_access_key: str):
        self.bucket = bucket
        self.s3_client = boto3.client(
            's3',
            config=Config(region_name=region_name),
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )

    def send_file(self, file_name: str) -> bool:
        try:
            self.s3_client.upload_file(file_name, self.bucket, os.path.basename(file_name))
            logger.info(f'File `{file_name.split("/")[-1]}` sent to S3 bucket `{self.bucket}`')
        except ClientError as e:
            monitoring.s3_error()
            logger.error(e)
            return False
        return True

    def stream_dir_to_file(self, dir_path: str, target_file: str) -> bool:
        try:
            with smart_open.open(
                    self._get_bucket_file_url(target_file),
                    'w',
                    transport_params={'client': self.s3_client}
            ) as fout:
                fout.write('{')

                first = True
                for s in DataGenerator.generate_data(dir_path):
                    if first:
                        first = False
                    else:
                        fout.write(',')
                    fout.write(s)

                fout.write('}')
        except ClientError as e:
            monitoring.s3_error()
            logger.error(e)
            return False
        except Exception as e:
            monitoring.error()
            logger.error(e)
            return False

        return True

    def _get_bucket_file_url(self, target_file: str) -> str:
        return f's3://{self.bucket}/{self._get_target_file_path(target_file)}'

    def _get_target_file_path(self, filename: str) -> str:
        return f'{self._get_dir()}/{filename}'

    @staticmethod
    def _get_dir() -> str:
        return f'{config_provider["aws_account_id"]}__{config_provider["aws_linked_account_id"]}/{config_provider["cluster_name"]}'


class DummySender(DataSender):
    def send_file(self, file_name: str) -> bool:
        output_dir = os.path.join(constants.DATA_DIR, 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        shutil.copy(file_name, output_dir)
        return True

    def stream_dir_to_file(self, dir_path: str, target_file: str):
        output_dir = os.path.join(constants.DATA_DIR, 'output')
        with open(os.path.join(output_dir, target_file), 'w') as f:
            f.write('{')

            first = True
            for s in DataGenerator.generate_data(dir_path):
                if first:
                    first = False
                else:
                    f.write(',')
                f.write(s)

            f.write('}')


class DataGenerator:
    @staticmethod
    def generate_data(metrics_dir: str) -> str:
        for file in os.listdir(metrics_dir):
            if file.endswith('.json'):
                with open(os.path.join(metrics_dir, file), 'r') as f:
                    yield f'"{Path(file).stem}": {f.read()}'
