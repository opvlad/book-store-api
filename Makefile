PYTHON := python3
BIN := .venv/bin

MAKEFLAGS += --no-print-directory


start-redis:
	@docker run --name redis-bookstore --rm -d -p 6379:6379 redis:7-alpine > /dev/null
	@echo "REDIS IS STARTED"

stop-redis:
	@docker container stop redis-bookstore > /dev/null 2>&1 || true
	@echo "REDIS IS STOPPED"

runserver:
	$(BIN)/uvicorn app.main:app --host localhost --port 8000 --reload --no-access-log

fullrunserver:
	@$(MAKE) start-redis
	@trap '$(MAKE) stop-redis; trap - EXIT' EXIT INT TERM; \
	$(BIN)/uvicorn app.main:app --host localhost --port 8000 --reload --no-access-log


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

test-errors:
	@$(BIN)/pytest -v tests/test_error_handling.py

coverage:
	@$(BIN)/pytest --cov=app --cov-report=term-missing
