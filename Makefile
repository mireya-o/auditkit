.DEFAULT_GOAL := help

.PHONY: help smoke test venv doctor index app ask pack eval adversarial clean

VENV ?= .venv
PY := $(if $(wildcard $(VENV)/bin/python),$(VENV)/bin/python,python3)
STREAMLIT := $(if $(wildcard $(VENV)/bin/streamlit),$(VENV)/bin/streamlit,streamlit)

help:
	@printf "Targets:\n"
	@printf "  make smoke         Validate shipped examples and check syntax\n"
	@printf "  make test          Run executable tests\n"
	@printf "  make venv          Create the local environment and install dependencies\n"
	@printf "  make doctor        Check runtime endpoint, configured profiles, source files, and index state\n"
	@printf "  make index         Build the local index from data/raw\n"
	@printf "  make app           Launch the interface\n"
	@printf "  make ask Q='...'   Run a grounded query from the CLI\n"
	@printf "  make pack          Generate a structured export from docs/operator_input_template.md\n"
	@printf "  make eval          Run the bounded evaluation set\n"
	@printf "  make adversarial   Run hostile-input checks\n"
	@printf "  make clean         Remove local caches and bytecode\n"

smoke:
	$(PY) -m compileall src app
	$(PY) scripts/validate_examples.py

test:
	PYTHONPATH=src $(PY) -m pytest -q

venv:
	python3 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install -r requirements.lock.txt

doctor:
	$(PY) scripts/doctor.py

index:
	PYTHONPATH=src $(PY) -m auditkit.build_index

app:
	$(STREAMLIT) run app/streamlit_app.py

ask:
	PYTHONPATH=src $(PY) -m auditkit.ask "$(Q)"

pack:
	PYTHONPATH=src $(PY) -m auditkit.generate_pack --input docs/operator_input_template.md --max_contexts 8 --max_tokens 1200

eval:
	PYTHONPATH=src $(PY) -m auditkit.eval --top_k 6 --max_tokens 650

adversarial:
	PYTHONPATH=src $(PY) -m auditkit.redteam --top_k 6 --max_tokens 650

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
