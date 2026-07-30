---
name: xa-ppt
description: Create, edit, validate, and generate xa-ppt-skill slide decks from deck-spec.json using the repo's design system and pipeline. Use when working on PPT generation, layout selection, deck validation, render/build errors, manifest updates, or layout regressions in this repository.
---

# xa-ppt

Use this skill as the Codex-facing entry point for the xa-ppt-skill repo.

## Source of truth

- Read [.claude/skills/xa-ppt/skill.md](../../../.claude/skills/xa-ppt/skill.md) for the full workflow and layout guardrails.
- Read [deck-spec.json](../../../deck-spec.json) for the current page spec format.
- Read [design-system/design-system.json](../../../design-system/design-system.json) for layout, theme, and regression rules.

## Workflow

1. Validate the page spec.
2. Review deck-level repetition and balance.
3. Generate HTML.
4. Render slides to PNG.
5. Build PPTX and manifest.

Prefer the one-command pipeline:

```bash
python scripts/run_pipeline.py --allow-warn
```

Use strict mode when warnings should fail the run:

```bash
python scripts/run_pipeline.py --stop-on-warn
```

## Editing rules

- Prefer `comparison`, `process`, `hero-statement`, and `table` for contrast, flow, conclusion, and table pages.
- Keep card content vertically centered while preserving left-aligned text.
- Keep tables full-height instead of shrinking them to the top.
- Let long hero statements widen first instead of shrinking type too early.
- Treat `output/`, `__pycache__/`, and `*.pyc` as disposable build artifacts.

## When to change what

- Update `deck-spec.json` for page-level content structure.
- Update `design-system/design-system.json` for layout or guardrail changes.
- Update `.claude/skills/xa-ppt/skill.md` when the shared workflow or rules change.
- Update scripts in `scripts/` or `src/` when the pipeline behavior changes.
