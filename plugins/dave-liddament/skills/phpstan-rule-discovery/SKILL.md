---
name: phpstan-rule-discovery
description: Find PHPStan rules and config changes worth adding to a project, by mining its fix commits, PR review comments and conventions, then measuring each candidate against today's code. Produces a decision document with examples, violation counts and live bugs. Use when the user wants to know which PHPStan rules would have prevented past bugs or review comments.
user-invocable: true
argument-hint: [optional focus or scale, e.g. "last 200 PRs only"]
---

# Discover PHPStan Rules Worth Adding

Review the project for PHPStan rules and config changes worth adding. The output is a document the user can decide from: real code examples for each candidate, and what adding it today would cost.

This is a large job. Use subagents and fan out widely. Before starting, tell the user how many commits and PRs you found and roughly how many agents you plan to run, and confirm the scale. Apply any focus or limit given in `$ARGUMENTS`.

## Step 1: Gather rule ideas

Use three sources:

1. **Fix commits.** Every commit whose message suggests a fix (fix, bug, revert, hotfix, oops, correct, ...). For each, read the diff, find the root cause, and decide whether a PHPStan rule or config change would have caught it.
2. **PR review comments.** Every PR comment, including inline review comments (use `gh api`). Decide whether a custom rule would have made the comment unnecessary.
3. **Conventions.** The ones documented in CLAUDE.md, the README and docs/, and the ones you can infer from the code (patterns followed almost everywhere). Decide which could be enforced.

Gather in batches: fix commits split into batches, PR comments split into batches, one agent for documented conventions, one for inferred conventions.

## Step 2: Check before proposing

- Read `phpstan.neon`, `composer.json` and the installed PHPStan extensions. Don't propose something an installed extension or option already does.
- If a claim depends on how a tool or framework behaves (what an extension checks, how a baseline tool filters, how a resolver falls back), check it in `vendor/` or with a run. Never claim it from memory.
- Read the project's decisions (CLAUDE.md, docs). Recommendations must not contradict them. If the user has said, for example, that POST data must go through forms, push recommendations towards forms.

## Step 3: Deduplicate into groups

Merge duplicate ideas across agents. Group the rules into chapters, e.g. access control/routes, config, ORM, forms/messaging, correctness, structure/tests, templates. Give each rule a stable ID (`A1`, `D3`, ...).

## Step 4: Measure each group

Run one agent per group to prototype, measure and write its section. Measurements must be exact, not estimated.

- Measure against a clean worktree of the default branch (`git worktree add`), not the branch the user is on. That branch may have work in progress, failing tests or someone else editing it.
- For each candidate, write a prototype rule or config and run PHPStan with it to count violations. To keep runs fast, use a probe config that loads only the probe rules (`customRulesetUsed: true`, the probe rules under `rules:`, the classes via `bootstrapFiles:`). Limit parallel processes when several agents run at once.
- Use a php-parser scan or grep only when a prototype isn't practical, and say which method was used.
- Keep probes in `<repo>/phpstan-rule-review/probes/<group>/`.
- Read the code behind every violation that looks like a real bug and confirm it is one. Don't fix it; record it.

## Rules for every subagent

Restate these in every subagent prompt. Subagents don't inherit the user's memory or this skill.

- Write everything to `<repo>/phpstan-rule-review/` from the start, not `/tmp` or the scratchpad, which a reboot can clear. Each agent writes its section file there before replying.
- Don't modify tracked files, install packages, run composer, commit, push or post to GitHub.
- Restate any shell or permission rules from the project's CLAUDE.md or the user's memory, e.g. "no `cd <repo> &&`, no heredocs".
- Reply with a compact table only (ID, name, kind, violations today, live bugs, recommendation), not the full section.

## Step 5: Write the deliverable

### `phpstan-rule-review/sections/<group>.md`

One block per rule, each with an anchor (`<a id="a1"></a>`) so the README can link to it:

```markdown
### A1. <Short rule name>

| | |
|---|---|
| Kind | Custom rule / Config / Existing extension / Not PHPStan |
| Catches | one sentence |
| Evidence | commit hashes with one line each, PR comment links, live bugs |
| Violations today | exact count and how measured, e.g. "7 in 5 files (prototype run)" |
| Effort to build | e.g. "~40 lines, 1–2 h" |
| False-positive risk | Low / Medium / High, and why |
| Recommendation | Add now / Add + baseline / Fix live bugs, then add / Later / Skip, and why |

**What it flags**

A bad and a good example from the repo (file:line) or from the evidence commit, 5–15 lines each.

**Consequence of adding it today**

Every violation as file:line if there are 15 or fewer; otherwise the top 10 and a breakdown by directory. Say whether fixes are mechanical (Rector or cs-fixer) or need judgment. Mark real bugs **bug**.

**How to build it**

For config, the exact neon snippet. For a custom rule, the node type, the logic, the edge cases and a 10–30 line `processNode` sketch, plus the prototype path.
```

End each section with `#### Rejected or merged`, one line per dropped idea and why.

### `phpstan-rule-review/README.md`

The decision document:

- headline numbers;
- a shortlist bucketed as Add now (config) / Add now (custom rule) / Fix live bugs, then add / Add + baseline / Later / Skip;
- a summary table per chapter (ID, name, kind, violations today, live bugs, effort, recommendation), each ID linking to its write-up;
- a live bugs table, security first, with file:line;
- a suggested rollout as a sequence of small PRs;
- the project decisions the recommendations respect.

Before finishing, re-check every count and claim in the README against the sections. A first pass is often wrong.

## Step 6: Report back

Report the shortlist, the live bugs (security first) and anything you couldn't measure. Then offer to:

- commit the folder to its own branch and open a draft PR (leave out `probes/` caches and `var/` directories);
- file issues for the live bugs;
- build the chosen rules with the `phpstan-custom-rule` skill;
- remove the worktree.
