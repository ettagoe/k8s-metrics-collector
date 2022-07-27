FROM python:3.10.5-alpine3.15

WORKDIR /usr/src/app

COPY . .

RUN mkdir /usr/src/app/data
RUN mkdir /usr/src/app/data/metrics
RUN mkdir /usr/src/app/data/grouped_metrics

RUN pip install -r requirements.txt
RUN python setup.py install

CMD ["python", "/usr/src/app/src/agent/main.py"]
