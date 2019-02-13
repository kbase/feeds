GITCOMMIT = $(shell git rev-parse HEAD)

all:
	echo "# Don't check this file into git please" > feeds/gitcommit.py
	echo 'commit = "$(GITCOMMIT)"' >> feeds/gitcommit.py

install:
	pip install -r requirements.txt
	pip install -r dev-requirements.txt

docs:
	-rm -r docs
	-rm -r docsource/internal_apis
	mkdir -p docs
	sphinx-apidoc --separate -o docsource/internal_apis feeds

test: all
	flake8 feeds
	# flake8 test
	pytest --verbose test --cov=feeds --cov-report html feeds -s

start_kafka_listener:
	python -m feeds.kafka_listener

start: all
	gunicorn --worker-class gevent --timeout 300 --workers 5 --bind :5000 feeds.server:app

.PHONY: test docs
