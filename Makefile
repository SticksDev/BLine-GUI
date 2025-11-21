PYTHON ?= python3
ROOT_DIR := $(shell pwd)
VENV_DIR ?= $(ROOT_DIR)/.venv
ACTIVATE := . $(VENV_DIR)/bin/activate

.PHONY: help install run fmt lint test package clean

help:
	@echo "Available targets:"
	@echo "  install  - create venv and install requirements"
	@echo "  run      - launch the GUI via main.py"
	@echo "  fmt      - run black and ruff format"
	@echo "  lint     - run ruff lint and mypy"
	@echo "  test     - run pytest suite"
	@echo "  package  - build platform-specific bundles via PySide deploy"
	@echo "  clean    - remove the virtualenv"

$(VENV_DIR)/bin/activate:
	$(PYTHON) -m venv $(VENV_DIR)

install: $(VENV_DIR)/bin/activate
	$(ACTIVATE) && pip install --upgrade pip
	$(ACTIVATE) && pip install -r $(ROOT_DIR)/requirements.txt

run:
	./scripts/dev_env.sh

fmt: install
	$(ACTIVATE) && black .
	$(ACTIVATE) && ruff format .

lint: install
	$(ACTIVATE) && ruff check .
	$(ACTIVATE) && mypy .

test: install
	$(ACTIVATE) && pytest

package: install
	$(ACTIVATE) && python scripts/package_app.py

clean:
	rm -rf $(VENV_DIR)

