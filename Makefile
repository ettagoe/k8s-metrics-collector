all: run-victoria _setup-victoria

rerun: _clean-docker-volumes all

_clean-docker-volumes:
	docker-compose down -v --remove-orphans

run-victoria:
	docker-compose up -d victoriametrics
	sleep 15

_setup-victoria:
	./scripts/upload-test-data-to-victoria.sh
