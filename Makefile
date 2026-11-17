PYTHON ?= python
.PHONY: build validate render all docs test check
build:
	$(PYTHON) src/build_v006.py
validate: build
	$(PYTHON) src/validate_v006.py
render: validate
	$(PYTHON) src/render_v006.py
docs:
	$(PYTHON) tests/test_repo_assets.py
test: docs
check: docs
all: render docs
