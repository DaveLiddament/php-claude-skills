---
name: phpstan-custom-rule
description: Create a custom PHPStan rule with tests and fixtures. Use when the user wants to create a new PHPStan rule for their project.
user-invocable: true
argument-hint: [description of what the rule should do]
---

# Create a Custom PHPStan Rule

Create a custom PHPStan rule based on the user's requirements. If no arguments are provided, ask the user what the rule should do.

IMPORTANT: This skill works on both new and existing projects. Before each step, check what already exists and only add what is missing.


## Step 1: Environment Setup (first time only)

Check if the custom PHPStan rule environment is already set up. If not, perform the following:

### Directory structure

Create the following directories if they don't exist:

- `utils/phpstan/src/Rules/`
- `utils/phpstan/tests/Rules/`

### Dependencies

Add `dave-liddament/phpstan-rule-test-helper` as a dev dependency if not already present:

```bash
composer require --dev dave-liddament/phpstan-rule-test-helper
```

### Autoloading

Ensure `composer.json` has the following PSR-4 autoload-dev entries (merge with existing):

```json
"autoload-dev": {
    "psr-4": {
        "Utils\\Phpstan\\": "utils/phpstan/src/",
        "Utils\\Phpstan\\Tests\\": "utils/phpstan/tests/"
    }
}
```

After adding, run `composer dump-autoload`.

### PHPUnit test suite

Ensure `phpunit.xml` (or `phpunit.xml.dist`) contains a `phpstan` test suite:

```xml
<testsuite name="phpstan">
    <directory>utils/phpstan/tests</directory>
</testsuite>
```

### PHPStan configuration

Update `phpstan.neon` to include the custom rule source and test directories in the analysed paths, and exclude fixture files:

Add to `parameters.paths`:
- `utils/phpstan/src`
- `utils/phpstan/tests`

Add to `parameters.excludePaths`:
- `utils/phpstan/tests/Rules/*/Fixtures`

### PHP-CS-Fixer configuration

Update `.php-cs-fixer.php` to include the custom rule directories but exclude fixtures:

Add to the finder:
- `->in(__DIR__ . '/utils/phpstan/src')`
- `->in(__DIR__ . '/utils/phpstan/tests')`
- `->notPath('utils/phpstan/tests/Rules/*/Fixtures')`

## Step 2: Understand the Rule

Based on `$ARGUMENTS` or by asking the user, have a conversation to understand:

1. What the rule should detect and report as an error.
2. What similar-looking code should NOT be flagged.

Then agree on a **rule class name** with the user (e.g. `DisallowEchoRule`). The class name should be a concise summary — it does not need to capture every nuance of what the rule does. The full behaviour is expressed in the implementation and tests, not the name. Either suggest a name for the user to approve, or let them propose one.

## Step 3: Create Test Fixtures First

Create fixture files in `utils/phpstan/tests/Rules/<RuleName>/Fixtures/`.

Fixtures must cover:
- **Error cases**: Code that violates the rule. Mark these lines with `// ERROR` comments.
- **Non-error cases**: Code that looks similar but should NOT trigger the rule. These lines must NOT have `// ERROR` comments.

It is critical to have good coverage of both. Think carefully about edge cases and code that looks similar to a violation but isn't.

Example fixture for a "disallow echo" rule:

```php
<?php

echo "hello"; // ERROR

print "hello"; // This is not echo, should not be flagged

$result = 1 + 2; // Unrelated code, should not be flagged
```

**IMPORTANT: Show the fixture files to the user and get confirmation before proceeding.** Ask if they want to add or change any test cases.

## Step 4: Ask for the Rule Identifier

Ask the user for the rule identifier. Explain that:

- It must be in dot-notation (e.g. `myProject.disallowEcho`)
- It can only contain letters (uppercase and lowercase) and dots
- No spaces, dashes, or other characters
- It should be descriptive and unique

## Step 5: Create the Test Class

Create the test class at `utils/phpstan/tests/Rules/<RuleName>/<RuleName>Test.php`.

The test class must:
- Be in namespace `Utils\Phpstan\Tests\Rules\<RuleName>`
- Extend `DaveLiddament\PhpstanRuleTestHelper\AbstractRuleTestCase`
- Implement `getRule()` returning an instance of the rule
- Implement `getErrorFormatter()` returning the error message template
- Have a test method for each fixture file calling `$this->assertIssuesReported()`

Example:

```php
<?php

declare(strict_types=1);

namespace Utils\Phpstan\Tests\Rules\DisallowEchoRule;

use DaveLiddament\PhpstanRuleTestHelper\AbstractRuleTestCase;
use PHPStan\Rules\Rule;
use Utils\Phpstan\Rules\DisallowEchoRule;

/** @extends AbstractRuleTestCase<DisallowEchoRule> */
class DisallowEchoRuleTest extends AbstractRuleTestCase
{
    protected function getRule(): Rule
    {
        return new DisallowEchoRule();
    }

    protected function getErrorFormatter(): string
    {
        return 'Echo statements are not allowed.';
    }

    public function testFixtures(): void
    {
        $this->assertIssuesReported(__DIR__ . '/Fixtures/echo.php');
    }
}
```

