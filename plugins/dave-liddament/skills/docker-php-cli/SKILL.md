---
name: docker-php-cli
description: Set up Docker for a PHP CLI project with Xdebug support. Use when the user wants to add Docker to a PHP project.
user-invocable: true
argument-hint: [php-version]
---

# Docker PHP CLI Setup

Set up Docker for a PHP CLI project.

IMPORTANT: This skill works on both new and existing projects. Before each step, check what already exists and only add what is missing.

## Step 1: Determine PHP Version

Use the following priority to determine the PHP version:

1. If `$ARGUMENTS` is provided (e.g. `8.3`), use that version.
2. Otherwise, check the project's `composer.json` for the PHP version requirement.
3. If neither is available, default to `8.5`.

## Step 2: Create Dockerfile

Create a `Dockerfile` in the project root if one doesn't already exist.

Use the template from `${CLAUDE_SKILL_DIR}/Dockerfile.template` as a base. Adjust the PHP version as determined in Step 1.

If a Dockerfile already exists, leave it as-is.

## Step 3: Create docker-compose.yml

Create a `docker-compose.yml` in the project root if one doesn't already exist.

Use the template from `${CLAUDE_SKILL_DIR}/docker-compose.yml.template` as a base. Adjust the PHP version to match the Dockerfile.

If a `docker-compose.yml` already exists, leave it as-is.

## Step 4: Update .gitignore

Ensure `.gitignore` does NOT ignore Docker files — `Dockerfile` and `docker-compose.yml` should be committed.

## Step 5: Update CLAUDE.md

Add a note to the project's `CLAUDE.md` file (create it if it doesn't exist). Merge with existing content if present.

Add the following guidance:

```
## Docker

This project uses Docker for all PHP operations. Always use `docker compose exec app` to run PHP commands inside the container.

Examples:
- `docker compose exec app composer install`
- `docker compose exec app vendor/bin/phpunit`
- `docker compose exec app vendor/bin/phpstan analyse`

To start the container: `docker compose up -d`
To stop the container: `docker compose down`
To rebuild after Dockerfile changes: `docker compose up -d --build`

Xdebug is enabled by default. To disable it, set `XDEBUG_MODE=off` in `docker-compose.yml` and restart the container.
```

## Step 6: Build and Start

Build and start the container:

```bash
docker compose up -d --build
```

Verify the container is running:

```bash
docker compose ps
```
