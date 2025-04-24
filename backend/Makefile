# include `.env` file if exists
ifneq ("$(wildcard .env)","")
	include .env
	export
endif

run.server.local:
	sh ./run-local.sh

run.server.prod: 
	uv run gunicorn app.web.wsgi:application \
		--bind 0.0.0.0:8000 \
		--workers ${WORKERS} \
		--threads ${THREADS} \
		--timeout 480

run.celery.local:
	OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES uv run celery -A tasks.app worker --loglevel=DEBUG --prefetch-multiplier=1

run.celery.prod:
	uv run celery -A tasks.app worker --loglevel=INFO --concurrency=${WORKERS} --prefetch-multiplier=1

wait_for_services:
	uv run manage.py wait_for_db

makemigrations:
	uv run manage.py wait_for_db && uv run manage.py makemigrations

migrate:
	uv run manage.py wait_for_db && uv run manage.py migrate

collectstatic:
	uv run collectstatic --no-input

createsuperuser:
	uv run manage.py createsuperuser --email "devdanasaham@danasaham.co.id" --username admin

# Tests, linters & formatters
formatblack:
	make -k ruff-format black

formatruff:
	make -k ruff-format ruff-fix

lint:
	make -k ruff-check mypy

black:
	uv run --with black black .

black-check:
	uv run --with black black --check .

ruff:
	uv run --with ruff ruff check .

ruff-fmt:
	uv run --with ruff ruff check --fix-only --unsafe-fixes .

test:
	uv run --with pytest pytest --cov=/apps

mypy:
	uv run --with mypy mypy .

# Docker
logs:
	docker compose logs -f --tail=100

logs.errors:
	docker compose logs -f --tail=100 | grep -E 'ERROR|WARNING|EXCEPTION|CRITICAL|FATAL|TRACEBACK'

db.dump.all:
	@mkdir -p backups
	$(eval BACKUP_PATH := backups/dump_$(shell date +%Y-%m-%d-%H-%M-%S).sql)
	@docker exec -e PGPASSWORD=${POSTGRES_PASSWORD} ${COMPOSE_PROJECT_NAME}-db-1 pg_dumpall -c -U ${POSTGRES_USER} > ${BACKUP_PATH}
	@echo "Database dumped to '${BACKUP_PATH}'"

db.restore:
	@test -n "$(BACKUP_PATH)" || (echo '`BACKUP_PATH` is not set. Use `make db.restore BACKUP_PATH=<path>`' && exit 1)

	@docker exec -i -e PGPASSWORD=${POSTGRES_PASSWORD} ${COMPOSE_PROJECT_NAME}-db-1 psql -U ${POSTGRES_USER} < ${BACKUP_PATH}
	@echo "Database restored from '${BACKUP_PATH}'"
