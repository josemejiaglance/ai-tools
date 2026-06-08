# Checkly Agent Skill

An [Agent Skill](https://agentskills.io) for Checkly network monitoring as code — DNS, TCP, and ICMP checks, CLI workflows, and API network diagnostics.

## Install

```bash
npx skills add josemejiaglance/ai-tools@checkly
```

Options:

```bash
# Cursor only, skip prompts
npx skills add josemejiaglance/ai-tools@checkly -a cursor -y

# Global install (all projects)
npx skills add josemejiaglance/ai-tools@checkly -g -y
```

Manual copy also works — see the [root README](../../README.md).

## Usage

```
@checkly
```

Example prompts:

- "Set up a DNS check for my domain with Cloudflare resolver"
- "Export my Checkly UI checks to a CLI project"
- "Why is my API check failing with a network error?"

## What it covers

- DNS, TCP, and ICMP monitoring
- Monitoring as Code — UI → CLI export, `checkly test`
- API check diagnostics — pcap, tracert, Rocky AI
- Private locations for on-prem checks

## Source

Generated from [Network Monitoring as Code](https://www.youtube.com/watch?v=rgAwZo9JiOk) (YouTube).

## License

Community documentation — not an official Checkly product.
