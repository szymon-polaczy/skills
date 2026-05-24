# CSP triage playbook (follow-up only)

**Workers use the 3 verdicts in report-worker-playbook.md** — do not read this file unless master is investigating **required more research** items.

Quick map: `skip` → **skipped** | new origin needed → **added** | already in CSP → **required more research**

---

Full detail below — for master/user follow-up on weird cases only.

## Step 1 — Classify the blocked URI

Extract hostname from `blocked-uri`. Ignore `inline`, `eval`, `data:`, `blob:` for origin checks — handle those separately (usually not allowlisted via URL).

## Step 2 — Is this a URL we actually want?

**Do not allowlist by default.** A CSP block may be working as intended.

### Skip when likely attack or junk

Mark `skip` and document reason when the URI looks like:

| Signal | Example | Typical reason |
|--------|---------|----------------|
| Known malware / skimmer domains | Random CDN strings, `.xyz` typosquats | Attack blocked correctly |
| `javascript:`, `data:`, `vbscript:` in script-src | Inline injection attempt | CSP doing its job |
| Domain unrelated to project stack | Crypto miner pools, paste sites | Not a vendor we use |
| Typosquat of real vendor | `googletagmanger.com` | Impersonation |
| Probe / scanner noise | Single-digit counts, exotic paths, no matching first-party page | Background internet noise |
| Suspicious `source-file` | Unknown third-party script, `about:blank`, missing source on sensitive page | Possible XSS — confirm with user, do not allowlist |

Cross-check against:
- Vendors already integrated (GTM, Marketo, LinkedIn, Adobe, CookieLaw, etc. from code/search)
- `document-uri` — does the blocked load happen on a real site page or a weird URL?
- Whether the project team would plausibly embed this origin

When skipping, **tell the user explicitly** in chat and in `csp.md` → `## Skipped Reports`. Do not silently drop.

### Skip format in `csp.md`

```markdown
[DD.MM.YYYY]
skipped [[issue URL]] — blocked `https://evil.example/miner.js` on script-src: domain unrelated to our stack and matches cryptominer pattern; CSP block is correct, no change needed
```

Set report queue status to `skipped`.

### When uncertain

Ask the user one line: “Report blocks `{uri}` on `{page}` — is this a vendor you use?” Default to **not** adding until confirmed.

---

## Step 3 — Already in CSP? Check redirects first

**If the blocked host (or its obvious parent) is already allowlisted, do not duplicate it.** The violation is almost certainly a **redirect or subdomain variant**.

### Common patterns

| Already allowed | Still blocked | Likely cause |
|-----------------|---------------|--------------|
| `https://www.google.com` | `https://www.google.co.uk` | Geo / locale redirect (country TLD) |
| `https://*.googletagmanager.com` | `https://tagmanager.google.com` | Different Google hostname, not a subdomain match |
| `https://*.linkedin.com` | `https://psx4.linkedin.com` | Internal LB / shard redirect (`psx` → `psx4`) |
| `https://googleads.g.doubleclick.net` | `https://ad.doubleclick.net` | Ad redirect chain |
| `https://cdn.cookielaw.org` | `https://geolocation.onetrust.com` | Vendor uses multiple domains |

**CSP wildcard rules (critical):**
- `*.google.com` matches `foo.google.com` but **not** `google.co.uk` or `www.google.de` (different registrable domain).
- Country-code Google domains need explicit entries or a broader pattern the team accepts (e.g. multiple `https://*.google.*` entries — note `*.google.*` is not valid CSP3 syntax for arbitrary TLDs; often you add `https://*.google.co.uk`, `https://*.google.de`, or vendor-specific hostnames).

### Follow the redirect chain

When parent domain is already allowed, trace where the blocked URL actually goes:

```bash
# Response headers only (see redirect Location)
curl -sI "BLOCKED_URI" | grep -iE '^(HTTP|location:)'

# Final URL after redirects (use for GET-able URLs only)
curl -sL -o /dev/null -w '%{url_effective}\n' "BLOCKED_URI"
```

Compare **initial blocked-uri** vs **final host**. The CSP entry must cover the host that actually loads — often the redirect target, not the first hop.

### Fix for redirect cases

1. Add the **destination host** (minimal), not the source again.
2. Or broaden an existing entry if the vendor rotates subdomains (e.g. `https://*.linkedin.com` already present → add `psx4.linkedin.com` or `https://*.linkedin.com` if not already wildcarded).
3. Document in changelog that the root domain was already allowed and the fix targets redirect/shard behavior:

```markdown
[23.05.2026]
added https://psx4.linkedin.com to connect-src - psx.linkedin.com was already allowed but LinkedIn redirects to psx4 shard; wildcard *.linkedin.com does not cover redirect target hostname mismatch and it will fix this report [[url]]
```

---

## Step 4 — Decide fix type

| Outcome | Action |
|---------|--------|
| Legitimate vendor, not in CSP | Add minimal origin to correct directive |
| Legitimate, parent in CSP | Trace redirect → add destination or adjust wildcard |
| Attack / junk / unwanted | Skip — document in `## Skipped Reports`, inform user |
| Inline / eval violation | Do not add URL — fix code or accept `unsafe-inline` tradeoff (rare, user decision) |

## Step 5 — Grouping with mixed outcomes

- Group **fixes** by same directive + same new origin.
- **Never** group skips with fixes.
- Skipped reports still get individual entries under `## Skipped Reports`.
