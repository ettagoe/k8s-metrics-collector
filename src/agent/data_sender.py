import os
import shutil
import boto3

from abc import abstractmethod, ABC
from botocore.config import Config
from botocore.exceptions import ClientError

from agent import constants, monitoring
from agent.logger import logger


class DataSender(ABC):
    @abstractmethod
    def send_file(self, file_name: str) -> bool:
        pass


class S3DataSender(DataSender):
    def __init__(self, bucket: str, region_name: str, access_key_id: str, secret_access_key: str):
        self.bucket = bucket
        self.config = Config(
            region_name=region_name,
        )
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key

    def send_file(self, file_name: str) -> bool:
        s3_client = boto3.client(
            's3', config=self.config, aws_access_key_id=self.access_key_id, aws_secret_access_key=self.secret_access_key
        )
        try:
            s3_client.upload_file(file_name, self.bucket, os.path.basename(file_name))
            logger.info(f'File `{file_name.split("/")[-1]}` sent to S3 bucket `{self.bucket}`')
        except ClientError as e:
            monitoring.s3_error()
            logger.error(e)
            return False
        return True


class DummySender(DataSender):
    def send_file(self, file_name: str) -> bool:
        output_dir = os.path.join(constants.DATA_DIR, 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        shutil.copy(file_name, output_dir)
        return True
