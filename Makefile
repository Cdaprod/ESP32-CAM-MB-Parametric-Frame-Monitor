PYTHON ?= python
.PHONY: build validate render test all
build:
	$(PYTHON) src/build.py build
validate:
	$(PYTHON) src/build.py validate
render:
	xvfb-run -a $(PYTHON) src/build.py render
test:
	$(PYTHON) tests/test_v010_outputs.py
all: build validate render test
