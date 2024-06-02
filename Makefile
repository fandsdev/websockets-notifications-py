SOURCES := src

.DEFAULT_GOAL := install-dev-deps

install-dev-deps: dev-deps
	uv pip sync requirements.txt dev-requirements.txt

install-deps: deps
	uv pip sync requirements.txt

deps:
	uv pip compile --output-file=requirements.txt pyproject.toml

dev-deps: deps
	uv pip compile --extra=dev --output-file=dev-requirements.txt pyproject.toml

fmt:
	ruff format $(SOURCES)
	ruff check $(SOURCES) --fix --unsafe-fixes

lint:
	dotenv-linter env.example
	ruff format --check $(SOURCES)
	ruff check $(SOURCES)
	mypy

test:
	cd src && pytest -x
	cd src && pytest --dead-fixtures
