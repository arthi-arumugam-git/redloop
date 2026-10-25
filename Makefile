PYTHON ?= python3

.PHONY: test demo
test:
	$(PYTHON) -m pytest

demo:
	$(PYTHON) -m redloop run --all --agent naive
	$(PYTHON) -m redloop run --all --agent guarded

.PHONY: attack dashboard
attack:
	$(PYTHON) -m redloop attack --all

dashboard:
	$(PYTHON) -m streamlit run dashboard/app.py
