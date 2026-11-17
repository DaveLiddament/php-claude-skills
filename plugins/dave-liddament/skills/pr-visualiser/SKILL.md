---
name: pr-visualiser
description: Turn a pull request, or the current branch's changes against main/master, into a published visual explainer page that guides a code review. The page has a high-level overview, a colour-coded change map (new / changed / unchanged / removed), flow and sequence diagrams, before/after comparisons, charts of where the lines went, a walkthrough of each changed piece, and a "where to look hardest" review guide. Use this whenever someone asks to visualise, explain, map, walk through or summarise a PR or branch for review ("explain PR 124", "what does this branch change?", "help me review this", "make a page for this PR", "diagram my changes vs main"), even if they don't say "visualise" or "artifact". Don't use it for a plain bug-hunting review with no explanation wanted; /code-review does that.
---

# PR visualiser

Produce one published Artifact page that lets a reviewer understand a change in five seconds and review it properly in fifteen minutes. The page explains; it does not just list. The first screen (title, stats strip, change map) should tell the whole story at a glance, and everything below it should help the reviewer decide where to spend their attention.

The bar is a page a senior engineer would be proud to share. It is accurate to the line, visual where the change has a shape, and short where it doesn't.

## 1. Work out what is being explained

- **A PR number or URL** → use `gh`. Gather `gh pr view <n> --json number,title,body,author,baseRefName,headRefName,headRefOid,mergeCommit,commits,files,url,state`, plus `gh pr diff <n>`.
  - To read code at the PR's head, fetch it first: `git fetch origin pull/<n>/head`. Then use `git show <headRefOid>:<path>` for each file.
  - Base commit. Open PR: `base=$(git merge-base <headRefOid> origin/<baseRefName>)`. Merged PR: `base=$(git merge-base <headRefOid> <mergeCommit>^1)`, because the base branch has moved on since.
  - Use `git diff -M $base <headRefOid>` as the canonical diff, for the stats and for reading. Use `gh pr diff` only as a cross-check.
- **Nothing given** → explain the current branch against the default branch (`main` or `master`; check `git symbolic-ref refs/remotes/origin/HEAD`, or which of the two exists). Use `git diff --merge-base <default>`, which includes uncommitted work, and say in the page header that it covers uncommitted changes. If the branch *is* the default branch with no local changes, ask what to compare.
- **A branch name or commit range** → treat it like the no-argument case with that base or head.

Record the exact head commit (short SHA). It goes in the header and the footer, so the page states what it describes.

## 2. Gather the facts

1. Get the size and shape from the diff with `<diff command> | python3 <skill-dir>/scripts/diff_stats.py --summary --depth 3`. It prints:
   - totals, plus a breakdown by kind: src, test (test code), fixture (test data), docs, config, ci and deps
   - totals by directory group
   - every file that was added, deleted, renamed or generated

   Use these numbers for the stats strip rather than counting by hand. `--bars` prints ready-to-paste HTML for the "Where the lines went" section: one block per kind, with every bar on one shared scale and generated files left out. Pick `--depth` so the groups match the codebase's real modules. Run without a flag to get the full per-file JSON.
2. Get the intent. Read the PR body, any linked issues (`gh issue view <n>`), and the commit messages. For a PR, also read the review discussion: `gh pr view <n> --comments` and `gh api repos/{owner}/{repo}/pulls/<n>/comments`. The page's "why" comes from here. If the sources don't say why, infer it from the code and label it as inferred. Don't invent a motivation.
3. Read the code properly. Read every changed source file in full at the head commit, not just the hunks. Then grep for the callers and collaborators of anything whose signature or behaviour changed. The unchanged code the change relies on is half of what a reviewer needs to know.
   - For a large change (roughly 30+ source files, or several unrelated areas), split the reading across a few Explore subagents, one per area. Have each one return: the entry points, what changed in behaviour, new types, contracts touched, and the unchanged pieces relied on.

