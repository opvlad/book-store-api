PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin

runserver:
	@$(BIN)/uvicorn app.main:app --host localhost --port 8000

test:
	@$(BIN)/pytest -v

coverage:
	@$(BIN)/pytest --cov=app --cov-report=term-missing
