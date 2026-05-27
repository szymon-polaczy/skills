# CSP Audit — {PROJECT_NAME}

> Last updated: {DD.MM.YYYY}

## Configuration

| Field | Value |
|-------|-------|
| **CSP source** | `{file:line}` |
| **Production URL** | `{https://...}` |
| **GlitchTip** | `{https://...}` — CSP-only project/view; scrape this URL as-is (no search-bar filters) |

Queue: **`csp-reports-queue.md`**

### CSP excerpt (for triage)

```
{directive summary}
```

### Vendor CSP references

- Google: https://developers.google.com/tag-platform/security/guides/csp
- Clarity: https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-csp
- OneTrust: https://developer.onetrust.com/onetrust/docs/content-security-policy-cdn
- {others used in Pass 2}

---

## Changelog

### {date} — Pass 1 (initial triage)

{batch adds} — {count} issues

### {date} — Pass 2 (vendor wildcard hardening)

{wildcards added, explicit+wildcard pairs} — aligned with vendor docs; N items → monitor

---

## Skipped

`[[url]]` — {one line}

---

## Monitor post-deploy

{N} issues — **still reporting after last deploy**; Pass 2 investigated each. Outcomes: wildcard/`img-src` fix applied, or documented **redirect / pre-redirect URL / adblock** noise per vendor docs. Not closed as “already covered.” Re-check GlitchTip after next deploy; new hosts in Network tab → new **added** cycle.

---

## Security tradeoffs (review once)

<!-- User accepts or narrows after deploy — do not block audit -->

- `*.linkedin.com` — geo-shard redirects; narrower: verify 302 in DevTools
- {other widened wildcards}

---

## Architectural (no host allowlist fix)

<!-- frame-ancestors, script-src-attr, strict-dynamic — optional user follow-up -->

- `[[url]]` — {one line}
