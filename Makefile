# Détection automatique Windows vs Unix
ifeq ($(OS),Windows_NT)
    PYTHON   := python
    PIP      := pip
    RM       := rmdir /s /q
    RMFILE   := del /f /q
else
    PYTHON   := python3
    PIP      := pip3
    RM       := rm -rf
    RMFILE   := rm -f
endif

install:
	$(PIP) install -e ".[dev]"

test:
	pytest tests/ -v --tb=short

test-file:
	pytest $(FILE) -v --tb=short

lint:
	ruff check sangho/ tests/
	ruff format --check sangho/ tests/

format:
	ruff format sangho/ tests/
	ruff check --fix sangho/ tests/

typecheck:
	mypy sangho/

build:
	$(PYTHON) -m build

publish-test:
	twine upload --repository testpypi dist/*

publish:
	twine upload dist/*

clean:
ifeq ($(OS),Windows_NT)
	if exist dist      rmdir /s /q dist
	if exist build     rmdir /s /q build
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist .mypy_cache   rmdir /s /q .mypy_cache
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
else
	rm -rf dist/ build/ *.egg-info .pytest_cache .mypy_cache __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
endif

.PHONY: install test test-file lint format typecheck build publish-test publish clean
