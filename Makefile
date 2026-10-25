PYTHON ?= python3

.PHONY: test demo
test:
	$(PYTHON) -m pytest

demo:
	$(PYTHON) -m redloop run --all --agent naive
	$(PYTHON) -m redloop run --all --agent guarded
