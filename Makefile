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

# One-command end-to-end pipeline for the demo video (fresh output dir, offline).
DEMO_DIR ?= build/showcase
.PHONY: showcase
showcase:
	rm -rf $(DEMO_DIR) && mkdir -p $(DEMO_DIR)
	$(PYTHON) -m redloop list
	$(PYTHON) -m redloop attack --all --agents naive,guarded --results $(DEMO_DIR)/attack.jsonl
	$(PYTHON) -m redloop report --results $(DEMO_DIR)/attack.jsonl --out $(DEMO_DIR)/ASR.md
	$(PYTHON) -m redloop export-suite --results $(DEMO_DIR)/attack.jsonl --out $(DEMO_DIR)/suite.json
	$(PYTHON) -m redloop check-suite --suite $(DEMO_DIR)/suite.json --agent guarded
	-$(PYTHON) -m redloop check-suite --suite $(DEMO_DIR)/suite.json --agent naive
	@echo "Showcase artifacts in $(DEMO_DIR): attack.jsonl ASR.md suite.json"
