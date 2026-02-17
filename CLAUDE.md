# content_upload_meister

Multi-platform article publishing automation. Publishes from one source to Medium + Substack with full SEO metadata, CDN images, and scheduling.

## Architecture

```
article (.md/.html)
    ↓
optimization_engine.py  →  optimizer_result dict
    ↓                              ↓
medium_adapter.py         substack_adapter.py
    ↓                              ↓
medium_seo_setter.py      substack_seo_setter.py (REST API)
(JS injection, browser)
```

**Shared tools location**: `G:/ai/_shared_tools/publishing/`
**Skill**: `/publish-everywhere` (at `C:/Users/ghigh/.claude/skills/publish-everywhere/`)

## Platform Constraints (HARD RULES)

### Medium
- **No `<table>` tags** — Medium strips them entirely. All tables must be PNG images.
- **GitHub Pages URLs only** for article import (not `raw.githubusercontent.com`)
- **SEO fields**: preview title ≤ 100 chars, description ≤ 140 chars, topics ≤ 5
- **Timestamped HTML filenames** required to bypass Medium's URL caching
- **No public API for SEO** — must use JS injection on submission page (`/p/{id}/submission?...`)
- **Topic selector**: `span.ao` (minified, may change). Three-strategy fallback now in place.

### Substack
- **SEO description: 140 char HARD LIMIT** (not 160 — API rejects longer)
- **REST API auth**: `python-substack` `put_draft()` via stored Fernet token
- **Token location**: `~/.substack-mcp-plus/auth.json` — expires ~30 days from store
- **Token expiry (current)**: ~2026-03-18 — refresh before that date
- **Auth workaround**: bypass `Api.__init__` (cookies_path bug); use `object.__new__(Api)` + `session.cookies.set('substack.sid', token, domain='.substack.com')`

## Key Design Decisions

- **Adapters return payloads; orchestrator does browser ops** — Medium SEO payload returned as `{submission_url, js}` dict; pipeline navigates + injects.
- **optimizer_result schema**: engine returns `title`/`description`; setters accept both `seo_title`/`seo_description` AND `title`/`description` as fallback.
- **Substack MCP path**: configurable via `SUBSTACK_MCP_PATH` env var (default: `C:/Users/ghigh/AppData/Roaming/npm/node_modules/substack-mcp-plus`).

## Python Environment

For Substack scripts, use the venv Python (needs 3.9+):
```
C:/Users/ghigh/AppData/Roaming/npm/node_modules/substack-mcp-plus/venv/Scripts/python.exe
```

## Test IDs

- Substack draft: `188207668` ("Test Article with Images")
- Medium story: `06b801e2ce3b` ("Test Article with Images")

## What NOT To Do

- Do NOT use `raw.githubusercontent.com` URLs for Medium import (serves `text/plain`)
- Do NOT paste `<table>` HTML into articles — always convert to PNG first
- Do NOT include local file paths in articles (`G:/ai/...`, `C:/Users/...`)
- Do NOT set SEO description > 140 chars for Substack (will fail silently or error)
- Do NOT retry Medium scheduling more than once if it fails — flag for manual fix
