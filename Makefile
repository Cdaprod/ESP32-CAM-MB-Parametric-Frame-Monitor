PYTHON ?= python
.PHONY: build validate render all docs test check
build:
	$(PYTHON) src/build.py build
validate: build
	$(PYTHON) src/build.py validate
render: validate
	$(PYTHON) src/build.py render
docs:
	$(PYTHON) tests/test_repo_assets.py
test: docs
check: docs
all: render docs
