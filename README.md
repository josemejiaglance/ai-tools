# ai-tools

A collection of tools and [Cursor Agent Skills](https://cursor.com/docs/context/skills) for building AI-assisted workflows.

## Contents

| Path | Description |
|------|-------------|
| [skills-generator/](skills-generator/) | Turn videos and transcripts into reusable Cursor skills |

## Quick start

Clone the repository and open it in [Cursor](https://cursor.com):

```bash
git clone git@github.com:josemejiaglance/ai-tools.git
cd ai-tools
```

### Use an existing skill

Copy a skill into your project or personal skills directory:

```bash
# Project-scoped (shared with the team)
cp -r skills-generator/.cursor/skills/checkly /path/to/your-project/.cursor/skills/

# Personal (available in all workspaces)
mkdir -p ~/.cursor/skills
cp -r skills-generator/.cursor/skills/checkly ~/.cursor/skills/checkly
```

Then invoke it in Agent chat with `@checkly`.

### Generate a new skill from a video

See [skills-generator/README.md](skills-generator/README.md) for setup and the `@video-to-skill` workflow.

## Included skills

| Skill | Description |
|-------|-------------|
| [checkly](skills-generator/.cursor/skills/checkly/) | Checkly network monitoring as code — DNS, TCP, ICMP, CLI workflows |
| [video-to-skill](skills-generator/.cursor/skills/video-to-skill/) | Meta-skill that turns videos and transcripts into new skills |

## Requirements

- [Cursor](https://cursor.com) with Agent Skills enabled
- Python 3.10+ (for transcript tooling in `skills-generator/`)

## License

Use and adapt freely. Third-party trademarks belong to their respective owners.
