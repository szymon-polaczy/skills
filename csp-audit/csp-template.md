# CSP Audit — {PROJECT_NAME}

> Last updated: {DD.MM.YYYY}

## Configuration

| Field | Value |
|-------|-------|
| **CSP source** | `{file:line}` |
| **Production URL** | `{https://...}` |
| **GlitchTip** | `{https://...}` |

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

{N} issues — CSP updated or already covered. Residual reports likely **redirect false positives** (browser reports pre-redirect URL). Re-check GlitchTip after prod deploy; no further allowlist work unless new hosts appear in Network tab.

---

## Security tradeoffs (review once)

<!-- User accepts or narrows after deploy — do not block audit -->

- `*.linkedin.com` — geo-shard redirects; narrower: verify 302 in DevTools
- {other widened wildcards}

---

## Architectural (no host allowlist fix)

<!-- frame-ancestors, script-src-attr, strict-dynamic — optional user follow-up -->

- `[[url]]` — {one line}
