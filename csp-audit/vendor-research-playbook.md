# Vendor CSP research (Phase 2 — automatic)

Runs **immediately after** Pass 1 CSP edits. **No user prompt** — master researches, applies wildcard hardening, updates `csp.md`, delivers one final handoff.

User may review **Security tradeoffs** at the end; optional follow-up only for **architectural** items.

---

## Input

All queue lines tagged **`required more research`** from Pass 1.

Group by vendor before searching (one search per vendor, not per URL):

| Group | Host signals |
|-------|----------------|
| Google | google-analytics, googletagmanager, doubleclick, googlesyndication, googleadservices, google.com TLD |
| LinkedIn | linkedin.com, licdn.com, ads.linkedin |
| Microsoft/Bing/Clarity | bing.com, bing.net, clarity.ms |
| OneTrust/CookieLaw | cookielaw.org, onetrust.com |
| Adobe | adoberesources, adobedtm, typekit, demdex |
| Dreamdata | dreamdata.cloud |
| Internal | `{production-domain}` from intake |
| Architectural | empty blocked-uri, frame-ancestors, script-src-attr, strict-dynamic |

---

## Step 1 — Web search (batched)

For each vendor group with host-allowlist issues, **one** search:

| Vendor | Search / doc URL |
|--------|------------------|
| Google | [Tag Platform CSP guide](https://developers.google.com/tag-platform/security/guides/csp) |
| LinkedIn | Microsoft Learn conversion tracking + `linkedin insight tag csp` |
| Clarity/Bing | [Clarity CSP](https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-csp) |
| OneTrust | [OneTrust CDN CSP](https://developer.onetrust.com/onetrust/docs/content-security-policy-cdn) |
| Adobe | Experience Platform tags CSP on Experience League |

Extract recommended **wildcard** patterns per directive — prefer vendor docs over guessing.

---

## Step 2 — Apply patterns (second CSP edit)

### Rule A — explicit + wildcard pair

When config already has a concrete host, add the vendor wildcard **on the next line** (same directive):

```javascript
'https://www.google-analytics.com',
'https://*.google-analytics.com',
'https://analytics.google.com',
'https://*.analytics.google.com',
'https://pagead2.googlesyndication.com',
'https://*.googlesyndication.com',
'https://googleads.g.doubleclick.net',
'https://*.g.doubleclick.net',
```

Apply across `script-src`, `connect-src`, `img-src` where that vendor appears — **`img-src` is often the gap** when wildcards exist only in `connect-src`.

### Rule B — prefer `*` over new hardcoded hosts

Pass 1 may have added `www.googleadservices.com` — Pass 2 checks if `*.googlesyndication.com` or vendor wildcard already covers it; **consolidate** toward wildcards when docs recommend.

### Rule C — known redirects (reclassify as monitor, not new host)

Do **not** add a host if research explains report as redirect noise:

| Reported | Likely real failure / note |
|----------|----------------------------|
| `px.ads.linkedin.com` | 302 to `px4.ads.linkedin.com` — fix with `*.ads.linkedin.com` + `*.linkedin.com` |
| `c.clarity.ms` | redirect via `c.bing.com` — ensure `*.clarity.ms` + `*.bing.com` |
| `www.google.de` | already in country TLD allowlist — browser reports pre-redirect URL ([CSP redirect reporting](https://mmazzarolo.com/blog/2021-12-14-lessons-learned-publishing-a-content-security-policy/)) |
| `pagead2.googlesyndication.com` | covered by `*.googlesyndication.com` |

### Rule D — Google country TLDs

**Never** replace a per-TLD country allowlist with a wildcard — Google requires individual TLD entries ([supported_domains](https://www.google.com/supported_domains)). Keep the project's list; reports are often noise.

### Rule E — LinkedIn widening (document tradeoff)

When research items include LinkedIn shards:

```javascript
'https://snap.licdn.com',
'https://*.licdn.com',
'https://*.ads.linkedin.com',
'https://*.linkedin.com',
```

Note in `csp.md` → **Security tradeoffs**: `*.linkedin.com` is broad; narrower alternative is DevTools 302 verification.

### Rule F — Bing / Clarity

```javascript
'https://bat.bing.net',
'https://bat.bing.com',
'https://*.bing.com',
```

Plus existing `*.clarity.ms`.

### Rule G — architectural (no host edit)

Keep **`required more research`** — do not allowlist:

- `frame-ancestors` — framing policy, not outbound load
- `script-src-attr` empty — inline handlers from GTM; needs tag fix or `'unsafe-hashes'`
- `strict-dynamic` / nonce propagation — not a missing domain
- cross-origin `'self'` (`www` vs apex) — may need explicit apex, not wildcard guess

One line each in `csp.md` → **Architectural (no host allowlist fix)**.

---

## Step 3 — Re-tag queue lines

Update Pass 1 **`required more research`** lines:

| After Pass 2 | Meaning |
|--------------|---------|
| **monitor** | Vendor pattern applied or already covered; expect redirect/adblock noise post-deploy |
| **required more research** | Architectural only — user optional follow-up |

Rewrite queue verdict inline — do not leave stale `required more research` on vendor items that got wildcard fixes.

---

## Step 4 — Update `csp.md` (once)

Append:

1. **Changelog** — Pass 2 vendor wildcard hardening (batch, not per URL)
2. **Vendor CSP references** — links used
3. **Monitor post-deploy** — count + one paragraph (redirect false positives)
4. **Security tradeoffs** — bullet per widened wildcard (`*.linkedin.com`, etc.)
5. **Architectural** — items with no host fix

**Do not** ask user to choose between options mid-run. Apply vendor-backed changes; list tradeoffs for review at end.

---

## Step 5 — Final handoff (user sees this only)

Single message:

- Pass 1 counts: added / skipped
- Pass 2: wildcards added, N items → monitor, M architectural
- Files changed
- **Review once:** Security tradeoffs section
- Deploy reminder + optional Tag Assistant check

No "which would you prefer?" — research pass is automatic.
