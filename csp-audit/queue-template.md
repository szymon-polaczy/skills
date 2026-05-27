# CSP Reports Queue

Pass 1 verdicts: **added** | **skipped** | **required more research** (in-CSP-but-still-reporting → research, never “covered”)  
Pass 2 re-tags research items: **monitor** | **required more research** (architectural only)

**Baseline:** all queue issues are post–last CSP deploy.

Format: `- [ ] {url} | {directive} | {blocked-uri}`

- [x] https://.../issues/100/ | connect-src | https://snap.licdn.com — **required more research** — in CSP excerpt, still reporting post-deploy
- [x] https://.../issues/123/ | img-src | px.ads.linkedin.com — **monitor** — Pass 2: added *.ads.linkedin.com; redirect pre-URL noise per vendor doc
- [x] https://.../issues/456/ | frame-ancestors | www.example.com — **required more research** — framing policy, not outbound allowlist
