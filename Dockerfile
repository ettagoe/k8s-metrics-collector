FROM python:3.10.5-alpine3.15

WORKDIR /usr/src/app

RUN apk add --no-cache bash

COPY ./src ./src
COPY ./requirements.txt ./
COPY ./entry.sh ./
COPY ./setup.py ./

RUN chmod 755 entry.sh

RUN mkdir /usr/src/app/data
RUN mkdir /usr/src/app/data/metrics
RUN mkdir /usr/src/app/data/metrics/cluster
RUN mkdir /usr/src/app/data/metrics/node
RUN mkdir /usr/src/app/data/metrics/pod
RUN mkdir /usr/src/app/data/metrics/container
# todo remove grouped dir?
RUN mkdir /usr/src/app/data/grouped_metrics

COPY ./data/metric_queries.json /usr/src/app/data/

RUN python setup.py develop
RUN pip install -r requirements.txt

CMD ["/usr/src/app/entry.sh"]
