PYTHON := python3
BIN := .venv/bin

MAKEFLAGS += --no-print-directory

start-redis:
	@redis-server --daemonize yes; \
	echo "REDIS IS STARTED"

stop-redis:
	@redis-cli shutdown; \
	echo "REDIS IS STOPPED"

runserver:
	@$(BIN)/uvicorn app.main:app --host localhost --port 8000

devrunserver:
	@$(MAKE) start-redis
	@trap '$(MAKE) stop-redis' EXIT; \
	trap 'exit 0' INT; \
	$(BIN)/uvicorn app.main:app --host localhost --port 8000 --reload

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
