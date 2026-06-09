---
name: video-to-skill
description: >-
  Turns video or transcript content into a project-local Agent Skill, or updates
  one already in the current repo. Never writes to global skill dirs. Accepts
  YouTube, Google Meet exports, Zoom/Teams/Loom captions, pasted transcripts,
  and other sources. Use when the user wants to create or update a skill from a
  video, meeting, webinar, tutorial, transcript, talk, or lecture.
---

# Video to Skill

Turn video or transcript knowledge into a **project-local** [Agent Skill](https://agentskills.io) — create new or update existing **in the current repo only**. Quality validation runs internally during build, not as separate eval files.

Follow [Agent Skills best practices](https://agentskills.io/specification): concise `SKILL.md`, progressive disclosure via `reference.md`, third-person description, delta-only content.

## Project-only policy

**All generated skills stay in the current project.** Never create, install, or write skills under global paths (`~/.cursor/skills/`, `~/.agents/skills/`, `~/.claude/skills/`, etc.). Do not suggest global install (`-g`) for output skills.

Valid output roots (project-relative, pick **one** per session):

| Agent / tool | Project path |
|--------------|--------------|
| Cursor | `.cursor/skills/<name>/` |
| Open standard | `.agents/skills/<name>/` |
| Claude Code | `.claude/skills/<name>/` |
| Codex | `.codex/skills/<name>/` |

The user chooses exactly **one** directory. Never write the same skill to multiple roots.

## Prerequisites

For auto-fetch and file parsing, install dependencies once per machine. Run commands from **this skill's install directory** (where `requirements.txt` and `scripts/` live — typically `~/.cursor/skills/video-to-skill/` or `.cursor/skills/video-to-skill/` in Cursor; `.agents/skills/video-to-skill/` for open-standard installs):

```bash
python3 -m pip install -r requirements.txt
```

See [providers.md](providers.md) for export steps per platform.

## Workflow

```
Task Progress:
- [ ] Step 1: Identify input source(s)
- [ ] Step 2: Load transcript(s)
- [ ] Step 3: Present topics overview
- [ ] Step 4: Detect existing skill in current project
- [ ] Step 5: Choose mode — replace, modify, or add (if exists) / create new
- [ ] Step 6: Confirm which video parts to include
- [ ] Step 7: Choose project skills directory (.cursor / .agents / .claude / .codex — one only)
- [ ] Step 8: Filter transcript content
- [ ] Step 9: Build and validate skill (internal eval loop)
- [ ] Step 10: Design file split (SKILL.md + reference.md)
- [ ] Step 11: Write or merge skill files
- [ ] Step 12: Confirm with user
```

### Step 1: Identify input source(s)

Accept **one or many** sources in a single session. Sources can be mixed (e.g. YouTube tutorial + Google Meet team discussion).

| Source | How to detect | Action |
|--------|---------------|--------|
| **YouTube URL** | `youtube.com`, `youtu.be`, or 11-char video ID | → [YouTube](#youtube-auto-fetch) |
| **Google Meet** | `.sbv`/`.vtt` file, "meet" in filename, Meet URL, pasted Gemini notes | → [Meet export](#google-meet) |
| **Zoom** | `.vtt` from cloud recording, "zoom" in filename | → [Zoom export](#zoom) |
| **Microsoft Teams** | `.vtt` from meeting recap, Teams URL | → [Teams export](#teams) |
| **Loom** | `.txt` export, Loom URL | → [Loom export](#loom) |
| **Vimeo** | `.vtt` captions, Vimeo URL | → [Vimeo export](#vimeo) |
| **Meeting notes** | Otter, Fireflies, Grain export (`.txt`/`.srt`) | → [File import](#file-import) |
| **Subtitle file** | `.vtt`, `.srt`, `.sbv` path | → [File import](#file-import) |
| **Pasted transcript** | User pastes text in chat | → [Pasted text](#pasted-text) |
| **Unknown URL** | Other `http(s)://` link | Show [providers.md](providers.md); ask for export or paste |

Full export guides: [providers.md](providers.md)

If unclear, ask:

> What do you have — a YouTube link, a meeting caption file (.vtt/.sbv), or a transcript to paste? You can provide multiple sources for one skill.

#### Collect multiple sources

When the user may have more than one source:

1. Load the first source in Step 2
2. Before Step 3, ask: **"Any other sources to include?"**
3. Load additional sources; merge into one payload
4. Cluster topics across all sources in Step 3
5. Cite every source in the skill's `## Source` section

### Step 2: Load transcript(s)

Use **`scripts/load_transcript.py`** as the single entry point (preferred over `fetch_transcript.py`).

#### YouTube (auto-fetch)

```bash
python3 scripts/load_transcript.py "<youtube-url>" -o /tmp/transcript.json
```

If English is unavailable:

```bash
python3 scripts/load_transcript.py "<youtube-url>" --list-only
python3 scripts/load_transcript.py "<youtube-url>" --languages es en -o /tmp/transcript.json
```

#### File import

Works for Google Meet `.sbv`, Zoom/Teams `.vtt`, `.srt`, and plain `.txt`:

```bash
python3 scripts/load_transcript.py path/to/meeting.vtt \
  --source google-meet \
  --title "Architecture sync" \
  -o /tmp/transcript.json
```

Set `--source` explicitly when the filename doesn't hint at the platform.

#### Google Meet

Meet URLs cannot be fetched automatically. Guide the user:

1. Drive recording → download **.sbv** subtitles, or
2. Meet → Activities → Transcripts → copy, or
3. Gemini meeting notes in Google Docs → paste

Then run file import or pasted text flow.

#### Zoom

Export **Audio transcript (.vtt)** from Zoom cloud recordings → file import with `--source zoom`.

#### Teams

Export **.vtt** from meeting recap or Stream → file import with `--source teams`.

#### Loom

Copy transcript from the Loom video page → save as `.txt` → file import with `--source loom`.

#### Vimeo

Download `.vtt` captions (if available) → file import with `--source vimeo`.

#### Pasted text

If the user pastes in chat (no file), normalize to the standard JSON shape and save as `/tmp/transcript.json`. Preserve inline timestamps like `[00:12:34]` when present. Or pipe via loader:

```bash
python3 scripts/load_transcript.py "paste content here" --source paste -o /tmp/transcript.json
```

#### Multiple sources

```bash
python3 scripts/load_transcript.py "<youtube-url>" meeting.vtt notes.txt \
  --merge -o /tmp/transcript.json
```

Merged payload has `"source": "multi"` and a `sources` array. Analyze each entry separately; timestamps are per-source.

On failure for any provider, show the relevant export steps from [providers.md](providers.md) and offer pasted transcript as fallback.

### Step 3: Present topics overview

Cluster content into **one main subject** and **subcategories**. With multiple sources, cluster **across all of them** — note which source contributed each subcategory when helpful.

```
Main subject: Playwright

Sources:
  1. YouTube — "Playwright Myths Busted" (56 min)
  2. Google Meet — "Team testing sync" (45 min)

Subcategories discussed:
  1. Test speed and page.goto tuning          YouTube ~14:32–20:28
  2. Flakiness and addLocatorHandler          YouTube ~21:46–39:02
  3. CI parallelization strategy              Meet ~0:15–12:00
  4. AI test generation with MCP              YouTube ~43:42–49:36
```

**Naming rules:**
- **Main subject** → skill name (`playwright`, not `playwright-flakiness`)
- **Subcategories** → sections in `SKILL.md` + matching sections in `reference.md`
- Multiple skills only when source covers **unrelated domains**

### Step 4: Detect existing skill in current project

**Hard gate — search the current project only.** Do not scan or write `~/` global skill directories. Do not default to `.agents/` without asking.

After identifying the main subject, Glob for `<main-subject>/SKILL.md` under **project** roots only:

```
.cursor/skills/<main-subject>/SKILL.md
.agents/skills/<main-subject>/SKILL.md
.claude/skills/<main-subject>/SKILL.md
.codex/skills/<main-subject>/SKILL.md
```

Also scan for similar skills when names may differ:

```bash
ls .cursor/skills .agents/skills .claude/skills .codex/skills 2>/dev/null
```

Read the first ~15 lines of plausible `SKILL.md` files. Treat as candidates when folder/`name` matches the subject or `description` covers the same domain.

| Found | Action |
|-------|--------|
| **No match in project** | → create-new path (Steps 5–12) |
| **One match** | Note its path; proceed to Step 5 (update mode) |
| **Same skill in multiple project roots** | Ask which copy to update; do not write to both |
| **Similar name, different topic** | Show candidate; confirm before updating |

**Read existing files** when a match is found:

```
skill-name/
├── SKILL.md        # read fully
├── reference.md    # read if present
└── examples.md     # read if present
```

### Step 5: Choose mode — replace, modify, or add

Use AskQuestion when available. **Skip this step** when no existing project skill was found — go straight to create-new.

**When a project skill exists**, ask how to apply the new video content:

| Mode | When to use | Behavior |
|------|-------------|----------|
| **Full replace** | User wants a clean rewrite from selected video parts | Rebuild `SKILL.md` + `reference.md` from confirmed scope; keep only structure/conventions worth preserving; refresh `## Source` |
| **Modify** | User wants to update existing sections | Present merge plan (NEW / ENRICH / SKIP / CONFLICT); patch matching sections in place |
| **Add** | User wants new content only | Add NEW sections; do not rewrite or remove existing sections unless user confirms |

For **modify**, present a merge plan before Step 6:

```
Existing skill: playwright (.cursor/skills/playwright/)

Merge plan:
  NEW       Component testing with mount()           ~12:00–18:30
  ENRICH    Flakiness — add clock mocking pattern     ~22:10–25:00
  SKIP      page.goto domcontentloaded                (already covered)
  CONFLICT  Prefer getByTestId for forms              (video says getByLabel — flag for user)
```

| Label | Meaning |
|-------|---------|
| **NEW** | Not in the skill — add section |
| **ENRICH** | Section exists — merge delta into it |
| **SKIP** | Already covered |
| **CONFLICT** | Contradicts existing guidance — ask user |

**Create new** (no existing skill): confirm skill name = main subject; proceed to Step 6.

### Step 6: Confirm which video parts to include

Present the Step 3 topic overview and ask **which subcategories or time ranges** from the video(s) should go into the skill.

| Question | Purpose |
|----------|---------|
| Include all listed subcategories, or only some? | Scope filter |
| Any time ranges to exclude? | Fine-grained filter |
| Exclude vendor promos, tangents, or unrelated domains? | Quality filter |

Respect answers strictly (e.g. "only Playwright flakiness" → exclude speed, MCP, Checkly sections).

**Modify/add modes:** default to user-selected parts only; SKIP items not in scope.

### Step 7: Choose project skills directory

Ask which **single** project root to use. Offer only project-relative options — never global paths.

**If the skill already exists in one project root**, default to that path. Only ask when creating new or when duplicates exist in multiple roots.

```
.cursor/skills/<name>/     ← Cursor
.agents/skills/<name>/     ← open standard
.claude/skills/<name>/     ← Claude Code
.codex/skills/<name>/      ← Codex
```

| Rule | Detail |
|------|--------|
| **One directory only** | Never write the same skill to `.cursor/` and `.agents/` in one session |
| **No global paths** | Never `~/.cursor/skills/`, `~/.agents/skills/`, etc. |
| **No silent default** | Do not pick `.agents/` unless the user chooses it |
| **Commit with repo** | Output is project-local so the team can share it |

Record the chosen path as `<skills-root>/<main-subject>/` for Steps 11–12.

### Step 8: Filter transcript content

Map confirmed subcategories to time ranges. Exclude opted-out segments.

**Single source:**

```bash
python3 scripts/load_transcript.py "<youtube-url>" --start 300 --end 720 -o /tmp/transcript-filtered.json
```

**Multi-source:** filter each source independently by its own timestamps, then re-merge. Do not mix timestamps across sources.

Distill only — never paste raw transcript into the skill.

### Step 9: Build and validate skill (internal eval loop)

Read [skill-output-template.md](skill-output-template.md) and [reference-template.md](reference-template.md). **Run this loop before writing files.** Do not create `evals/` directories or deliver eval artifacts to the user.

#### 9a. Draft from confirmed subcategories only

Split content mentally into two layers:

| Layer | File | Content |
|-------|------|---------|
| **Routing** | `SKILL.md` | Overview, When to Use, Quick Reference, Agent Instructions, top pitfalls, links |
| **Depth** | `reference.md` | Full subcategory guidance, extended examples, detailed pitfalls, edge cases |

Transformation rules:
1. One skill per main subject; subcategories are paired sections in both files
2. Distill procedures and decisions — not "the speaker said"
3. Reorder by utility, not video chronology
4. Generalize examples (no demo-specific strings from the video)
5. Explain *why* for non-obvious rules
6. **No duplicate paragraphs** across SKILL.md and reference.md — SKILL.md summarizes and links; reference.md holds depth

#### 9b. Internal validation (do not skip)

For **each confirmed subcategory**, mentally run this check:

1. **Write one realistic user prompt** the skill should handle (casual phrasing, real context).
2. **Simulate baseline response** — on **create**: general knowledge alone; on **update**: existing skill content alone.
3. **Identify the delta** — APIs, patterns, or decision trees the video adds beyond the baseline.
4. **Keep only delta content**. Remove anything the baseline already covers.
5. **Define pass criteria** (internal, not written to disk):
   - Uses the recommended pattern from the source
   - Avoids known anti-patterns the source warns about
   - Includes correct syntax/API names
   - Gives actionable steps, not summary prose

If a section fails: tighten instructions, add a bad/good code pair, or cut the section.

Run **2–3 prompts total** across subcategories (not one per section — stay lean). Revise draft until each would pass.

#### 9c. Lean pass

Before finalizing:
- Remove duplicate guidance across Quick Reference, Agent Instructions, and Pitfalls
- Remove duplicate guidance between SKILL.md and reference.md
- Remove generic filler the model already knows
- Remove vendor/product content excluded by user scope
- Prefer one strong example per pattern over many weak ones
- No transcript quotes, speaker names in body, or webinar housekeeping

#### 9d. Frontmatter

On **modify/add**: revise `description` only when new subcategories add trigger terms. On **full replace**, rewrite frontmatter to match the new scope.

```yaml
---
name: main-subject
description: >-
  Third-person description. WHAT the skill does + WHEN to use it.
  Include trigger terms for main subject AND included subcategories.
---
```

Rules:
- **Third person** ("Writes and debugs…"), never "I can help you…"
- **WHAT + WHEN** — capabilities and trigger terms
- Max 1024 chars; lowercase hyphens in `name`; `name` must match parent folder per [spec](https://agentskills.io/specification)
- Output only under the project path chosen in Step 7
- **Never** create skills in `~/.cursor/skills-cursor/` (Cursor internal directory)

### Step 10: Design file split

Plan the output directory **before writing**. Default to progressive disclosure — do not put everything in one file.

```
skill-name/
├── SKILL.md        # required — routing layer (~150–300 lines target)
├── reference.md    # required — depth layer (default for all generated skills)
└── examples.md     # optional — only when 4+ full copy-paste examples
```

#### What goes where

| Content | SKILL.md | reference.md | examples.md |
|---------|----------|--------------|-------------|
| Overview, When to Use | ✓ | | |
| Quick Reference table | ✓ | | |
| Agent Instructions (top scenarios) | ✓ | | |
| Subcategory core pattern (1 good/bad pair) | ✓ brief | ✓ full | |
| Decision trees, diagnosis steps | link | ✓ | |
| Extended code examples | link | ✓ | ✓ if many |
| Full pitfalls table | top 5–8 | ✓ complete | |
| Source timestamps | ✓ summary | ✓ per-section | |

#### reference.md rules

- **Always create** `reference.md` for generated skills (even single-subcategory sources)
- One `##` section per confirmed subcategory, using kebab-case anchor-friendly headings
- Include `## Detailed Pitfalls` and `## Source Detail` at the bottom
- Follow [reference-template.md](reference-template.md)
- Links from SKILL.md must be **one level deep** — link directly to `reference.md`, not nested files

#### SKILL.md size targets

| Metric | Target |
|--------|--------|
| SKILL.md lines | 150–300 ideal; **hard max 500** |
| If draft exceeds 300 lines | Move subcategory depth to reference.md |
| examples.md | Create when 4+ full examples would bloat reference.md |

#### Optional examples.md

Create only when the skill has many complete, copy-pasteable examples (e.g. 4+ multi-step test files). Keep SKILL.md and reference.md lean; put standalone examples in `examples.md` and link from both.

### Step 11: Write or merge skill files

Write to **only** the path chosen in Step 7:

```
<skills-root>/<main-subject>/     # e.g. .cursor/skills/playwright/
├── SKILL.md                      # required
├── reference.md                  # required (default)
└── examples.md                   # optional
```

#### Full replace

Rewrite files from the validated draft. Replace `SKILL.md` and `reference.md` content for the confirmed scope. Rebuild `## Source` for all included sources.

#### Modify / add

**Merge, don't blindly replace.** Preserve existing structure, heading names, and conventions.

| File | Merge rules |
|------|-------------|
| `SKILL.md` | Add NEW sections; patch ENRICH sections; update Quick Reference and Agent Instructions; keep routing lean |
| `reference.md` | Add/expand matching sections; create file if missing (migrate depth from bloated SKILL.md) |
| `examples.md` | Append new examples; dedupe near-identical ones |
| `description` | Append new trigger terms if subcategories were added |

**Source section** — append, never overwrite. List **every source** with platform label:

```markdown
## Source

Generated from:
- [Playwright Myths Busted](https://youtube.com/...) (YouTube) — speed, flakiness, MCP
- Architecture sync (Google Meet, 2025-06-08) — CI parallelization (0:15–12:00)
```

For file-based sources without a URL, use: `Title (Google Meet)` or the file path.

If the skill had no Source section, add one covering all provenance.

**Do not** write `evals/`, workspace dirs, or grading files.

After writing, verify:
- [ ] Every SKILL.md subcategory links to its reference.md section
- [ ] No paragraph duplicated verbatim between files
- [ ] SKILL.md under 500 lines
- [ ] reference.md covers all confirmed subcategories in full
- [ ] File references are one level deep
- [ ] **Modify/add only:** existing content preserved; merge plan items applied; no redundant restatements
- [ ] **Full replace only:** old content fully superseded by confirmed scope

### Step 12: Confirm with user

Show:
1. Project skill path (e.g. `.cursor/skills/playwright/`) and invocation (`@skill-name`)
2. Mode: **created** / **full replace** / **modify** / **add**
3. Files written (`SKILL.md`, `reference.md`, `examples.md` if any)
4. Subcategories included (and excluded, if any)
5. **Modify/add only:** merge summary (NEW / ENRICH / SKIP counts)
6. `description` field (note if trigger terms were added)

Ask once for adjustments. Do not expose internal validation steps unless the user asks.

## Skill Authoring Best Practices

Apply on every generated skill:

### Progressive disclosure
- SKILL.md = what to do and where to look
- reference.md = how and why in depth
- Agent reads SKILL.md first; loads reference.md when the task needs detail

### Concise routing layer
- Assume the agent is already capable — only add delta knowledge
- Quick Reference table routes common prompts to the right section
- Agent Instructions cover the top 3–4 user scenarios

### Quality
- Third-person description with trigger terms
- Consistent terminology throughout (pick one term, don't mix)
- Generalized, copy-pasteable examples — not demo-specific strings
- Bad/good code pairs for non-obvious anti-patterns

### Structure
- Subcategory headings match between SKILL.md and reference.md
- Use markdown links: `[reference.md — Speed](reference.md#speed)`
- Source section cites every source with platform label, URL or date, and timestamps

## Providers

| Provider | Auto-fetch | Loader | Export guide |
|----------|------------|--------|--------------|
| YouTube | Yes | `load_transcript.py` | — |
| Google Meet | No | file / paste | [providers.md](providers.md) |
| Zoom | No | `.vtt` file | [providers.md](providers.md) |
| Microsoft Teams | No | `.vtt` file | [providers.md](providers.md) |
| Loom | No | `.txt` paste/file | [providers.md](providers.md) |
| Vimeo | No | `.vtt` file | [providers.md](providers.md) |
| Otter / Fireflies / Grain | No | `.txt` / `.srt` | [providers.md](providers.md) |
| Pasted text | N/A | inline / loader | — |
| Multi-source | Mixed | `--merge` | [providers.md](providers.md) |

Legacy: `scripts/fetch_transcript.py` (YouTube only). Prefer `load_transcript.py`.

## Build-Time Quality Checklist

Run internally before Step 11:

- [ ] Step 4 completed: searched project `.cursor/skills/`, `.agents/skills/`, `.claude/skills/`, `.codex/skills/` only — no global paths
- [ ] If existing skill found: user chose replace, modify, or add before scope questions
- [ ] Step 7 completed: exactly one project skills directory chosen — never global, never multiple roots
- [ ] Every section maps to a user-confirmed subcategory
- [ ] Each subcategory survived the without-skill delta test
- [ ] Quick Reference routes common prompts to the right section
- [ ] Agent Instructions cover top 3–4 user scenarios
- [ ] Examples are generalized, copy-pasteable
- [ ] No excluded topics (vendor promos, out-of-scope tangents)
- [ ] No eval artifacts in output
- [ ] SKILL.md under 500 lines (ideally 150–300)
- [ ] reference.md created with full subcategory depth
- [ ] SKILL.md links to reference.md sections (one level deep)
- [ ] No duplicate content between SKILL.md and reference.md
- [ ] Description is third-person with WHAT + WHEN
- [ ] **Modify/add only:** delta tested against existing skill, not just general knowledge
- [ ] **Modify/add only:** Source section appended with new video entry
- [ ] **Full replace only:** Source section rebuilt for included sources

## Error Handling

| Error | Action |
|-------|--------|
| Transcripts disabled (YouTube) | Ask for pasted transcript |
| No transcript for language | Run `--list-only`, let user pick |
| Video unavailable | Verify URL; offer pasted transcript |
| Meet/Zoom/Teams URL only | Show export steps in [providers.md](providers.md) |
| Unrecognized file format | Ask for `.vtt`, `.srt`, `.sbv`, or plain text |
| Unrelated domains in one video | Suggest multiple skills |
| Multi-source timestamp overlap | Keep sources separate; don't merge timelines |

## Example Sessions

### Create new (no existing project skill)

**User:** Create a skill from https://www.youtube.com/watch?v=kFv0bRH78xM — Playwright topics only

**Agent:**
1. Fetches transcript → main subject **Playwright**, 4 subcategories
2. Searches project skill dirs → no `playwright/SKILL.md` found
3. User picks subcategories (excludes Checkly monitoring)
4. User chooses `.cursor/skills/playwright/` (not `.agents/`, not global)
5. Runs internal eval loop → keeps `addLocatorHandler`, `domcontentloaded`; drops generic filler
6. Writes `.cursor/skills/playwright/SKILL.md` + `reference.md`
7. Confirms project path, files, subcategories, `@playwright`

### Modify existing project skill

**User:** Update our Playwright skill from https://www.youtube.com/watch?v=NEW_ID — component testing section only

**Agent:**
1. Fetches transcript → finds **Component testing** (~12:00–18:30) and minor **Flakiness** additions
2. Finds `.cursor/skills/playwright/SKILL.md` in project → reads existing files
3. Asks mode → user picks **modify** (not full replace)
4. User confirms only component testing + flakiness clock-mocking parts
5. Merge plan: NEW component testing; ENRICH flakiness; SKIP speed
6. Merges into `.cursor/skills/playwright/`; appends Source entry
7. Confirms path, mode, merge summary

### Skill already exists — user picks mode

**User:** Create a skill from [YouTube URL] — Playwright topics only

**Agent:**
1. Fetches transcript → main subject **Playwright**
2. Finds `.cursor/skills/playwright/SKILL.md` in project
3. Asks: **full replace**, **modify**, or **add**? User picks **add**
4. User selects which new subcategories to include
5. Adds NEW sections only; preserves existing content
6. Confirms `.cursor/skills/playwright/`, mode=add, sections added

### Multi-source

**User:** Create a Playwright skill from this YouTube link AND our Meet recording (`sprint.vtt`)

**Agent:**
1. Loads both → merged payload with 2 sources
2. Clusters topics across YouTube (speed, flakiness) and Meet (CI strategy)
3. No existing skill → user picks scope and `.cursor/skills/playwright/`
4. Writes skill citing both sources in `## Source`
5. Confirms project path and `@playwright`
