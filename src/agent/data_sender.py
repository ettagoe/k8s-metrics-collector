from abc import abstractmethod, ABC


class DataSender(ABC):
    @abstractmethod
    def send(self, data):
        pass


class S3DataSender(DataSender):
    def __init__(self, s3_bucket, s3_key, s3_region):
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.s3_region = s3_region

    def send(self, data):
        pass
