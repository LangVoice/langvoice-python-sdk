.PHONY: help install install-dev clean lint format test build publish publish-test all

# Variables - Use python instead of python3 for Windows compatibility
ifeq ($(OS),Windows_NT)
    PYTHON := python
    # Windows-compatible delete commands using Python
    RM_DIR = $(PYTHON) -c "import shutil, os; [shutil.rmtree(d, ignore_errors=True) for d in ['$(1)'] if os.path.exists(d)]"
    RM_PATTERN = $(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(str(p), ignore_errors=True) if p.is_dir() else p.unlink(missing_ok=True) for p in pathlib.Path('.').rglob('$(1)')]"
else
    PYTHON := python3
    RM_DIR = rm -rf $(1)
    RM_PATTERN = find . -type f -name "$(1)" -delete 2>/dev/null || true; find . -type d -name "$(1)" -exec rm -rf {} + 2>/dev/null || true
endif

PIP := $(PYTHON) -m pip
PACKAGE_NAME := langvoice

help:
	@echo "LangVoice SDK - Available commands:"
	@echo ""
	@echo "  make install        Install package"
	@echo "  make install-dev    Install package with dev dependencies"
	@echo "  make clean          Remove build artifacts"
	@echo "  make lint           Run linters"
	@echo "  make format         Format code with black"
	@echo "  make test           Run tests"
	@echo "  make build          Build package"
	@echo "  make publish-test   Publish to TestPyPI"
	@echo "  make publish        Publish to PyPI"
	@echo "  make all            Clean, lint, test, build, and publish"
	@echo ""

install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[all,dev]"

install-all:
	$(PIP) install -e ".[all]"

clean:
	$(PYTHON) -c "import shutil, os; dirs = ['build', 'dist', '.pytest_cache', '.mypy_cache', '.ruff_cache']; [shutil.rmtree(d, ignore_errors=True) for d in dirs]"
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(str(p), ignore_errors=True) for p in pathlib.Path('.').rglob('*.egg-info')]"
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(str(p), ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
	$(PYTHON) -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.pyc') if p.is_file()]"

lint:
	$(PYTHON) -m ruff check src/ tests/
	$(PYTHON) -m mypy src/

format:
	$(PYTHON) -m black src/ tests/
	$(PYTHON) -m ruff check --fix src/ tests/

test:
	$(PYTHON) -m pytest tests/ -v

build: clean
	$(PYTHON) -m build

publish-test: build
	$(PYTHON) -m twine upload --repository testpypi dist/*

publish: build
	$(PYTHON) -m twine upload dist/*

# Complete workflow: clean, format, lint, test, build, and publish
all: clean format lint test build publish

# Development workflow: format, lint, and test
dev: format lint test

# Quick build and test publish
quick-test: clean build publish-test

# Setup PyPI credentials (run once)
setup-pypi:
	@echo "Creating .pypirc file..."
	@$(PYTHON) -c "import os; home = os.path.expanduser('~'); f = open(os.path.join(home, '.pypirc'), 'w'); f.write('[pypi]\nusername = __token__\npassword = <your-pypi-token>\n\n[testpypi]\nusername = __token__\npassword = <your-testpypi-token>\n'); f.close()"
	@echo "Please edit ~/.pypirc and add your API tokens"

# Version bump helpers using Python for cross-platform compatibility
bump-patch:
	@echo "Bumping patch version..."
	@$(PYTHON) -c "import re; \
		content = open('pyproject.toml').read(); \
		match = re.search(r'version = \"(\\d+)\\.(\\d+)\\.(\\d+)\"', content); \
		major, minor, patch = match.groups(); \
		new_version = f'{major}.{minor}.{int(patch)+1}'; \
		content = re.sub(r'version = \"\\d+\\.\\d+\\.\\d+\"', f'version = \"{new_version}\"', content); \
		open('pyproject.toml', 'w').write(content)"

bump-minor:
	@echo "Bumping minor version..."
	@$(PYTHON) -c "import re; \
		content = open('pyproject.toml').read(); \
		match = re.search(r'version = \"(\\d+)\\.(\\d+)\\.(\\d+)\"', content); \
		major, minor, patch = match.groups(); \
		new_version = f'{major}.{int(minor)+1}.0'; \
		content = re.sub(r'version = \"\\d+\\.\\d+\\.\\d+\"', f'version = \"{new_version}\"', content); \
		open('pyproject.toml', 'w').write(content)"

bump-major:
	@echo "Bumping major version..."
	@$(PYTHON) -c "import re; \
		content = open('pyproject.toml').read(); \
		match = re.search(r'version = \"(\\d+)\\.(\\d+)\\.(\\d+)\"', content); \
		major, minor, patch = match.groups(); \
		new_version = f'{int(major)+1}.0.0'; \
		content = re.sub(r'version = \"\\d+\\.\\d+\\.\\d+\"', f'version = \"{new_version}\"', content); \
		open('pyproject.toml', 'w').write(content)"
