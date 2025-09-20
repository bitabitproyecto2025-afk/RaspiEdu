up:
docker compose up -d


down:
docker compose down


logs:
docker compose logs -f --tail=100


seed-admin:
docker compose exec app python -c "from app.seed import ensure_admin; ensure_admin(); print('ok')"
