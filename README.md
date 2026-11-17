# PHP Claude Skills

A Claude Code plugin providing skills for PHP projects.

## Installation

From within a Claude Code session, run:

```
/plugin marketplace add DaveLiddament/php-claude-skills
/plugin install dave-liddament@php-claude-skills
```

For local testing:

```bash
claude --plugin-dir /path/to/php-claude-skills
```

## Skills

Skills are invoked as `/dave-liddament:<skill-name>`.

- [`docker-php-cli`](#docker-php-cli) — Docker setup for PHP CLI projects
- [`php-project-setup`](#php-project-setup) — Standard PHP project tooling and config
- [`makefile-php-cli`](#makefile-php-cli) — Makefile wrapping Docker and PHP commands
- [`phpstan-custom-rule`](#phpstan-custom-rule) — Create custom PHPStan rules
- [`pr-visualiser`](#pr-visualiser) — Visual explainer page for a PR or branch, to guide code review

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

### `pr-visualiser`

Turn a pull request, or the current branch's changes against `main`/`master`, into a published visual explainer page that guides a code review. Works with any language, not just PHP.

- High-level overview: what the change makes possible, why it exists, and a stats strip
- Colour-coded change map showing what's new, changed, unchanged-but-relied-on, and removed
- Flow and sequence diagrams, before/after comparisons, and charts of where the lines went
- Walkthrough of each changed piece, contract and test-coverage tables
- A "where to look hardest" guide with `path:line` references; for merged PRs, each point is checked against the default branch
- Publishes as a private Artifact page (requires `gh` for PRs)

```bash
/dave-liddament:pr-visualiser 124
/dave-liddament:pr-visualiser            # current branch vs main/master
```

## License

MIT
