PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin

runserver:
	@$(BIN)/uvicorn app.main:app --host localhost --port 8000

devrunserver:
	@$(BIN)/uvicorn app.main:app --host localhost --port 8000 --reload

test:
	@$(BIN)/pytest -v

test-auth:
	@$(BIN)/pytest -v tests/test_auth.py

test-authors:
	@$(BIN)/pytest -v tests/test_authors.py

test-books:
	@$(BIN)/pytest -v tests/test_books.py

test-orders:
	@$(BIN)/pytest -v tests/test_orders.py

test-users:
	@$(BIN)/pytest -v tests/test_users.py

coverage:
	@$(BIN)/pytest --cov=app --cov-report=term-missing
