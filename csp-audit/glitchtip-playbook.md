# GlitchTip bulk scrape (master, one browser session)

Goal: fill `csp-reports-queue.md` with **URL + blocked URI + directive** from the **list page only**. No per-issue navigation.

**Triage assumption:** every scraped issue is **post–last CSP deploy** — see [report-worker-playbook.md](report-worker-playbook.md) post-deploy rules.

---

## URL — do not filter in the UI

The user’s issues-list URL is already scoped to **CSP reports only** (dedicated GlitchTip project or saved view). That URL is the full filter.

**Never** use the GlitchTip search bar or `browser_type` to enter Sentry-style queries, for example:

- `is:unresolved Content Security Policy violation`
- `Content Security Policy`
- Any variant that re-filters by CSP text

**Do:** `browser_navigate` to the user URL as-is → scrape rows → paginate.

**Do not:** `curl` GlitchTip API, append `query=` for CSP keywords, or “helpfully” narrow results after load.

---

## Steps

1. `browser_navigate` → **exact** user-provided issues list URL (no search-bar edits) → login gate if form
2. For each page of results:
   - Prefer **`browser_cdp` `Runtime.evaluate`** to dump all rows in one call:

```javascript
(() => {
  const links = [...document.querySelectorAll('a[href*="/issues/"]')];
  const seen = new Set();
  return links.filter(a => {
    const m = a.href.match(/\/issues\/(\d+)/);
    if (!m || seen.has(m[1])) return false;
    seen.add(m[1]);
    const row = a.closest('tr') || a.closest('[class*="issue"]') || a.parentElement?.parentElement;
    const text = (row?.innerText || a.innerText || '').replace(/\s+/g, ' ').trim();
    return true;
  }).map(a => {
    const row = a.closest('tr') || a.closest('[class*="issue"]') || a.parentElement?.parentElement;
    return { url: a.href.split('?')[0], title: (row?.innerText || a.innerText || '').slice(0, 300) };
  });
})()
```

   - If CDP fails → `browser_snapshot` and read rows manually (still on list page only)
   - Parse `title` for blocked URI + directive (GlitchTip/Sentry titles often embed these)
3. `browser_scroll` / click next page → repeat until no new issue IDs
4. Write queue lines ([queue-template.md](queue-template.md)):

```markdown
- [ ] {url} | {directive} | {blocked-uri-or-title-snippet}
```

If directive/URI not parseable from title, use `? | {title snippet}` — batch triage may still decide from title text.

5. `browser_unlock` — **close browser work**; triage is text-only from here

**Never** `browser_navigate` to individual issue URLs during scrape or triage.

---

## Pagination

Track issue IDs seen; stop when a page adds zero new IDs. For 100+ issues expect 2–5 list pages, not 100 issue pages.
