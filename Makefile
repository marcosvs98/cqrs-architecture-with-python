rest-up:
	docker-compose -f rest.docker-compose.yml up --build

rest-down:
	docker-compose -f rest.docker-compose.yml down

test-domain:
	pytest tests/domain/
