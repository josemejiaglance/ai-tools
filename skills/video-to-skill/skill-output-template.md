---
name: main-subject
description: >-
  Third-person description of the full subject and its key areas.
  WHAT the skill does + WHEN to use it.
  Include trigger terms for the main subject AND all included subcategories.
---

# Main Subject

## Overview

One paragraph on the subject's purpose and what this skill enables the agent to do.

## When to Use

- Trigger tied to the main subject
- Trigger tied to a subcategory
- Trigger tied to another subcategory

## Quick Reference

| Situation | Approach |
|-----------|------------|
| User asks about X | Do Y — see [reference.md](reference.md#section) |
| User asks about A | Do B |

## [Subcategory One]

Core principle and the highest-value pattern in 5–15 lines. Link to reference for depth:

→ Full guidance: [reference.md — Subcategory One](reference.md#subcategory-one)

```typescript
// Minimal good/bad pair or one canonical pattern
```

## [Subcategory Two]

→ Full guidance: [reference.md — Subcategory Two](reference.md#subcategory-two)

## Agent Instructions

**When the user asks to [scenario 1]:** ...

**When the user reports [scenario 2]:** Start with ...

**When the user asks about [scenario 3]:** ...

For extended examples and edge cases, read [reference.md](reference.md).

## Common Pitfalls

Top 5–8 pitfalls only — table or bullets. Full list in [reference.md](reference.md#detailed-pitfalls).

| Pitfall | Fix |
|---------|-----|
| ... | ... |

## Additional Resources

- Detailed subcategory guidance: [reference.md](reference.md)
- Extended copy-paste examples: [examples.md](examples.md) *(if created)*

## Source

Generated from: [Title](source-url)

Subcategories included:
- Subcategory one: MM:SS–MM:SS
- Subcategory two: MM:SS–MM:SS

Excluded (if any):
- ...

---

## Updating an Existing Skill

When merging into an existing skill, do not replace files wholesale. Patch in place:

| Merge label | SKILL.md | reference.md |
|-------------|----------|--------------|
| **NEW** | Add section + Quick Reference row + Agent Instruction | Add full `##` section |
| **ENRICH** | Update brief summary if routing changed | Expand existing section |
| **SKIP** | No change | No change |

Append to Source (never overwrite prior entries). Include platform label for each:

```markdown
## Source

Generated from:
- [First Video](url) (YouTube) — original subcategories: ...
- Sprint review (Google Meet, 2025-06-08) — added: CI parallelization (0:15–12:00)
- [Second Video](url) (YouTube) — added: subcategory X (MM:SS–MM:SS)
```