## 3. Find the story

Before writing any HTML, answer these in your working notes:

- **What does this change make possible or fix?** One sentence in the user's terms. This becomes the lede.
- **What is the new concept, if any?** For example a new value type, a new endpoint, a new stage or a new flag. Most good PRs have one, and the page should be built around it.
- **How does data or control flow through it?** Trace the entry point to the output, and mark which hops are new, changed, or unchanged but relied on.
- **Which contracts moved?** Public APIs and interfaces, CLI options, file and wire formats, HTTP endpoints and status codes, DB schema, config keys, and backward compatibility (old files or clients still accepted?).
- **What's mechanical and what's substantive?** "The same three-line edit in nine parsers" is one row with a count, not nine walkthrough steps. Saying so tells the reviewer where they can skim.
- **What's tested?** Map each behaviour change to the tests that cover it, and spot the gaps.
- **Where should the reviewer look hardest?** Pick the riskiest logic, edge cases, compatibility, and anything the tests miss.

## 4. Choose the sections and visuals

Build the page from the sections that change needs, in roughly this order. Every page has the first three. Include the rest when the change has that shape. Don't pad a small change: three sections and one diagram is a fine page for a twenty-line fix.

| Section | Include when | Form |
| --- | --- | --- |
| **Header** | always | Eyebrow (`PR #n · repo · commit sha`, or `branch vs main · sha`), a 2–4 word title naming the change, and a one-to-two sentence lede. |
| **At a glance** | always | Stats strip: files changed, +/− lines (from the script), new types, and contracts changed. Add one or two numbers specific to this change (e.g. "9 parsers updated", "3 new endpoints"). |
| **Change map** | always | Mermaid flowchart of the parts involved, coloured by status: new, changed, unchanged-but-relied-on, removed. Use the classDefs in the template, and put the legend above the map. This is the hero visual, so make it show the real architecture, not a list of files in boxes. |
| **Why it exists** | always | A few short paragraphs from the PR, issue and commits. A callout for the single most important fact (e.g. "No behaviour change until X is enabled"). |
| **Before / after** | a format, output, signature or behaviour visibly changes | Side-by-side `.compare` figures: JSON, CLI output, a call signature or a table row. Highlight additions in `.hl` and strike removals with `.gone`. Prefer real output: expected output from the PR's own tests is ideal, and say which test it came from. If it's cheap and safe, you can run both commits in a throwaway `git worktree add <scratchpad>/wt-<sha> <sha>`, removed afterwards. Never check out over the user's working tree. If you rebuilt the output by tracing the code, label it "traced from the code, not captured from a run". |
| **Flow** | anything with a runtime path worth following | A Mermaid `sequenceDiagram` (with `autonumber` and `alt` blocks for branches), or a `flowchart` for decision logic. One diagram per entry point. |
| **Walkthrough** | always, for substantive pieces | `ol.steps`, one step per class or function in flow order. Each step gets a chip (`new`, `changed`, `same`) and a path, plus two to four bullets on what it does and why it matters. Collapse the mechanical changes into one step with a count. |
| **Contracts / behaviour table** | endpoints, CLI options, error codes, config keys, file-format fields | A table. For example: status code · when · decided by. Or: option · default · effect. |
| **Where the lines went** | more than a handful of files | The `--bars` output from the script, pasted in as-is. A reviewer reads this as "most of the work is here". A sentence above it saying what the bars show (e.g. "most of the PR is fixtures") is worth more than the bars alone. |
| **Test coverage** | behaviour changed | A table: behaviour · test that covers it · gap. A row with no test is a review point. |
| **Unchanged but relied on** | the change leans on existing code | A short list of existing pieces, each with a line on what the change assumes about it. |
| **Where to look hardest** | always for a PR under review; optional for a finished, merged PR | `ol.review` items. Each has a severity (`block` = worth fixing before merge, `look` = needs a careful read, `tidy` = optional), a `path:line`, and a concrete scenario. Write it as a reviewer's guide, not a verdict. Only state real defects as defects, each with its failure case. For a merged PR, check each point against the default branch today and tag it "still on main" or "fixed since", because the reader will want to know whether it's still live. |

