from src.agent import data_sender
from src.agent.config_provider import config_provider


def get_sender():
    if config_provider['environment'] == 'production':
        return data_sender.S3DataSender(
            config_provider['s3_bucket'],
            config_provider['s3_key'],
            config_provider['s3_region'],
        )
    else:
        return data_sender.DummySender()
