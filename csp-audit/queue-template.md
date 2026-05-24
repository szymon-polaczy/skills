# CSP Reports Queue

Pass 1 verdicts: **added** | **skipped** | **required more research**  
Pass 2 re-tags research items: **monitor** | **required more research** (architectural only)

Format: `- [ ] {url} | {directive} | {blocked-uri}`

- [x] https://.../issues/123/ | img-src | px.ads.linkedin.com — **monitor** — *.ads.linkedin.com + *.linkedin.com; redirect report noise
- [x] https://.../issues/456/ | frame-ancestors | www.example.com — **required more research** — framing policy, not outbound allowlist
