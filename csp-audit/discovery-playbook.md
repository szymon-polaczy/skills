# CSP discovery playbook

Find where CSP is defined before changing anything.

## Step 1 — Search codebase (parallel grep)

Run these searches across the repo:

| Pattern | Typical location |
|---------|------------------|
| `contentSecurityPolicy` | Nuxt `@nuxtjs/security`, Next config, Express helmet |
| `Content-Security-Policy` | Server middleware, nginx snippets, meta tags |
| `content-security-policy` | Lowercase header keys in proxies |
| `helmet` + `csp` | Node/Express apps |
| `add_header Content-Security-Policy` | nginx.conf, `.htaccess` |
| `Header set Content-Security-Policy` | Apache |
| `http-equiv="Content-Security-Policy"` | HTML meta (usually secondary) |

Also check:
- `nuxt.config.*`, `next.config.*`, `vite.config.*`
- `server/middleware/`, `server/plugins/`
- Infrastructure: `docker/`, `k8s/`, `terraform/`, `.platform/`, `vercel.json`, `netlify.toml`
- WordPress: security plugins (Sucuri, etc.), `wp-config`, theme `functions.php`

## Step 2 — Identify canonical source

When multiple sources exist, prefer **the one that actually ships to production**:

1. App framework security module (e.g. Nuxt `security.headers.contentSecurityPolicy`)
2. Server/reverse-proxy headers (may override app)
3. Meta tag (often report-only or legacy)

Note all locations in `csp.md` but edit only the canonical one unless user wants infra changes.

## Step 3 — Fetch from production (fallback)

If code search finds nothing or user says prod differs:

```bash
curl -sI "https://PRODUCTION_URL/" | grep -iE 'content-security-policy'
```

Try www and non-www if redirect differs. Check a few key paths (`/`, login, main app route) if CSP varies by route.

Compare header policy to code. If they differ, note both in `csp.md` and ask which is authoritative.

## Step 4 — Normalize for editing

When reading from code (e.g. Nuxt object), flatten to directive → sources list for comparison with GlitchTip violations:

```
script-src: 'self' 'nonce-...' https://cdn.example.com
connect-src: 'self' https://api.example.com
```

Map common frameworks:

| Framework | Edit target |
|-----------|-------------|
| Nuxt + `@nuxtjs/security` | `nuxt.config.*` → `security.headers.contentSecurityPolicy` |
| Next.js | `next.config.js` headers or middleware |
| Express + helmet | `helmet({ contentSecurityPolicy: { directives: {...} } })` |
| nginx | `add_header Content-Security-Policy "..."` |
| WordPress Sucuri | Plugin CSP settings (may be report-only) |

## Step 5 — No CSP found

Set source to `none` in `csp.md`. Build `## Recommended CSP` from:
- Production headers if any partial policy exists
- Else a sensible baseline: `default-src 'self'`, tighten `object-src 'none'`, `base-uri 'self'`, plus origins gathered from GlitchTip reports
