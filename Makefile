all: run-all _setup-victoria

rerun: _clean-docker-volumes all

_clean-docker-volumes:
	docker-compose down -v --remove-orphans

run-victoria: _up-victoria sleep _setup-victoria

_up-victoria:
	docker-compose up -d victoriametrics

run-all: run-victoria
	docker-compose up -d agent

stop:
	rm -rf data/grouped_metrics/*
	rm -rf data/metrics/*
	rm -rf data/output/*
	rm data/offsets.json
	rm data/state.json
	docker-compose down -v --remove-orphans

_setup-victoria:
	./scripts/upload-test-data-to-victoria.sh

sleep:
	sleep 15
