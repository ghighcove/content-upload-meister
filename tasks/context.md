# content_upload_meister - Session Context

## Last Updated: 2026-02-17

## Current State

**SEO automation complete for both platforms. Pipeline integration done. TE article GEO-improved and in Medium draft.**

### Recently Published Articles (Cross-Project)

| Article | Platform | Published | Notes |
|---------|----------|-----------|-------|
| Super Bowl Seat article | Unknown | Super Bowl Sunday, Feb 9 2026 | User confirmed published |
| "The 5-12 Seed Upset Is Overrated" | Substack | Feb 17 2026 | Post 188309673 — march_madness project |
| TE Market Inefficiency (NFL) | Medium | In draft (not yet live) | Story 5e631a644b94 — needs SEO + publish |

### Medium SEO (100% automated)
- `medium_seo_setter.py` — JS injection on submission page
  - Sets preview title (100 chars), description (140 chars), topics (up to 5)
  - `build_medium_seo_js()` — builds injectable JS string
  - `build_medium_seo_from_optimizer(story_id, optimizer_result)` — optimizer integration
  - Submission URL: `https://medium.com/p/{story_id}/submission?...`
- Key discoveries from live browser testing:
  - Dropdown options: 3-strategy fallback (span.ao → role=option → listbox li)
  - Must use `input.click()` before `nativeInputSetter` to trigger React
  - Skip topics already added as chips (avoid stale-state failures)
  - Poll for chip count increase rather than fixed wait

### Substack SEO (100% automated)
- `substack_seo_setter.py` — direct REST API (no browser)
  - `set_seo_metadata(draft_id, seo_title, seo_description, slug, tags)`
  - `set_seo_from_optimizer_output(draft_id, optimizer_result)`
  - API fields: `search_engine_title`, `search_engine_description`, `postTags`, `draft_slug`
- Auth fix: bypass `Api.__init__` (cookies_path bug), use `session.cookies.set('substack.sid', token, domain='.substack.com')`

### Medium (85% automated)
- HTML export -> GitHub Pages CDN -> Medium import: working
- Images: CDN pre-upload working
- Tags/SEO: now automated via `medium_seo_setter.py`
- Scheduling: partial (React date picker still unreliable ~30%)

### Substack (content + images + SEO = ~95%)
- Content entry: working
- Image upload: via substack-mcp-plus `upload_image` tool
- SEO metadata: now automated via `substack_seo_setter.py`

### 3D Optimization Engine (Phases 1-6 complete)
- `optimization_engine.py` — 5-strategy optimizer
- `visualizer.py` — 3D Plotly visualization
- Pipeline integration test confirms: optimizer output -> both SEO setters works
- **Known gap**: optimizer requires YAML frontmatter to generate title/description/tags
  - NFL articles use plain markdown headers — optimizer produces garbled output without frontmatter
  - GEO score (75) and voice profile are reliable even without frontmatter
  - Fix needed: add YAML frontmatter to NFL article drafts OR add frontmatter extraction to analyzer

---

## Active Work

### TE Article (NFL) — In Progress

**Story ID**: `5e631a644b94`
**Edit URL**: `https://medium.com/p/5e631a644b94/edit`
**GitHub Pages**: `https://ghighcove.github.io/nfl-salary-analysis/article/te_market_inefficiency_20260217_1255_ff3269c9.html`

**GEO improvements applied (2026-02-17):**
- Attribution updated: Claude Sonnet 4.5 → 4.6
- Finding #3 BLUF fixed: now leads with "7 of top 10 from Rounds 2-3"
- Entity consistency: "Day 2/Day 1" → "Round 2/Round 1" in conclusion

**SEO values to inject (pending):**
- Preview title: `Tight End Market Inefficiency: Why Round 2 TEs Are the NFL Draft's Best-Kept Secret`
- Preview description: `Round 2 NFL TEs deliver +0.582 value vs +0.353 Round 1. 60% bust rate validated across 1,063 player-seasons. Quantitative framework.` (133 chars)
- Topics: NFL Draft · NFL · Data Analysis · Sports Analytics · Football

**Remaining**: Navigate to submission page, inject SEO JS, publish or schedule

### publish-everywhere Skill — Created

- Location: `C:/Users/ghigh/.claude/skills/publish-everywhere/SKILL.md`
- Skill ID visible in system as `publish-everywhere`
- Covers full 4-phase workflow: CDN → Medium import → Medium SEO → Substack SEO

