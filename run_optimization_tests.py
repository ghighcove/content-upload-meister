#!/usr/bin/env python3
"""
Phase 4: Run 30-case optimization test matrix and generate 3D visualization
3 articles x 5 strategies x 2 platforms = 30 test cases
"""
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add shared tools to path
sys.path.insert(0, 'G:/ai/_shared_tools/publishing')

from multi_dim_analyzer import MultiDimAnalyzer
from optimization_engine import OptimizationEngine
from visualizer import OptimizationVisualizer


# =====================================================================
# TEST ARTICLES - Update these paths to your real articles
# =====================================================================
TEST_ARTICLES = {
    'Research Analysis': {
        'path': 'G:/ai/content_upload_meister/test/article/test_with_images.md',
        'type': 'research_analysis',
        'description': 'Data-heavy analytical content'
    }
    # Phase 6: Add 2 more article types here once implemented
    # 'Tutorial HowTo': {'path': '...', 'type': 'tutorial'},
    # 'Opinion Commentary': {'path': '...', 'type': 'opinion'}
}

PLATFORMS = ['substack', 'medium']


def run_test_matrix():
    """Run full 3D optimization test matrix"""
    print("=" * 70)
    print("  3D CONTENT OPTIMIZATION TEST MATRIX")
    print("=" * 70)
    print(f"  Articles: {len(TEST_ARTICLES)}")
    print(f"  Platforms: {len(PLATFORMS)}")
    print(f"  Strategies: 5")
    print(f"  Total test cases: {len(TEST_ARTICLES) * len(PLATFORMS) * 5}")
    print("=" * 70)
    print()

    analyzer = MultiDimAnalyzer()
    visualizer = OptimizationVisualizer()

    all_results = {}   # {article_name: {platform: {strategy: result}}}
    summary_data = []

    for article_name, article_info in TEST_ARTICLES.items():
        article_path = article_info['path']
        all_results[article_name] = {}

        print(f"[*] Analyzing: {article_name}")
        print(f"    Path: {article_path}")

        # Analyze article
        try:
            analysis = analyzer.analyze_content_3d(article_path)
        except Exception as e:
            print(f"    [ERROR] Could not analyze: {e}")
            continue

        seo_score = analysis['traditional_seo']['score']
        voice = analysis['voice_profile']

        print(f"    Traditional SEO: {seo_score}/100 ({analysis['traditional_seo']['grade']})")
        print(f"    Voice: Formality {voice['formality']}/5, Data-heaviness {voice['data_heaviness']}/5")
        print()

        # Run optimization for each platform
        engine = OptimizationEngine(voice_profile=voice)

        for platform in PLATFORMS:
            all_results[article_name][platform] = {}
            print(f"  [{platform.upper()}]")

            # Run all 5 strategies
            strategy_results = engine.optimize_all_strategies(analysis, platform)

            for strategy, result in strategy_results.items():
                all_results[article_name][platform][strategy] = result
                s = result['scores']

                print(f"    {strategy:20s} SEO:{s['seo']:3d} GEO:{s['geo']:3d} Plat:{s['platform_fit']:3d} Combined:{s['combined']:3d}")

                summary_data.append({
                    'article': article_name,
                    'article_type': article_info['type'],
                    'platform': platform,
                    'strategy': strategy,
                    'seo_score': s['seo'],
                    'geo_score': s['geo'],
                    'platform_fit': s['platform_fit'],
                    'voice_distance': s['voice_distance'],
                    'combined_score': s['combined'],
                    'description': result['description'],
                    'tags': result['tags']
                })

            print()

    # Save results JSON
    results_path = f"G:/ai/content_upload_meister/test/optimization_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump({
            'generated': datetime.now().isoformat(),
            'test_cases': len(summary_data),
            'articles': list(TEST_ARTICLES.keys()),
            'results': all_results,
            'summary': summary_data
        }, f, indent=2, default=str)

    print(f"[OK] Results saved: {results_path}")

    # Generate 3D visualization
    print()
    print("[*] Generating 3D visualization...")
    viz_path = visualizer.create_3d_plot(all_results)
    print(f"[OK] Visualization saved: {viz_path}")
    print()

    # Print summary table
    print("=" * 70)
    print("  SUMMARY: Best Strategy Per Article x Platform")
    print("=" * 70)
    print(f"  {'Article':25s} {'Platform':10s} {'Best Strategy':22s} {'SEO':5s} {'GEO':5s} {'Comb':5s}")
    print("-" * 70)

    seen = set()
    for article_name, platforms in all_results.items():
        for platform, strategies in platforms.items():
            if not strategies:
                continue
            best_strategy = max(strategies.keys(), key=lambda s: strategies[s]['scores']['combined'])
            best = strategies[best_strategy]
            s = best['scores']
            key = (article_name, platform)
            if key not in seen:
                seen.add(key)
                print(f"  {article_name:25s} {platform:10s} {best_strategy:22s} {s['seo']:5d} {s['geo']:5d} {s['combined']:5d}")

    print("=" * 70)
    print()
    print("[SUCCESS] Phase 4 test matrix complete!")
    print()
    print(f"  Open in browser: {viz_path}")

    return all_results, viz_path


if __name__ == "__main__":
    all_results, viz_path = run_test_matrix()
