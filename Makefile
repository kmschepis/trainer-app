.PHONY: help build up down restart ps logs config check web-lint web-build py-lint py-compile new-branch commit-new-branch tag

# Usage:
#   make help
#   make build
#   make check
#   make commit-new-branch BRANCH=chore/template1 MSG="template hardening"
#   make tag TAG=template1

help:
	@echo "Targets:"
	@echo "  build              Build all docker images"
	@echo "  up                 Start stack (build + detached)"
	@echo "  down               Stop stack"
	@echo "  restart            Restart stack"
	@echo "  ps                 Show container status"
	@echo "  logs               Follow logs"
	@echo "  config             Validate compose.yml"
	@echo "  check              Build + lint/compile checks (no tests yet)"
	@echo "  new-branch          Create and switch to a new git branch (BRANCH=...)"
	@echo "  commit-new-branch   Create branch, commit all changes, push (BRANCH=..., MSG=...)"
	@echo "  tag                Create + push annotated git tag (TAG=template1)"

build:
	docker compose -f compose.yml build

up:
	docker compose -f compose.yml up --build -d

down:
	docker compose -f compose.yml down

restart:
	docker compose -f compose.yml restart

ps:
	docker compose -f compose.yml ps

logs:
	docker compose -f compose.yml logs -f

config:
	docker compose -f compose.yml config > /dev/null

check: config build web-lint web-build py-lint py-compile

web-lint:
	docker compose -f compose.yml run --rm web sh -lc "npm run lint"

web-build:
	docker compose -f compose.yml run --rm web sh -lc "npm run build"

py-lint:
	@# ruff is installed on-demand (keeps runtime images minimal)
	docker compose -f compose.yml run --rm api sh -lc "python -m pip install -q ruff==0.9.4 && ruff check app"
	docker compose -f compose.yml run --rm agent sh -lc "python -m pip install -q ruff==0.9.4 && ruff check app"

py-compile:
	docker compose -f compose.yml run --rm api sh -lc "python -m compileall app"
	docker compose -f compose.yml run --rm agent sh -lc "python -m compileall app"

new-branch:
	@if [ -z "$(BRANCH)" ]; then echo "BRANCH is required"; exit 2; fi
	git switch -c "$(BRANCH)"

commit-new-branch:
	@if [ -z "$(BRANCH)" ]; then echo "BRANCH is required"; exit 2; fi
	@if [ -z "$(MSG)" ]; then echo "MSG is required"; exit 2; fi
	git switch -c "$(BRANCH)"
	git add -A
	git commit -m "$(MSG)"
	git push -u origin "$(BRANCH)"

tag:
	@if [ -z "$(TAG)" ]; then echo "TAG is required (e.g. TAG=template1)"; exit 2; fi
	git tag -a "$(TAG)" -m "$(TAG)"
	git push origin "$(TAG)"