---

## Issues Fixed This Session (Sprint)

1. Dead code removed from `medium_seo_setter.py` (set_medium_seo_via_browser + asyncio import)
2. `span.ao` selector hardened to 3-strategy fallback
3. Schema mismatch fixed: both setter integration functions accept `title`/`description` OR `seo_title`/`seo_description`
4. `SUBSTACK_MCP_PATH` now configurable via env var
5. Medium scheduling JS improved: uses `nativeInputValueSetter`, scans visible inputs, structured JSON return
6. `publish-everywhere` skill created
7. Project `CLAUDE.md` created

---

## Assumptions Checked This Session

| Assumption | Status | Finding |
|-----------|--------|---------|
| GEO 97/100 score was accurate | ❌ Inflated | Real GEO from 3D engine = 75. geo_metadata.py is a simpler estimator |
| 3D optimizer works on NFL articles | ❌ Broken for metadata | Needs YAML frontmatter — NFL articles use plain headers. Voice profile is accurate |
| SEO description 180 chars was fine | ❌ Wrong | Medium JS enforces 140 chars — was being silently truncated. Fixed to 133 chars |
| Day 2/Round 2 terminology consistent | ❌ Inconsistent | Conclusion used "Day 2" while rest used "Round 2" — fixed |
| span.ao selector was stable | ⚠️ Fragile | Minified class, will change on Medium deploys. Now has 3 fallback strategies |

---

## Pending (Next Session)

1. **Finish TE article SEO injection** — open Medium draft, navigate to submission page, inject JS
2. **Publish TE article** — schedule or immediate
3. **Optimizer frontmatter gap** — add YAML frontmatter support to NFL article pipeline so 3D optimizer works properly
4. **Other NFL articles** — Draft ROI, RB Economics, QB Deep Dive — apply same GEO improvements before publishing
5. **march_madness project** — 5-12 upset article published to Substack; check if it needs Medium publish too

---

## Key Design Decisions

### Medium SEO approach
- No public API exists — must use browser automation on submission page
- Submit URL differs from edit URL: `/p/{id}/submission?redirectUrl=...`
- `medium_seo_setter.py` returns {submission_url, js} dict — pipeline navigates + injects
- The JS is stored in `MEDIUM_SEO_JS` constant with `MEDIUM_SEO_CONFIG` placeholder

### Substack SEO approach
- Direct REST API via `python-substack` `put_draft(**kwargs)`
- SEO description: 140 char HARD LIMIT (not 160)
- Tags via `postTags: [{"name": "tag"}]` format

### Adapter pattern
- Adapters prepare/return payloads; orchestrator (pipeline/skill) does browser operations
- `publish_to_medium()` stores `_medium_seo_payload` in `article_data` for pipeline
- `publish_to_substack()` reads `draft_id` from `article_data` or `frontmatter`

### Authentication
- Substack: `SimpleAuthManager.get_token()` decrypts Fernet token from `~/.substack-mcp-plus/auth.json`
- Token expiry: ~2026-03-18 (30 days from 2026-02-17)
- Medium: via logged-in Chrome session

---

## Environment

- Python: Use `C:/Users/ghigh/AppData/Roaming/npm/node_modules/substack-mcp-plus/venv/Scripts/python.exe` for substack tests (needs 3.9+)
- Browser: Chrome with claude-in-chrome extension
- GitHub Pages: https://ghighcove.github.io/content-upload-meister/ (for Medium CDN images)
- Substack token expiry: ~2026-03-18

---

## Quick Reference

- Shared tools: `G:/ai/_shared_tools/publishing/`
  - `medium_seo_setter.py` — Medium SEO via JS injection
  - `substack_seo_setter.py` — Substack SEO via REST API
  - `medium_adapter.py` — Medium workflow adapter
  - `substack_adapter.py` — Substack workflow adapter
  - `optimization_engine.py` — 3D SEO optimizer
- Tests: `G:/ai/content_upload_meister/test_pipeline_integration.py`
- Test draft IDs: Substack=188207668, Medium story=06b801e2ce3b
- Git repos:
  - ai-shared-tools: https://github.com/ghighcove/ai-shared-tools
  - content-upload-meister: https://github.com/ghighcove/content-upload-meister
  - nfl-salary-analysis: https://github.com/ghighcove/nfl-salary-analysis
- Working directory: `G:/ai/content_upload_meister`
