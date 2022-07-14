import os
import shutil
import boto3

from abc import abstractmethod, ABC
from botocore.exceptions import ClientError

from src.agent import logging, constants

logger = logging.get_logger(__name__)


class DataSender(ABC):
    @abstractmethod
    def send_file(self, file_name: str) -> bool:
        pass


class S3DataSender(DataSender):
    def __init__(self, bucket, s3_key, s3_region):
        self.bucket = bucket
        self.s3_key = s3_key
        self.s3_region = s3_region

    def send_file(self, file_name: str) -> bool:
        s3_client = boto3.client('s3')
        try:
            s3_client.upload_file(file_name, self.bucket, os.path.basename(file_name))
        except ClientError as e:
            logger.error(e)
            return False
        return True


# todo I guess I don't need dummy destination because I can write data locally, no need in a container, volumes etc.
class DummySender(DataSender):
    def send_file(self, file_name: str) -> bool:
        output_dir = os.path.join(constants.ROOT, 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        shutil.copy(file_name, output_dir)
        return True
