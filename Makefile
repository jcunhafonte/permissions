.PHONY: help protos-generate docker-build docker-delete docker-prune docker-up docker-down start stop install uninstall recreate

help: ## Available commands
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/:.*##\s*/##/g' | awk -F'##' '{ printf "%-14s %s\n", $$1, $$2 }'

protos-generate: ## Generate protos
	python3 -m grpc_tools.protoc -I ./permissions-protos --python_out=./permissions-service/app --grpc_python_out=./permissions-service/app ./permissions-protos/permission.proto

docker-build: ## Docker build in detached mode
	@docker compose up --build -d

docker-delete: ## Docker delete images, volumes and its dependencies
	@docker compose down --rmi all --volumes

docker-prune: ## Docker image prune
	@docker image prune --force

docker-up: ## Docker compose up
	@docker compose up

docker-down: ## Docker compose down
	@docker compose down

start: docker-up ## Start application

stop: docker-down ## Stop application

install: docker-build ## Install application

uninstall: docker-delete docker-prune ## Uninstall application and its dependencies (images, volumes, networks)

recreate: uninstall install ## Recreate application
