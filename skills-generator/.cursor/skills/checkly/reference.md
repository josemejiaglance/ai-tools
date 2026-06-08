# Checkly — Reference

Deep-dive material for Checkly network monitoring as code. Read when SKILL.md routing is not enough.

## DNS Monitoring

Monitor DNS resolution, record correctness, and resolver behavior from global Checkly locations.

### When to apply

- Verify authoritative or public DNS records for your domain
- Compare resolution across resolvers (e.g., Google 8.8.8.8 vs Cloudflare 1.1.1.1)
- Monitor on-prem DNS fleet configuration consistency
- Catch DNS-layer issues before they bubble to application checks

### Configuration options

| Option | Purpose |
|--------|---------|
| Hostname / query | Domain or record to resolve |
| Resolver | Override default resolver (test specific DNS providers) |
| Protocol | DNS (default) or TCP |
| Regions | Run from specific global locations (e.g., Montreal, US East) |
| Assertions | Match response body content, status, or JSON path |

### Assertions

Standard text assertions verify the response contains expected record data:

```typescript
assertions: [
  {
    source: 'RESPONSE_BODY',
    property: '',
    comparison: 'CONTAINS',
    target: '203.0.113.10',
  },
],
```

For JSON-formatted DNS responses, use JSON path expressions to assert on structured fields — same assertion engine as other Checkly check types.

### Step-by-step

1. Create a DNS check in the UI or define in a CLI project
2. Set hostname and optional custom resolver
3. Pick one or more monitoring regions
4. Add assertions on expected A/AAAA/CNAME values
5. Run once manually to inspect raw DNS response (IP list, errors)
6. Export to CLI if part of a larger monitoring-as-code setup

### Edge cases

| Case | Approach |
|------|----------|
| Multiple resolvers to compare | Create separate checks, one per resolver |
| JSON DNS responses | Use JSON path assertions instead of plain CONTAINS |
| Internal DNS servers | Use private locations (see below) |

## TCP Monitoring

Verify TCP connectivity and response content on arbitrary ports — load balancers, databases, custom services without HTTP endpoints.

### When to apply

- Port is open and accepting connections
- Service returns identifiable content on connect (banner, handshake response)
- HTTP/API checks are not applicable (no REST endpoint)

### Configuration

Same regional and assertion model as DNS checks. Assertions validate response body content after TCP connection — useful for catching misconfigured services or unexpected banners.

### Step-by-step

1. Specify host and port
2. Select monitoring regions
3. Add assertions on expected response content
4. Run manually to inspect connection result
5. Export to CLI or Terraform as needed

### Export paths

- **CLI:** Copy export command from UI → run in Checkly CLI project (same import plan flow as DNS)
- **Terraform:** UI provides a Terraform resource block — copy into your IaC repo (less polished than CLI export but functional)

## ICMP (Ping) Monitoring

Ping-based uptime monitoring with packet loss, latency metrics, and JSON-path assertions.

### When to apply

- VM, server, or appliance uptime (no HTTP endpoint)
- Packet loss or latency degradation detection
- Multi-region availability for servers that should respond globally

### Key configuration

| Setting | Detail |
|---------|--------|
| Frequency | As low as every 10 seconds |
| Regions | Run in parallel across multiple regions |
| IPv4 vs IPv6 | Mutually exclusive — Checkly prevents mixing address families on one check |
| Assertions | JSON path on underlying JSON response (packet loss %, latency, etc.) |

### Results format

The results page renders terminal-style ping output for familiarity, but the underlying data is JSON. Pull metrics via API for downstream alerting or dashboards.

### Step-by-step

1. Create ICMP check with target IP (v4 or v6, not both)
2. Set frequency (10s for critical servers)
3. Enable parallel multi-region if cross-region availability matters
4. Run manually — inspect packet loss % and latency
5. Add JSON path assertions if automated thresholds needed (e.g., packet loss > 5%)
6. Bulk-test fleet: define multiple ICMP checks in CLI project, run `npx checkly test`

### Edge cases

| Case | Approach |
|------|----------|
| Server drops some pings intermittently | Assert on packet loss threshold, not just reachability |
| IPv6-only host | Create separate check with IPv6; do not reuse IPv4 check |
| Demo / staging servers with artificial loss | Useful for validating assertion thresholds before production |

## Monitoring as Code Workflow

Checkly is headless-first — UI for exploration, CLI for scale and CI/CD.

### Project setup

```bash
npm create checkly@latest
cd <project>
npx checkly login
```

The scaffold creates a default project with sample checks. Delete unused check files and strip Playwright config from `checkly.config.ts` when working network-only.

### UI → CLI export

1. Create and configure a check in the Checkly UI
2. Open the check's export menu → copy the CLI export command
3. Run the command inside your CLI project
4. Review the import plan (works for bulk UI imports — 20–30+ checks)
5. Confirm import — check definition appears as code in the project
6. Validate: `npx checkly test --record`

The `--record` flag is required to view detailed run results locally.

### CI/CD integration

