from urllib.parse import urljoin

import requests


class PrometheusClient:
    def __init__(self, url, auth=None):
        # todo verify ssl?
        self.url = urljoin(url, '/api/v1/query')
        self.session = requests.Session()
        if auth:
            self.session.auth = (auth.username, auth.password)

    def query(self, query: str, time: float = None):
        params = {'query': query}
        if time:
            params['time'] = time
        # todo configurable timeout? queries could take long
        # todo do we need stream and deflate for prometheus? those were for victoria
        res = self.session.get(
            self.url,
            params=params,
            stream=True,
            headers={'Accept-Encoding': 'deflate'},
            timeout=300
        )
        res.raise_for_status()
        res = res.json()
        # todo does prometheus have the same response format as victoria?
        if res['status'] != 'success':
            raise RequestException(f'Prometheus query failed: {res}')
        return res['data']['result']


class RequestException(Exception):
    pass
