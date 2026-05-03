.PHONY: install lint test dev

install:
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev]"
	pre-commit install

lint:
	ruff check .
	isort --check-only .
	black --check .
	mypy .

format:
	black .
	isort .

test:
	python manage.py test

dev:
	python manage.py runserver