## Step 6: Create the Rule Class

Create the rule class at `utils/phpstan/src/Rules/<RuleName>.php`.

The rule class must:
- Be in namespace `Utils\Phpstan\Rules`
- Implement `PHPStan\Rules\Rule`
- Have the correct `@implements Rule<Node\...>` generic annotation
- Implement `getNodeType()` returning the appropriate node class
- Implement `processNode()` with the rule logic
- Use `RuleErrorBuilder::message()->identifier()->build()` to create errors

Example:

```php
<?php

declare(strict_types=1);

namespace Utils\Phpstan\Rules;

use PhpParser\Node;
use PHPStan\Analyser\Scope;
use PHPStan\Rules\Rule;
use PHPStan\Rules\RuleErrorBuilder;

/** @implements Rule<Node\Stmt\Echo_> */
class DisallowEchoRule implements Rule
{
    public function getNodeType(): string
    {
        return Node\Stmt\Echo_::class;
    }

    /** @return list<\PHPStan\Rules\RuleError> */
    public function processNode(Node $node, Scope $scope): array
    {
        return [
            RuleErrorBuilder::message('Echo statements are not allowed.')
                ->identifier('myProject.disallowEcho')
                ->build(),
        ];
    }
}
```

## Step 7: Register the Rule

Add the rule as a service in `phpstan.neon`:

```yaml
services:
    -
        class: Utils\Phpstan\Rules\DisallowEchoRule
        tags:
            - phpstan.rules.rule
```

## Step 8: Verify

Run the PHPStan test suite to verify the rule works:

```bash
./vendor/bin/phpunit --testsuite phpstan
```

If tests fail, investigate and fix the rule implementation.

## Appendix: PHPStan Rule Test Helper Reference

Reference for `dave-liddament/phpstan-rule-test-helper`. Use this when creating tests for custom PHPStan rules.

### Base Class

Tests extend `DaveLiddament\PhpstanRuleTestHelper\AbstractRuleTestCase` which extends PHPStan's `RuleTestCase`. It removes the need to manually track line numbers in tests.

### Fixture Error Markers

Mark lines in fixture files with `// ERROR` to indicate where the rule should report an error. Lines without `// ERROR` must not trigger errors.

#### Simple error (no context)

When all errors have the same message, define it once via `getErrorFormatter()`:

```php
protected function getErrorFormatter(): string
{
    return "Echo statements are not allowed.";
}
```

Fixture:
```php
echo "hello"; // ERROR
print "hello"; // This should not be flagged
```

#### Error with context values

Use pipe-separated (`|`) values after `// ERROR` to substitute into `{0}`, `{1}`, etc. placeholders in the error message:

```php
protected function getErrorFormatter(): string
{
    return "Can not call {0} from within class {1}";
}
```

Fixture:
```php
class SomeCode
{
    public function go(): void
    {
        $item = new Item("hello");
        $item->updateName("world"); // ERROR Item::updateName|SomeCode
    }

    public function go2(): void
    {
        $item = new Item("hello");
        $item->remove(); // ERROR Item::remove|SomeCode
    }
}
```

This produces:
- "Can not call Item::updateName from within class SomeCode"
- "Can not call Item::remove from within class SomeCode"

#### Full error message in fixture

Instead of using `getErrorFormatter()`, you can put the complete expected error message after `// ERROR`:

```php
$item->updateName("world"); // ERROR Can not call method
```

#### Custom ErrorMessageFormatter

For complex formatting logic, return an `ErrorMessageFormatter` from `getErrorFormatter()`:

```php
use DaveLiddament\PhpstanRuleTestHelper\ErrorMessageFormatter;

protected function getErrorFormatter(): ErrorMessageFormatter
{
    return new class() extends ErrorMessageFormatter {
        public function getErrorMessage(string $errorContext): string
        {
            $parts = $this->getErrorMessageAsParts($errorContext);
            $calledFrom = count($parts) === 2
                ? 'class ' . $parts[1]
                : 'outside an object';

            return sprintf('Can not call %s from %s', $parts[0], $calledFrom);
        }
    };
}
```

Fixture:
```php
class SomeCode
{
    public function go(): void
    {
        $item->updateName("world"); // ERROR Item::updateName|SomeCode
    }
}

$item->remove(); // ERROR Item::remove
```

Produces:
- "Can not call Item::updateName from class SomeCode"
- "Can not call Item::remove from outside an object"

### Key Points

- One `assertIssuesReported()` call per fixture file
- Multiple fixture files can be tested in separate test methods
- Lines with `// ERROR` are expected to trigger the rule
- Lines without `// ERROR` must NOT trigger the rule
- If the rule needs a `ReflectionProvider`, use `$this->createReflectionProvider()` in `getRule()`