Other shapes the change might have, each better drawn than described: a state machine (`stateDiagram-v2`), a class or type hierarchy (`classDiagram`), or a data migration (before → after schema). If the numbers have a shape (benchmarks, sizes, counts over time), use a chart. Load the `dataviz` skill before drawing one.

Use the visual vocabulary consistently: the same four status colours on chips, map nodes and legend; tabular figures for numbers; mono for code identifiers.

## 5. Accuracy rules

Reviewers will check this page against the code, and a single wrong claim costs it their trust.

- Every behavioural claim comes from code you read, and names the file. Give `path:line` for review items and anywhere a reviewer would want to jump.
- Every number comes from the diff stats, the code, or a cited source, never an estimate.
- Use names exactly as they appear in the code: classes, methods, flags, fields.
- Motivation that isn't stated in the PR, issue or commits is labelled as inferred.
- If something is unclear, say so on the page as an open question rather than guessing.

## 6. Build and publish

1. Follow the Artifact tool's flow for a new page: call `quickstart` with `intent: "other"` and follow what it returns.
2. Start from `<skill-dir>/assets/template.html`. It carries the page contract (light/dark tokens, mobile layout, fonts) and every component class used above. Copy it to the scratchpad as `pr-<n>-<slug>.html` (or `branch-<slug>.html`), then replace everything from `<div class="wrap">` down with your content. Keep the `<style>` block whole, and append any new CSS rules at its end rather than editing or splicing it. Keep the TOC in the same order as the sections.
3. Diagrams go in `<pre class="mermaid">` inside a `.sheet`. The Artifact publisher injects a Mermaid runtime that themes diagram text and lines for the viewer's light or dark mode, and the template's sheets follow the page theme to match.
   - Don't add a `%%{init: …}%%` theme directive, and don't force a sheet's background: either one gives light text on a white sheet in dark mode.
   - Give styled nodes the template's classDefs. They set their own dark text on light fills, so they read in both themes.

   Mermaid breaks on small things. Before publishing, check:
   - Quote every node label that contains punctuation: `A["Foo::bar()"]`.
   - No bare `end` as a node id. Avoid `;` and `#` inside sequence messages and notes. Escape `<` and `>` in labels as `&lt;` and `&gt;`.
   - Each `classDef` is declared before use. `class X new` lines name node ids, not labels.
   - **Width.** The content column is about 880px wide. A flowchart more than about 5 ranks across scrolls sideways, which spoils the first screen. Use `flowchart TB` for call chains and pipelines. Use `LR` only for short, wide-and-shallow maps, and keep long class names on two lines with `<br/>`.
   - Keep a map to at most ~20 nodes. If it's bigger, split it into an overview plus a detail diagram.
   - To highlight the new path, use `linkStyle <i> stroke:#1f7a4d,stroke-width:3px`. Edge indexes count from 0 in the order the edges are declared, and `A --> B --> C` counts as two. Declare the new-path edges first so their indexes are 0..n and can't drift.
4. Publish with `icon: "code"` and a one-sentence `description`. After publishing, `read` the artifact back and confirm the `claude-mermaid-runtime` block was injected. If it wasn't, redraw the diagrams as inline SVG (load the `artifact-diagramming` skill). A diagram that fails to parse quietly falls back to showing its source text. If this session has a way to look at the page (a preview tool, a browser, or `mmdc` to parse the Mermaid), use it once. If not, tell the user to check the diagrams when they open it.
5. Reply with the link and two or three lines: what the change is, and the one or two places the reviewer should look first. Don't recap the page.

The page is private by default. Leave sharing to the user, especially for code from a private repo.
