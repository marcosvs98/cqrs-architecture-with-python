run-tests:
	pytest src/tests/


pre-commit-config:
	pre-commit autoupdate && pre-commit install --install-hooks


start-app:
	docker-compose down && docker-compose up -d && docker-compose logs -f app
