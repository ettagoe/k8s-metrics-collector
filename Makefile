all: run-all _setup-victoria

rerun: _clean-docker-volumes all

_clean-docker-volumes:
	docker-compose down -v --remove-orphans

run-all:
	docker-compose up -d
	sleep 15

_setup-victoria:
	./scripts/upload-test-data-to-victoria.sh
