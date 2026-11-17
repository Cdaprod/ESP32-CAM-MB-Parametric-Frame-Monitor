PYTHON ?= python
.PHONY: build validate render all docs
build:
	$(PYTHON) src/build_v006.py
validate: build
	$(PYTHON) src/validate_v006.py
render: validate
	$(PYTHON) src/render_v006.py
all: render
docs:
	$(PYTHON) tests/test_repo_assets.py
