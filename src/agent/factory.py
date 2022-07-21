from src.agent import data_sender, monitoring
from src.agent.config_provider import config_provider


def get_sender():
    if config_provider['environment'] == 'production':
        return data_sender.S3DataSender(
            config_provider['s3_bucket'],
        )
    else:
        return data_sender.DummySender()


def get_monitoring_client():
    monitoring_type = config_provider.get('monitoring_type', monitoring.INSTANT_MONITORING)
    if monitoring_type == monitoring.INSTANT_MONITORING:
        return monitoring.InstantMonitoringClient(config_provider['monitoring_token'])
    elif monitoring_type == monitoring.ACCUMULATIVE_MONITORING:
        raise NotImplementedError('Accumulative monitoring is not implemented yet')
