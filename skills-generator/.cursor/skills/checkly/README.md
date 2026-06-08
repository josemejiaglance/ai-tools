# Checkly Cursor Skill

A [Cursor Agent Skill](https://cursor.com/docs/context/skills) for Checkly network monitoring as code — DNS, TCP, and ICMP checks, CLI workflows, and API network diagnostics.

Generated from the [Network Monitoring as Code](https://www.youtube.com/watch?v=rgAwZo9JiOk) webinar.

## What it covers

- **DNS monitoring** — custom resolvers, assertions, JSON path expressions
- **TCP monitoring** — port connectivity and response assertions
- **ICMP (ping) monitoring** — packet loss, latency, multi-region runs
- **Monitoring as Code** — UI → CLI export, `checkly test`, CI deploy
- **API check diagnostics** — pcap capture, tracert, Rocky AI debugging
- **Private locations** — on-prem and internal network checks

## Requirements

- [Cursor](https://cursor.com) with Agent Skills enabled
- A Checkly account (for applying the guidance — the skill itself is just documentation)

## Install

### Option 1 — Copy into a project (team sharing)

Clone or copy this folder into your repository:

```bash
git clone <this-repo-url>
cp -r skills-generator/.cursor/skills/checkly /path/to/your-project/.cursor/skills/
```

Anyone who opens the project in Cursor can invoke `@checkly`.

### Option 2 — Personal install (all projects)

Copy the skill to your user skills directory:

```bash
mkdir -p ~/.cursor/skills
cp -r /path/to/checkly ~/.cursor/skills/checkly
```

The skill is available in every workspace you open in Cursor.

### Option 3 — Skills CLI

If this skill is published to a GitHub repository:

```bash
npx skills add <owner>/<repo>@checkly
```

Browse installable skills at [skills.sh](https://skills.sh/).

## Usage

In Cursor Agent chat, reference the skill with:

```
@checkly
```

Example prompts:

- "Set up a DNS check for my domain with Cloudflare resolver"
- "Export my Checkly UI checks to a CLI project"
- "Why is my API check failing with a network error?"
- "Configure ICMP monitoring for internal servers via private locations"

The agent reads `SKILL.md` first for routing, then loads `reference.md` when it needs detailed guidance.

## Files

```
checkly/
├── SKILL.md       # Main skill — quick reference and agent instructions
├── reference.md   # Deep-dive per topic
└── README.md      # This file
```

## Updating

To regenerate or extend this skill from new video content, use the [video-to-skill](../video-to-skill/SKILL.md) workflow in this repository:

```
/video-to-skill
```

Then provide a YouTube URL or transcript and ask to update `@checkly`.

## Source

| Source | Topics |
|--------|--------|
| [Network Monitoring as Code](https://www.youtube.com/watch?v=rgAwZo9JiOk) (YouTube) | DNS, TCP, ICMP, MaC workflow, API diagnostics, private locations |

## License

Use and adapt freely. Checkly is a trademark of Checkly GmbH; this skill is community documentation, not an official Checkly product.
