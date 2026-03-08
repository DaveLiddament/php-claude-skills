---
name: php-project-setup
description: Set up a new PHP project with standard tooling and configuration. Use when creating a new PHP project or ensuring an existing project has the correct setup.
user-invocable: true
---

# PHP Project Setup

Set up or complete the setup of a PHP project with the standard tooling and configuration described below.

IMPORTANT: This skill works on both new and existing projects. Before each step, check what already exists and only add what is missing. Do not duplicate or overwrite existing configuration unless it conflicts with the requirements below.

## Directory Structure

Ensure the following directories exist:

- `src/`
- `tests/`
- `utils/`

## PHP Version

Detect the installed PHP version by running `php -v` and extracting the major.minor version (e.g. 8.5). Set the `require.php` constraint in `composer.json` to `~X.Y` (e.g. `~8.5`).

## Dependencies

### Main dependencies

Install with `composer require` (skip any already present):

- `dave-liddament/php-language-extensions`

### Dev dependencies

Install with `composer require --dev` (skip any already present):

- `bamarni/composer-bin-plugin`
- `phpstan/phpstan`
- `phpstan/phpstan-strict-rules`
- `phpstan/phpstan-phpunit`
- `phpstan/phpstan-webmozart-assert`
- `dave-liddament/phpstan-php-language-extensions`
- `spaze/phpstan-disallowed-calls`
- `rector/rector`
- `phpunit/phpunit`

### Bamarni composer-bin-plugin configuration

Ensure `composer.json` contains the following `extra` configuration:

```json
"extra": {
    "bamarni-bin": {
        "bin-links": true,
        "forward-command": true
    }
}
```

### Isolated dev tools (via composer bin)

Install each in its own namespace to avoid dependency clashes. Skip any already present:

- `composer bin cs-fixer require --dev friendsofphp/php-cs-fixer`
- `composer bin parallel-lint require --dev php-parallel-lint/php-parallel-lint`
- `composer bin require-checker require --dev maglnet/composer-require-checker`
- `composer bin unused require --dev icanhazstring/composer-unused`

## Composer Scripts

Ensure the following scripts are defined in `composer.json`. Merge with any existing scripts:

```json
"scripts": {
    "setup": [
        "@composer install",
        "@composer bin all install"
    ],
    "ci": [
        "@composer-validate",
        "@lint",
        "@composer-unused",
        "@composer-require-checker",
        "@cs",
        "@phpstan",
        "@test"
    ],
    "ci-local": [
        "@composer-validate",
        "@lint",
        "@composer-unused",
        "@composer-require-checker",
        "@cs-fix",
        "@phpstan",
        "@test"
    ],
    "composer-validate": "@composer validate --no-check-all --strict",
    "lint": "parallel-lint src tests utils",
    "composer-unused": "composer-unused",
    "composer-require-checker": "composer-require-checker check",
    "cs": "php-cs-fixer fix -v --dry-run",
    "cs-fix": "php-cs-fixer fix -v",
    "phpstan": "phpstan analyse --no-progress",
    "test": "phpunit"
}
```

## Configuration Files

### PHPStan (`phpstan.neon`)

If no `phpstan.neon` exists, copy the template from `${CLAUDE_SKILL_DIR}/phpstan.neon` into the project root.

If a `phpstan.neon` already exists, merge the template into the existing configuration. Ensure all includes, rules, and paths from the template are present without removing any existing configuration.

### PHP-CS-Fixer (`.php-cs-fixer.php`)

If no `.php-cs-fixer.php` exists, copy the template from `${CLAUDE_SKILL_DIR}/.php-cs-fixer.php` into the project root.

If `.php-cs-fixer.php` already exists, leave it as-is.

### PHPUnit (`phpunit.xml`)

If no `phpunit.xml` or `phpunit.xml.dist` exists, generate the configuration by running:

```bash
./vendor/bin/phpunit --generate-configuration
```

### .gitignore

Ensure `.gitignore` contains at least the following entries (merge with any existing `.gitignore`):

```
/vendor/
/vendor-bin/*/vendor/
/.php-cs-fixer.cache
/.phpunit.cache/
/.idea/
```

## Completion

After setup, run `composer run ci-local` to verify everything is working correctly.
