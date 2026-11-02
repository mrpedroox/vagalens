.PHONY: install lint format typecheck test check eval clean

install:
	pip install -e ".[dev]"
	pre-commit install

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

typecheck:
	mypy

test:
	pytest

check: lint typecheck test

eval:
	@echo "Evaluation is not implemented yet (planned for v0.8)."

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache build dist *.egg-info
