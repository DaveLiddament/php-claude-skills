---
name: makefile-php-cli
description: Create a Makefile for a Dockerised PHP CLI project. Use when the user wants to add Make targets for Docker and PHP tooling.
user-invocable: true
---

# Makefile for PHP CLI Docker Project

Create a Makefile that wraps Docker and PHP tooling commands.

IMPORTANT: If a Makefile already exists, leave it as-is. Only create a new one if none exists.

## Step 1: Check Prerequisites

Verify the project has:
- A `docker-compose.yml` (required — the Makefile wraps Docker commands)
- A `composer.json` with scripts section (used to determine which app targets to generate)

If `docker-compose.yml` is missing, inform the user they should run the `docker-php-cli` skill first.

## Step 2: Determine App Targets

Read the `composer.json` scripts section. Generate `app/*` targets only for composer scripts that exist. The mapping is:

| Composer script | Make target | Description |
|---|---|---|
| `ci-local` | `app/ci` | Run local CI tasks |
| `test` | `app/test` | Run tests (supports `c=` for extra phpunit options) |
| `phpstan` | `app/phpstan` | Run PHPStan analysis |
| `cs-fix` | `app/cs-fix` | Fix code style |
| `cs` | `app/cs` | Check code style (dry run) |
| `lint` | `app/lint` | Run parallel-lint |
| `composer-unused` | `app/composer-unused` | Check for unused composer packages |
| `composer-require-checker` | `app/require-checker` | Check for missing composer requirements |
| `composer-validate` | `app/composer-validate` | Validate composer.json |
| `setup` | `app/setup` | Install all dependencies |

Only include targets for scripts that actually exist in `composer.json`.

Always include these targets regardless of composer scripts:
- `app/shell` — Open a bash shell in the container
- `app/composer` — Run arbitrary composer commands (supports `c=`)

## Step 3: Create the Makefile

Create a `Makefile` in the project root using the template below. Include only the app targets determined in Step 2.

```makefile
OS_FAMILY :=
ifeq ($(OS),Windows_NT)
    OS_FAMILY = Windows
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
        OS_FAMILY = Linux
    endif
    ifeq ($(UNAME_S),Darwin)
        OS_FAMILY = Darwin
    endif
    UNAME_R := $(shell uname -r)
    ifneq ($(findstring WSL2,$(UNAME_R)),)
        OS_FAMILY = Linux
    endif
endif

export USER_ID :=
export DOCKER_USER :=
ifeq ($(OS_FAMILY),Linux)
    USER_ID = $(shell id -u)
    DOCKER_USER = --user "$(USER_ID):$(shell id -g)"
endif

DOCKER_COMP = docker compose
APP_EXEC = $(DOCKER_COMP) exec $(DOCKER_USER) app

.DEFAULT_GOAL = help

## —— Help ——————————————————————————————————————————————————————————————————————
.PHONY: help

help: ## Outputs this help screen
	@grep -E '(^[a-zA-Z0-9\./_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}{printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'

## —— Docker ———————————————————————————————————————————————————————————————————
.PHONY: build up start down logs

build: ## Builds the Docker images
	@$(DOCKER_COMP) build --pull --no-cache

up: ## Starts the container in detached mode
	@$(DOCKER_COMP) up --detach

start: build up ## Build and start the container

down: ## Stop the container
	@$(DOCKER_COMP) down --remove-orphans

logs: ## Show live logs
	@$(DOCKER_COMP) logs --tail=0 --follow

## —— App ——————————————————————————————————————————————————————————————————————
.PHONY: app/shell app/composer

app/shell: ## Open a shell in the app container
	@$(APP_EXEC) bash

app/composer: ## Run composer. Pass the parameter "c=" to run a given command
	@$(eval c ?=)
	@$(APP_EXEC) composer $(c)
```

For each app target determined in Step 2, add it to the App section. Follow these patterns:

### Standard composer script target (no extra params):
```makefile
app/cs-fix: ## Fix code style
	@$(APP_EXEC) composer cs-fix
```

### Target with passthrough params:
For `app/test`, allow extra options via `c=`:
```makefile
app/test: ## Run tests. Pass the parameter "c=" to add options to phpunit
	@$(eval c ?=)
	@$(APP_EXEC) vendor/bin/phpunit $(c)
```

### CI target:
```makefile
app/ci: ## Run local CI tasks
	@$(APP_EXEC) composer ci-local
```

IMPORTANT: Makefiles require actual tab characters for indentation, not spaces. Ensure all recipe lines are indented with tabs.

Remember to add all generated app targets to the `.PHONY` declaration.

## Step 4: Update CLAUDE.md

Update the project's `CLAUDE.md` file (create it if it doesn't exist). If there are existing Docker instructions, update them to say use the Makefile first.

Add or replace with the following guidance:

```
## Running Commands

This project uses a Makefile to wrap Docker commands. Always prefer `make` targets over direct Docker commands.

Run `make help` to see all available targets.

Common commands:
- `make up` — Start the Docker container (use this for day-to-day work)
- `make start` — Full rebuild and start (only needed after Dockerfile changes)
- `make app/shell` — Open a shell in the container
- `make app/ci` — Run all CI checks
- `make app/test` — Run tests (`make app/test c="--filter=MyTest"` for specific tests)
- `make app/composer c="require some/package"` — Run composer commands

Only fall back to `docker compose exec app <command>` if there is no suitable Make target.
```
