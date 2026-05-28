.PHONY: up down logs api studio test lint migrate seed zip

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

api:
	uvicorn services.api.app.main:app --reload

studio:
	cd apps/studio && npm install && npm run dev

migrate:
	alembic upgrade head

seed:
	python scripts/seed_demo_corpus.py

test:
	pytest -q

lint:
	python -m compileall services packages scripts

zip:
	cd /mnt/data && zip -qr ATMAN_REPO_v0_3.zip ATMAN_REPO_v0_3
