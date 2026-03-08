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

## License

MIT
