build-docs:
	-rm -r docs
	-rm -r docsource/internal_apis
	mkdir -p docs
	sphinx-apidoc --separate -o docsource/internal_apis src

test:
	flake8 feeds
	pytest --verbose test --cov feeds