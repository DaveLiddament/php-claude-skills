# PHP Claude Skills

A Claude Code plugin providing skills for PHP projects.

## Installation

```bash
claude /plugin install --from https://github.com/DaveLiddament/php-claude-skills
```

## Skills

Skills are invoked as `/dave-liddament:<skill-name>`.

### `php-project-setup`

Set up a new PHP project or complete the setup of an existing one. Works incrementally — checks what already exists and only adds what's missing.

Includes:

- Standard directory structure (`src/`, `tests/`, `utils/`)
- PHP 8.3+ requirement
- Composer dependencies: PHPStan (with strict rules, PHPUnit, webmozart-assert, php-language-extensions, and disallowed-calls extensions), PHPUnit, and php-language-extensions
- Isolated dev tools via `bamarni/composer-bin-plugin`: PHP-CS-Fixer, parallel-lint, composer-require-checker, and composer-unused
- Composer scripts for CI, linting, static analysis, code style, and testing
- Template configs for PHPStan and PHP-CS-Fixer
- `.gitignore` setup

```bash
/dave-liddament:php-project-setup
```

### `phpstan-custom-rule`

Create a custom PHPStan rule with tests and fixtures. Handles both initial environment setup (directories, autoloading, test suite, config) and rule creation.

- Sets up `utils/phpstan/` directory structure on first use
- Creates test fixtures first for review before implementing the rule
- Generates rule class, test class, and fixture files
- Registers the rule in `phpstan.neon`
- Supports error message placeholders and custom formatters via `phpstan-rule-test-helper`

```bash
/dave-liddament:phpstan-custom-rule Disallow echo statements
```

### `docker-php-cli`

Set up Docker for a PHP CLI project with Xdebug support.

- Generates Dockerfile and docker-compose.yml
- Xdebug enabled by default, easy to toggle off
- Composer cache persisted via Docker volume
- PHP version configurable via build arg
- Updates CLAUDE.md to instruct Claude to use Docker for all PHP commands

```bash
/dave-liddament:docker-php-cli
```

### `makefile-php-cli`

Create a Makefile wrapping Docker and PHP tooling for a CLI project.

- OS detection with Linux user mapping for correct file permissions
- Docker targets: `build`, `up`, `start`, `down`, `logs`
- App targets generated dynamically from `composer.json` scripts
- Always includes `app/shell` and `app/composer` with passthrough params
- Self-documenting via `make help`
- Updates CLAUDE.md to prefer Make targets over direct Docker commands

```bash
/dave-liddament:makefile-php-cli
```

## License

MIT
