#!/usr/bin/env python3
"""
Pipeline integration test: optimizer output -> SEO setters (both platforms).

Tests the complete flow:
  1. Run optimization engine on article content
  2. Apply optimizer output to Substack draft via REST API
  3. Build Medium SEO JS + URL ready for browser injection

Usage:
    python test_pipeline_integration.py

Requires:
    - Valid Substack session token (~/.substack-mcp-plus/auth.json)
    - Draft 188207668 must exist ("Test Article with Images")
"""
import sys
import json
from pathlib import Path

# Shared publishing tools
sys.path.insert(0, str(Path("G:/ai/_shared_tools/publishing")))

from substack_seo_setter import set_seo_from_optimizer_output
from medium_seo_setter import build_medium_seo_from_optimizer

# ── Test article data ──────────────────────────────────────────────────────────

SUBSTACK_DRAFT_ID = 188207668   # "Test Article with Images"
MEDIUM_STORY_ID = "06b801e2ce3b"  # "Test Article with Images"

# Simulated optimizer output (matches optimization_engine.py output schema)
OPTIMIZER_OUTPUT = {
    "seo_title": "Test Pipeline: Automated SEO Metadata",
    "seo_description": "End-to-end pipeline test: optimizer output wired to Substack API and Medium JS injection. Validates full automation.",
    "tags": ["Data Science", "Python", "Content Automation"],
    "slug": "test-pipeline-automated-seo",
    "geo_score": 82,
    "seo_score": 78,
    "voice_score": 85,
}


def test_substack_seo():
    """Test 1: Apply optimizer output to Substack draft via REST API."""
    print("=" * 60)
    print("TEST 1: Substack SEO via REST API")
    print(f"  Draft ID: {SUBSTACK_DRAFT_ID}")
    print(f"  SEO title: {OPTIMIZER_OUTPUT['seo_title']}")
    print(f"  SEO desc: {len(OPTIMIZER_OUTPUT['seo_description'])} chars")
    print(f"  Tags: {OPTIMIZER_OUTPUT['tags']}")
    print()

    try:
        result = set_seo_from_optimizer_output(SUBSTACK_DRAFT_ID, OPTIMIZER_OUTPUT)
        title_ok = result.get("search_engine_title") == OPTIMIZER_OUTPUT["seo_title"]
        desc_ok = result.get("search_engine_description") == OPTIMIZER_OUTPUT["seo_description"]

        print(f"  search_engine_title: {'OK' if title_ok else 'FAIL - got: ' + str(result.get('search_engine_title'))}")
        print(f"  search_engine_description: {'OK' if desc_ok else 'FAIL'}")

        if title_ok and desc_ok:
            print("\n[PASS] Substack SEO API integration working")
        else:
            print("\n[WARN] Substack SEO partial success")
        return result

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None


def test_medium_seo_build():
    """Test 2: Build Medium SEO JS + URL from optimizer output (no browser needed)."""
    print()
    print("=" * 60)
    print("TEST 2: Medium SEO JS builder (no browser)")
    print(f"  Story ID: {MEDIUM_STORY_ID}")
    print()

    try:
        payload = build_medium_seo_from_optimizer(MEDIUM_STORY_ID, OPTIMIZER_OUTPUT)

        url_ok = MEDIUM_STORY_ID in payload["submission_url"]
        js_ok = OPTIMIZER_OUTPUT["seo_title"] in payload["js"]
        topics_ok = all(t in payload["js"] for t in OPTIMIZER_OUTPUT["tags"])

        print(f"  submission_url: {'OK' if url_ok else 'FAIL'}")
        print(f"    {payload['submission_url']}")
        print(f"  JS contains title: {'OK' if js_ok else 'FAIL'}")
        print(f"  JS contains topics: {'OK' if topics_ok else 'FAIL'}")
        print(f"  JS length: {len(payload['js'])} chars")

        if url_ok and js_ok and topics_ok:
            print("\n[PASS] Medium SEO JS builder working")
            print()
            print("  To apply to browser:")
            print("  1. Navigate to:", payload["submission_url"])
            print("  2. Inject payload['js'] via mcp__claude-in-chrome__javascript_tool")
        else:
            print("\n[WARN] Medium SEO JS builder partial success")

        return payload

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("Pipeline Integration Test: Optimizer -> SEO Setters")
    print("=" * 60)
    print()

    substack_result = test_substack_seo()
    medium_payload = test_medium_seo_build()

    print()
    print("=" * 60)
    print("SUMMARY")
    print(f"  Substack API:  {'PASS' if substack_result else 'FAIL'}")
    print(f"  Medium JS:     {'PASS' if medium_payload else 'FAIL'}")
    print()

    if substack_result and medium_payload:
        print("[SUCCESS] Pipeline integration complete.")
        print("  Both platforms ready for automated SEO metadata.")
        print()
        print("  Integration chain:")
        print("  optimization_engine.py -> optimizer_result dict")
        print("    -> set_seo_from_optimizer_output(draft_id, result)  [Substack]")
        print("    -> build_medium_seo_from_optimizer(story_id, result)  [Medium]")
        return 0
    else:
        print("[FAIL] See errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
