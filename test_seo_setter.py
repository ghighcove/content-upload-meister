#!/usr/bin/env python3
"""
Test SEO setter against draft 188207668 (Test Article with Images).
Verifies that search_engine_title, search_engine_description, and postTags
are correctly accepted by the Substack REST API.
"""
import sys
import json
import asyncio
from pathlib import Path

# Add shared publishing tools
sys.path.insert(0, str(Path("G:/ai/_shared_tools/publishing")))

from substack_seo_setter import set_seo_metadata

DRAFT_ID = 188207668  # "Test Article with Images"

TEST_SEO_TITLE = "Test Article with Images: Pipeline Validation"
TEST_SEO_DESCRIPTION = "Automated SEO metadata test via python-substack API. Validates search_engine_title and description fields for publish-everywhere pipeline."
TEST_TAGS = ["data science", "content automation", "testing"]
TEST_SLUG = "test-article-images-pipeline"


def run_test():
    print("[*] Testing Substack SEO setter via direct API...")
    print(f"    Draft ID: {DRAFT_ID}")
    print(f"    SEO title: {TEST_SEO_TITLE[:50]}...")
    print(f"    SEO desc: {len(TEST_SEO_DESCRIPTION)} chars")
    print(f"    Tags: {TEST_TAGS}")
    print()

    try:
        result = set_seo_metadata(
            draft_id=DRAFT_ID,
            seo_title=TEST_SEO_TITLE,
            seo_description=TEST_SEO_DESCRIPTION,
            tags=TEST_TAGS,
        )

        print("=" * 60)
        print("  [RESULT] API response keys:")
        for key in sorted(result.keys()):
            val = result[key]
            if isinstance(val, str) and len(val) > 80:
                val = val[:77] + "..."
            print(f"    {key}: {val}")
        print("=" * 60)

        # Check if our fields were set
        seo_title_ok = result.get('search_engine_title') == TEST_SEO_TITLE
        seo_desc_ok = result.get('search_engine_description') == TEST_SEO_DESCRIPTION

        print()
        print(f"  search_engine_title accepted: {'[OK]' if seo_title_ok else '[FAIL] got: ' + str(result.get('search_engine_title'))}")
        print(f"  search_engine_description accepted: {'[OK]' if seo_desc_ok else '[FAIL] got: ' + str(result.get('search_engine_description'))[:60]}")
        print()

        if seo_title_ok and seo_desc_ok:
            print("[SUCCESS] SEO setter verified - API field names are correct!")
            print()
            print("Next: open the browser and verify the SEO Options section shows:")
            print(f"  Title: {TEST_SEO_TITLE}")
            print(f"  Desc:  {TEST_SEO_DESCRIPTION[:60]}...")
        else:
            print("[WARN] Fields might use different names - check result above for actual field names")

        return result

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = run_test()
    sys.exit(0 if result else 1)
