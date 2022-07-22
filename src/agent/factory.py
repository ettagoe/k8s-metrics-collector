from src.agent import data_sender, monitoring, metrics_retriever, transformer, offset_manager, director, time
from src.agent.config_provider import config_provider


def get_sender():
    if config_provider['data_sender'] == 'real':
        return data_sender.S3DataSender(
            config_provider['s3_bucket'],
        )
    elif config_provider['data_sender'] == 'dummy':
        return data_sender.DummySender()


def get_monitoring_client():
    if config_provider['monitoring'] == 'dummy':
        return monitoring.DummyMonitoringClient()
    monitoring_type = config_provider.get('monitoring_type', monitoring.INSTANT_MONITORING)
    if monitoring_type == monitoring.INSTANT_MONITORING:
        return monitoring.InstantMonitoringClient(config_provider['monitoring_token'])
    elif monitoring_type == monitoring.ACCUMULATIVE_MONITORING:
        raise NotImplementedError('Accumulative monitoring is not implemented yet')


def get_metrics_retriever():
    return metrics_retriever.PrometheusAsyncMetricsRetriever(config_provider.get('prometheus_url'))


def get_transformer():
    return transformer.Transformer(config_provider['metric_groups'])


def get_offset_manager():
    return offset_manager.OffsetManager(config_provider['initial_offset'])


def get_director():
    return director.Director(
        get_metrics_retriever(),
        get_transformer(),
        get_sender(),
        get_offset_manager(),
        time.Interval(config_provider['interval']),
        config_provider['metric_queries'],
    )
