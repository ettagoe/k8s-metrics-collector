from agent import data_sender, monitoring, metrics_retriever, offset_manager, director, time
from agent.config_provider import config_provider


def get_sender():
    if config_provider['data_sender'] == 's3':
        return data_sender.S3DataSender(
            config_provider['s3_bucket'],
            config_provider['s3_region'],
            config_provider['aws_access_key_id'],
            config_provider['aws_secret_access_key'],
        )
    elif config_provider['data_sender'] == 'dummy':
        return data_sender.DummySender()
    else:
        raise ValueError(f'Unknown data sender type: {config_provider["data_sender"]}')


def get_monitoring_client():
    if config_provider['monitoring'] == 'dummy':
        return monitoring.DummyMonitoringClient()
    monitoring_type = config_provider.get('monitoring_type', monitoring.INSTANT_MONITORING)
    if monitoring_type == monitoring.INSTANT_MONITORING:
        return monitoring.InstantMonitoringClient(config_provider['monitoring_token'])
    elif monitoring_type == monitoring.ACCUMULATIVE_MONITORING:
        raise NotImplementedError('Accumulative monitoring is not implemented yet')


def get_metrics_retriever():
    return metrics_retriever.PrometheusAsyncMetricsRetriever(
        config_provider.get('prometheus_url'),
        int(config_provider['max_concurrent_requests']),
        int(config_provider.get('request_timeout', 300))
    )


def get_offset_manager():
    return offset_manager.OffsetManager(config_provider['initial_offset'])


def get_director():
    return director.Director(
        get_metrics_retriever(),
        get_sender(),
        get_offset_manager(),
        time.Interval(config_provider['interval']),
    )
