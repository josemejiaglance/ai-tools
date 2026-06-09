---
name: video-to-skill
description: >-
  Turns video or transcript content into an Agent Skill (open standard), or
  updates an existing skill with new knowledge. Accepts YouTube, Google Meet
  exports, Zoom/Teams/Loom captions, pasted transcripts, and other common
  sources. Supports multiple sources per skill. Use when the user wants to
  create or update a skill from a video, meeting, webinar, tutorial, transcript,
  talk, or lecture.
---

# Video to Skill

Turn video or transcript knowledge into a reusable [Agent Skill](https://agentskills.io) — **create new** or **update existing**. Output works with Cursor, Codex, Claude Code, and any agent that supports the open standard. **Deliver the final skill directory** — quality validation runs internally during build, not as separate eval files.

Follow [Agent Skills best practices](https://agentskills.io/specification): concise `SKILL.md`, progressive disclosure via `reference.md`, third-person description, delta-only content.

## Prerequisites

For auto-fetch and file parsing, install dependencies once per machine. Run commands from **this skill directory** (where `requirements.txt` and `scripts/` live):

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
- [ ] Step 4: Detect existing skill → create or update path
- [ ] Step 5: Confirm scope and subcategories
- [ ] Step 6: Filter transcript content
- [ ] Step 7: Build and validate skill (internal eval loop)
- [ ] Step 8: Design file split (SKILL.md + reference.md)
- [ ] Step 9: Write or merge skill files
- [ ] Step 10: Confirm with user
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

### Step 4: Detect existing skill → create or update path

**Hard gate — complete before any save-location or create questions.** If you have not searched the filesystem, you may not ask "Where should the skill be saved?" or default to creating under `.agents/`.

After identifying the main subject, **search yourself** using Glob/Read/Shell — no helper script required. This should take seconds.

#### 4a. Exact name check

Glob for `<main-subject>/SKILL.md` under every standard root (Cursor first):

| Scope | Paths |
|-------|-------|
| Personal | `~/.cursor/skills/`, `~/.agents/skills/`, `~/.claude/skills/`, `~/.codex/skills/` |
| Project | `.cursor/skills/`, `.agents/skills/`, `.claude/skills/`, `.codex/skills/` |

Example globs (replace `playwright` with the main subject):

```
~/.cursor/skills/playwright/SKILL.md
~/.agents/skills/playwright/SKILL.md
.cursor/skills/playwright/SKILL.md
.agents/skills/playwright/SKILL.md
```

#### 4b. Similar-skill scan (when exact match is missing or names may differ)

List skill folders and skim frontmatter `name` + `description`:

```bash
ls ~/.cursor/skills ~/.agents/skills .cursor/skills .agents/skills 2>/dev/null
```

For each plausible folder, read the first ~15 lines of `SKILL.md`. Treat as **update candidates** when:

- Folder or `name` contains the main subject (`playwright-e2e` ↔ `playwright`)
- `description` covers the same domain (shared trigger terms, same library/framework)

**When candidates exist**, show full paths and ask **update existing vs create new** — do not jump to save-location as if nothing exists.

Also honor explicit user intent: "update `@playwright`", "add to my existing skill", "use my `.cursor/skills`", or a path they provide.

| Found | Action |
|-------|--------|
| **No existing skill** | → [Create path](#create-path) (Steps 5–10) |
| **One match** | **Default to update.** Present merge plan (below); only offer "create new duplicate" if user rejects update |
| **Match in `~/.cursor/skills/`** | Prefer updating there — do not write to `~/.agents/skills/` unless user explicitly asks |
| **Both project and personal** | Ask which location to update (default: personal `~/.cursor/skills/` if it exists) |
| **Same name in `.cursor/skills/` and `.agents/skills/`** | Ask which to update; **never silently pick `.agents/`** |
| **Name mismatch but similar topic** | Show candidate(s); ask update vs new name |

**Read existing files before proceeding on the update path:**

```
skill-name/
├── SKILL.md        # read fully
├── reference.md    # read if present
└── examples.md     # read if present
```

Note: older skills may lack `reference.md`. Plan to create or backfill it during the update.

#### Update path — diff against existing skill

Compare the new video's subcategories to what's already in the skill. Present a merge plan:

```
Existing skill: playwright (~/.cursor/skills/playwright/)

Merge plan:
  NEW       Component testing with mount()           ~12:00–18:30
  ENRICH    Flakiness — add clock mocking pattern     ~22:10–25:00
  SKIP      page.goto domcontentloaded                (already covered)
  CONFLICT  Prefer getByTestId for forms              (video says getByLabel — flag for user)
```

| Label | Meaning |
|-------|---------|
| **NEW** | Subcategory or pattern not in the skill — add section |
| **ENRICH** | Section exists but video adds delta — merge into existing section |
| **SKIP** | Already covered; no new delta vs existing skill content |
| **CONFLICT** | Contradicts existing guidance — ask user which to keep |

Run the without-skill delta test (Step 7b) **against the existing skill**, not just general knowledge. Content must be new relative to what's already written.

#### Create path

No existing skill, or user chose to create a new one (use a distinct name if the topic diverges).

### Step 5: Confirm scope and subcategories

Use AskQuestion when available.

**Create path** (only after Step 4 confirms no suitable existing skill):

| Question | Purpose |
|----------|---------|
| Create a skill for **[main subject]**? | Confirms skill name |
| Include all subcategories, or exclude some? | Scope filter |
| Where to save? | See [Storage locations](#storage-locations) — offer all relevant options |

**AskQuestion options for save location** — always include Cursor paths; never offer only `.agents/`:

```
Personal — ~/.cursor/skills/<name>/          ← default for Cursor users
Project  — .cursor/skills/<name>/ in this repo
Personal — ~/.agents/skills/<name>/          ← only if user wants open-standard / npx skills layout
Project  — .agents/skills/<name>/ in this repo
```

If the user said they use `.cursor/skills`, skip the agents options unless they ask for them.

**Update path:**

| Question | Purpose |
|----------|---------|
| Update **[existing skill]** with new content? | Confirms target |
| Merge **NEW** and **ENRICH** items from the plan? | Scope filter (SKIP excluded by default) |
| Resolve **CONFLICT** items how? | keep existing / adopt new / blend |
| Update project, personal, or both? | Target location |

Respect scope filters strictly (e.g. "only Playwright-related" → exclude vendor/product sections like Checkly deploy).

### Step 6: Filter transcript content

Map confirmed subcategories to time ranges. Exclude opted-out segments.

**Single source:**

```bash
python3 scripts/load_transcript.py "<youtube-url>" --start 300 --end 720 -o /tmp/transcript-filtered.json
```

**Multi-source:** filter each source independently by its own timestamps, then re-merge. Do not mix timestamps across sources.

Distill only — never paste raw transcript into the skill.

### Step 7: Build and validate skill (internal eval loop)

Read [skill-output-template.md](skill-output-template.md) and [reference-template.md](reference-template.md). **Run this loop before writing files.** Do not create `evals/` directories or deliver eval artifacts to the user.

#### 7a. Draft from confirmed subcategories only

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

#### 7b. Internal validation (do not skip)

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

#### 7c. Lean pass

Before finalizing:
- Remove duplicate guidance across Quick Reference, Agent Instructions, and Pitfalls
- Remove duplicate guidance between SKILL.md and reference.md
- Remove generic filler the model already knows
- Remove vendor/product content excluded by user scope
- Prefer one strong example per pattern over many weak ones
- No transcript quotes, speaker names in body, or webinar housekeeping

#### 7d. Frontmatter

On **update**: revise `description` only when new subcategories add trigger terms. Do not rewrite unrelated sections of frontmatter.

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
- Default output to `~/.cursor/skills/` when running in Cursor; use `.agents/skills/`, `.claude/skills/`, `.codex/skills/`, or another tool path only when the user chooses it
- **Never** create skills in `~/.cursor/skills-cursor/` (Cursor internal directory)

### Step 8: Design file split

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

### Step 9: Write or merge skill files

#### Create path

Write the full skill directory to the **confirmed** location:

```
~/.cursor/skills/<main-subject>/        # personal (Cursor — default)
.cursor/skills/<main-subject>/          # project (Cursor)
~/.agents/skills/<main-subject>/        # personal (open standard / npx skills)
.agents/skills/<main-subject>/          # project (open standard)

├── SKILL.md                            # required
├── reference.md                        # required (default)
└── examples.md                         # optional
```

#### Storage locations

Skills can live under any agent's standard directory — **the user's tool and existing install win**, not a fixed default.

| Tool / context | Personal path | Project path | When to use |
|----------------|---------------|--------------|-------------|
| **Cursor** (default here) | `~/.cursor/skills/<name>/` | `.cursor/skills/<name>/` | User works in Cursor; `@skill` resolves here |
| Open standard / `npx skills` | `~/.agents/skills/<name>/` | `.agents/skills/<name>/` | User explicitly wants agents layout |
| Claude Code | `~/.claude/skills/<name>/` | `.claude/skills/<name>/` | User says they use Claude |
| Codex | `~/.codex/skills/<name>/` | `.codex/skills/<name>/` | User says they use Codex |
| Custom | Path user provides | — | Honor verbatim |

| Situation | Action |
|-----------|--------|
| Existing skill found in Step 4 | **Update that path** — do not ask save location unless duplicates exist in multiple roots |
| User says "my skills" / `@skill` | Use the path discovery returned |
| Same name in `.cursor/` and `.agents/` | Ask which to update; **never silently pick `.agents/`** |
| No existing skill, Cursor session | Default offer: `~/.cursor/skills/<name>/` first |

**Never** create skills in `~/.cursor/skills-cursor/` (Cursor built-ins only).

#### Update path

**Merge, don't replace.** Preserve existing structure, heading names, and conventions unless the user asked for a rewrite.

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
- [ ] **Update only:** existing content preserved; merge plan items applied; no redundant restatements

### Step 10: Confirm with user

Show:
1. Skill path and invocation (`@skill-name` in Cursor, `/skill-name` where slash commands are supported)
2. Mode: **created** or **updated**
3. Files written (`SKILL.md`, `reference.md`, `examples.md` if any)
4. Subcategories included (and excluded, if any)
5. **Update only:** merge summary (NEW / ENRICH / SKIP counts)
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

Run internally before Step 9:

- [ ] Step 4 completed: globbed exact name + listed similar skills across `.cursor/skills/` and `.agents/skills/` (personal + project)
- [ ] If existing skill found: merge plan shown before create/save questions
- [ ] Output path matches user choice — default `~/.cursor/skills/` for Cursor, not `.agents/` unless requested
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
- [ ] **Update only:** delta tested against existing skill, not just general knowledge
- [ ] **Update only:** Source section appended with new video entry

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

### Create

**User:** Create a skill from https://www.youtube.com/watch?v=kFv0bRH78xM — Playwright topics only

**Agent:**
1. Fetches transcript → main subject **Playwright**, 4 subcategories
2. No existing skill found → create path
3. Confirms scope (excludes Checkly monitoring) and save location
4. Runs internal eval loop: flaky-login prompt → keeps `addLocatorHandler`; slow-goto prompt → keeps `domcontentloaded`; drops generic "use getByRole" filler
5. Designs split: SKILL.md (routing + quick patterns) + reference.md (full flakiness/speed/MCP depth)
6. Writes `~/.cursor/skills/playwright/SKILL.md` and `~/.cursor/skills/playwright/reference.md`
7. Confirms path, files, subcategories, `@playwright`

### Update

**User:** Update `@playwright` from https://www.youtube.com/watch?v=NEW_ID — component testing section only

**Agent:**
1. Fetches transcript → finds **Component testing** (~12:00–18:30) and minor **Flakiness** additions
2. Searches `~/.cursor/skills/playwright/` → **found**; reads `SKILL.md` + `reference.md`
3. Merge plan: NEW component testing; ENRICH flakiness (clock mocking); SKIP speed (already covered)
4. User confirms ENRICH + NEW, skips the rest
5. Delta test vs existing skill → keeps clock mocking pattern; drops repeated `domcontentloaded` advice
6. Merges into existing files; creates `## Component Testing` section; appends Source entry
7. Confirms updated path, merge summary, new trigger terms in description

### Create when skill already exists

**User:** Create a skill from [YouTube URL] — Playwright topics only

**Agent:**
1. Fetches transcript → main subject **Playwright**
2. Searches skill dirs → finds `~/.cursor/skills/playwright/SKILL.md`
3. **Does not ask "where to save" as if nothing exists.** Presents merge plan and asks: update existing `@playwright` or create a differently named skill?
4. User chooses **update** → merge path (NEW / ENRICH / SKIP)
5. Merges into `~/.cursor/skills/playwright/`; appends Source entry
6. Confirms updated path and merge summary

### Multi-source

**User:** Create a Playwright skill from this YouTube link AND our Meet recording (`sprint.vtt`)

**Agent:**
1. Loads both → merged payload with 2 sources
2. Clusters topics across YouTube (speed, flakiness) and Meet (CI strategy)
3. User confirms scope
4. Writes skill citing both sources in `## Source`
5. Confirms files and `@playwright`