Checks driven from Git show in the UI **resource history**: last modified time, branch, and repository. UI-created checks display a distinct icon. Typical flow: PR merge → Checkly deploy in CI → production monitors updated.

### Repo layout

**Recommended:** Colocate checks with the service they monitor (e.g., `checkly/` in the app repo). Avoid a central checks-only repository unless organizational policy requires it. The CLI defaults to a `checkly/` directory.

### Rocky AI agent

Checkly's Rocky coding agent can debug failing checks — paste failure context and it analyzes response data. Most useful for subtle assertion mismatches; obvious failures (case sensitivity, wrong expected value) are detected automatically. Rocky also reads pcap and tracert artifacts on API network failures.

### Terraform export

From the UI, copy a check's settings as a Terraform resource block. Paste into your IaC repo. CLI export is smoother for day-to-day workflows; Terraform suits teams already managing infra as code.

## API Check Network Diagnostics

Enhanced debugging when API checks fail due to network errors (not application logic).

### Artifacts on network failure

| Artifact | Purpose |
|----------|---------|
| **pcap capture** | Full packet trace — open in Wireshark for packet-level analysis |
| **Traceroute** | Hop-by-hop path; identify where connectivity drops |

Both artifacts are available in the check result UI. Tracert also downloads in traditional console format for sharing.

### Diagnosis workflow

1. API check fails with network error (not 4xx/5xx from app)
2. Open check result → inspect tracert table
3. Look for complete loss after a specific hop → likely ISP or routing outage
4. Cross-reference timing with external status (e.g., ISP outage radar)
5. For deeper analysis, download pcap → Wireshark
6. Use Rocky to summarize suspicious packets or hop failures

### Example pattern

Tracert shows connectivity for 2 hops, then 100% loss at hop 3 onward. Timing coincides with a known ISP outage between Cloudflare and the target ISP. Root cause is network infrastructure, not the application — no code deploy needed.

### Rocky on network artifacts

Rocky reads pcap files and tracert output to flag anomalies at the packet or hop level. Useful when manual Wireshark analysis is slow or the team lacks network tooling locally.

## Private Locations

Run checks inside your own network instead of Checkly's public locations.

### When to apply

- On-prem DNS servers, internal load balancers, VMs without public IPs
- Compliance requirements preventing external probing
- Network monitors targeting RFC1918 address space

### Supported check types

Browser (Playwright), API, and Playwright check suites run on private location agents today. Network monitors (DNS, TCP, ICMP) require private location agent support — deploy agents in the target VPC/datacenter, then assign checks to that private location.

### Setup pattern

1. Deploy a private location agent in the target network
2. Register the location in Checkly
3. Create DNS/TCP/ICMP/API checks assigned to that private location
4. Run and deploy via CLI same as public-location checks

## Extended Examples

### Example: DNS resolver comparison

**Context:** Verify your domain resolves correctly via both Google and Cloudflare public resolvers.

**Approach:** Two DNS checks, same hostname, different resolver settings, same assertions. Run from the same region to isolate resolver differences.

### Example: Fleet ICMP sweep

**Context:** 50 internal servers need uptime monitoring without HTTP endpoints.

**Approach:**

```bash
# checkly/ directory with one ICMP check file per server
npx checkly test --record   # ping entire fleet locally before deploy
```

Set 10-second frequency and JSON path assertion on `packetLoss` for critical servers.

### Example: API failure triage

**Context:** Production API check fails intermittently; team suspects network issue.

**Approach:**
1. Open failing result → tracert shows loss starting at hop 4 (ISP boundary)
2. Download pcap → confirm TCP handshake never completes
3. Share console-format tracert with network team
4. No application rollback — wait for ISP resolution

## Detailed Pitfalls

| Pitfall | Why it fails | Fix |
|---------|--------------|-----|
| IPv4 + IPv6 on one ICMP check | Invalid ping configuration | Separate checks per address family |
| Playwright config in network-only project | `checkly test` runs browser checks unexpectedly | Remove Playwright from `checkly.config.ts` |
| Missing `--record` flag | Local test runs but no visible results | Always pass `--record` during development |
| Public location for RFC1918 target | Check cannot reach private IP | Use private location agents |
| Case-sensitive assertion | `"OK"` vs `"ok"` fails TCP/DNS body match | Match exact response casing |
| Ignoring tracert on API failure | Team debugs application code for network outage | Check network artifacts first |
| Recreating UI checks manually | Wasted effort, drift risk | Use UI export command |
| Central checks repo far from service | Harder to correlate monitor changes with app changes | Colocate in service repo |

## Source Detail

From: [Network Monitoring as Code](https://www.youtube.com/watch?v=rgAwZo9JiOk) (YouTube)

Timestamps for sections in this file:
- DNS monitoring: 6:06–8:10
- Monitoring as Code workflow: 8:10–12:00
- TCP monitoring: 12:00–20:16
- ICMP/Ping monitoring: 20:16–24:18
- API check network diagnostics: 24:18–28:22
- Private locations: 28:22–30:23
