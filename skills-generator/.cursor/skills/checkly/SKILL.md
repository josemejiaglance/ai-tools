---
name: checkly
description: >-
  Configures and debugs Checkly network and uptime monitoring as code. Covers
  DNS, TCP, and ICMP checks, UI-to-CLI export, checkly test/deploy workflow,
  API check network diagnostics (pcap, tracert), Rocky AI debugging, and
  private locations for on-prem checks. Use when working with Checkly, monitoring
  as code, DNS/TCP/ICMP uptime checks, network layer monitoring, checkly CLI,
  or debugging Checkly API check network failures.
---

# Checkly

Guidance for Checkly network monitoring as code — DNS, TCP, and ICMP checks plus API network diagnostics. Assumes familiarity with uptime monitoring concepts; focuses on Checkly-specific patterns and workflows.

## Overview

Checkly extends application monitoring (Playwright browser checks, API checks) down the network stack with DNS, TCP, and ICMP monitors. All check types support monitoring-as-code via the CLI, UI export, Terraform, and the API. Network failures on API checks include pcap and tracert artifacts for root-cause analysis.

## When to Use

- Creating or configuring DNS, TCP, or ICMP uptime checks in Checkly
- Exporting UI-created checks to a Checkly CLI project
- Running or deploying checks with `checkly test` / CI deploy
- Debugging API check network failures (pcap, tracetroute)
- Running network checks inside private networks via private locations
- Choosing repo layout for Checkly check definitions

## Quick Reference

| Situation | First move |
|-----------|------------|
| Monitor DNS resolution or config | DNS check with resolver + assertions — [reference.md — DNS](reference.md#dns-monitoring) |
| Verify TCP port connectivity | TCP check with response assertions — [reference.md — TCP](reference.md#tcp-monitoring) |
| Ping servers / measure packet loss | ICMP check, 10s interval, multi-region — [reference.md — ICMP](reference.md#icmp-ping-monitoring) |
| Move UI check to code | Copy export command from UI → run in CLI project — [reference.md — MaC](reference.md#monitoring-as-code-workflow) |
| Validate checks locally | `npx checkly test` (add `--record` for results) |
| API check network failure | Inspect pcap + tracert; use Rocky — [reference.md — API diagnostics](reference.md#api-check-network-diagnostics) |
| Monitor internal DNS/servers | Private location agents — [reference.md — Private locations](reference.md#private-locations) |
| Terraform instead of CLI | Export check settings to Terraform resource from UI |

## DNS Monitoring

Monitor DNS resolution, custom resolvers, and record correctness. Run from global regions; assert on response content or JSON path expressions for JSON-formatted DNS responses.

→ Full guidance: [reference.md — DNS monitoring](reference.md#dns-monitoring)

```typescript
// Assertion example — response must contain expected record data
assertions: [
  { source: 'RESPONSE_BODY', property: '', comparison: 'CONTAINS', target: '203.0.113.10' },
]
```

## TCP Monitoring

Verify TCP connectivity and response content on any port. Same assertion model as DNS; export to CLI or Terraform like other uptime checks.

→ Full guidance: [reference.md — TCP monitoring](reference.md#tcp-monitoring)

## ICMP (Ping) Monitoring

Ping servers for uptime, packet loss, and latency. Results render as terminal-style output but are JSON — use JSON path assertions for custom thresholds. Supports 10-second frequency and parallel multi-region runs.

→ Full guidance: [reference.md — ICMP monitoring](reference.md#icmp-ping-monitoring)

```typescript
// IPv4 and IPv6 are mutually exclusive — pick one address family per check
// Bad: IPv4 host with IPv6 ping enabled (Checkly blocks this configuration)
```

## Monitoring as Code Workflow

Start in the UI to explore check types, then export to a CLI project for scale. Use `npm create checkly` for boilerplate; import UI checks via the export command (generates an import plan). Validate with `npx checkly test`.

→ Full guidance: [reference.md — Monitoring as Code](reference.md#monitoring-as-code-workflow)

```bash
npm create checkly@latest          # scaffold project
# paste export command from UI     # imports UI check(s) into project
npx checkly test --record          # run locally, view results
```

## API Check Network Diagnostics

When an API check fails due to network errors, Checkly attaches a pcap capture and kicks off a tracert. Use pcap in Wireshark for packet-level analysis; tracert shows hop-by-hop loss to isolate ISP or routing issues. Rocky AI can analyze both artifacts.

→ Full guidance: [reference.md — API diagnostics](reference.md#api-check-network-diagnostics)

## Private Locations

Run browser, API, and (with private location agents) network checks inside your own datacenter or VPC. Required for monitoring on-prem DNS servers, internal load balancers, and VMs without public endpoints.

→ Full guidance: [reference.md — Private locations](reference.md#private-locations)

## Agent Instructions

**When the user wants DNS/TCP/ICMP monitoring:** Identify the target (hostname, IP, port), whether public or private network, and required assertions. For private targets, plan private location agents first. Scaffold with UI or CLI; prefer CLI for multiple checks.

**When the user has UI checks to codify:** Run the export command copied from the Checkly UI inside an existing or new CLI project. Review the import plan, confirm, then `npx checkly test`. Remove unrelated check types from `checkly.config.ts` if the project only needs network monitors.

**When an API check fails with a network error:** Pull the pcap and tracert from the check result. Look for complete connectivity loss at a specific hop (ISP/routing outage) vs application-layer failure. Share tracert in console format for colleagues; use Rocky for automated packet/hop analysis.

**When choosing repo layout:** Default recommendation — colocate checks with the service they monitor (e.g. `checkly/` directory in the app repo), not a central checks-only repo. Resource history in the UI shows whether a check is UI-, CLI-, or Git-driven.

For extended examples, Terraform export, and Rocky debugging patterns, read [reference.md](reference.md).

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| IPv4 host with IPv6 ping enabled | Use one address family per ICMP check — Checkly enforces this |
| `checkly test` runs unwanted Playwright checks | Remove Playwright config from `checkly.config.ts` when testing network-only project |
| No visible test results | Pass `--record` to `checkly test` |
| Monitoring internal DNS/servers from public locations | Deploy private location agents in the target network |
| Assuming API failure is application bug | Check pcap/tracert first — may be ISP or routing outage |
| Discarding UI checks when adopting MaC | Use UI export command; no need to recreate checks manually |
| Case-sensitive assertion mismatch | Match exact casing in response body assertions |

Full list: [reference.md — Detailed Pitfalls](reference.md#detailed-pitfalls)

## Additional Resources

- Detailed subcategory guidance: [reference.md](reference.md)

## Source

Generated from:
- [Network Monitoring as Code](https://www.youtube.com/watch?v=rgAwZo9JiOk) (YouTube) — DNS, TCP, ICMP checks, MaC workflow, API diagnostics, private locations

Subcategories included:
- DNS monitoring: 6:06–8:10
- Monitoring as Code workflow: 8:10–12:00
- TCP monitoring: 12:00–20:16
- ICMP/Ping monitoring: 20:16–24:18
- API check network diagnostics: 24:18–28:22
- Private locations: 28:22–30:23

Excluded:
- Company intro and marketing slides (0:00–4:05)
