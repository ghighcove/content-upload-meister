# SEO Automation Architecture

**Goal**: Intelligent, content-aware SEO metadata generation for Medium + Substack

---

## 📊 SEO Fields Mapping

### Medium SEO Capabilities

| Field | Location | Automation Method | Priority |
|-------|----------|------------------|----------|
| **Tags** | Story settings | Browser automation (click, type, enter) | HIGH |
| **Custom URL slug** | Story settings | Browser automation | MEDIUM |
| **Meta description** | Story settings (optional) | Browser automation | MEDIUM |
| **Publication** | Story settings | Browser automation | LOW |
| **Canonical URL** | Story settings | Browser automation | LOW |

**Current Status**: ❌ Not automated
**Blocker**: None - just needs implementation

### Substack SEO Capabilities

| Field | Location | Automation Method | Priority |
|-------|----------|------------------|----------|
| **SEO Title** | Settings panel | Browser automation | HIGH |
| **SEO Description** | Settings panel (140 char limit) | Browser automation | HIGH |
| **Tags** | Post editor | Browser automation or API | HIGH |
| **Category/Section** | Post editor | substack-mcp-plus (`get_sections`) | MEDIUM |
| **Custom URL slug** | Post settings | Browser automation | MEDIUM |
| **Subtitle** | Post editor | substack-mcp-plus (already working) | HIGH |

**Current Status**: ⚠️ Subtitle working, rest not automated
**Blocker**: Need to explore Settings panel UI

---

## 🧠 Intelligent SEO Generation System

### Content Analyzer

**Input**: Article markdown + YAML frontmatter
**Output**: Optimized SEO metadata for each platform

**Analysis steps:**
1. **Topic extraction**: Identify main themes, keywords
2. **Entity recognition**: People, places, technologies mentioned
3. **Sentiment analysis**: Tone (analytical, opinion, news, etc.)
4. **Reading level**: Target audience sophistication
5. **Content type**: Tutorial, analysis, news, opinion, research

**Output schema:**
```yaml
seo_metadata:
  # Core metadata (platform-agnostic)
  primary_topic: "March Madness Predictions"
  secondary_topics: ["NCAA Basketball", "Data Science", "Sports Analytics"]
  keywords: ["bracket", "upset prediction", "Elo ratings", "statistical modeling"]
  entities: ["NCAA", "Sweet Sixteen", "Cinderella teams"]
  content_type: "research_analysis"
  target_audience: "data-literate sports fans"

  # Generated SEO (platform-specific)
  medium:
    tags: ["March Madness", "Data Science", "NCAA Basketball", "Sports Analytics", "Machine Learning"]
    description: "Statistical modeling achieves 70% bracket accuracy using Elo ratings and efficiency metrics"
    custom_slug: "march-madness-upset-prediction-model-2026"

  substack:
    seo_title: "Cinderella Index: Predicting March Madness Upsets | Data-Driven Brackets"
    seo_description: "Statistical modeling achieves 70% bracket accuracy: Elo ratings, efficiency metrics, upset prediction methodology, 10-year validation"  # 140 char
    tags: ["March Madness", "NCAA", "Analytics"]  # Substack limits to 3-5
    section: "Sports Analytics"  # Must match existing section
```

### SEO Rules Engine

**Platform-specific constraints:**

**Medium:**
- **Tags**: Max 5, must be existing tags (Medium suggests)
- **Description**: Optional, ~150-160 chars
- **Slug**: Auto-generated from title, can customize
- **Tone**: Professional but accessible

**Substack:**
- **SEO Title**: 60-70 chars max (Google cutoff)
- **SEO Description**: **EXACTLY 140 chars** (hard limit)
- **Balance**: 50% SEO keywords + 50% GEO depth signals
- **Tags**: 3-5 max, existing tags preferred
- **Tone**: Signals intellectual rigor (per CLAUDE.md rules)

**GEO Principles** (both platforms):
- Signal depth: "statistical modeling", "quantitative framework", "methodology"
- Avoid clickbait: "You won't believe...", "Shocking..."
- Be specific: "70% accuracy" not "high accuracy"
- Include validation: "10-year backtest", "peer-reviewed"

---

## 🏗️ Architecture

### Component 1: Content Analyzer
**File**: `G:/ai/_shared_tools/publishing/seo_analyzer.py`

```python
def analyze_article(article_path: str) -> dict:
    """
    Analyze article and extract SEO-relevant metadata

    Returns:
        {
            'topics': ['Machine Learning', 'Sports'],
            'keywords': ['prediction', 'model', 'accuracy'],
            'entities': ['NCAA', 'March Madness'],
            'content_type': 'research',
            'reading_level': 'college',
            'word_count': 3500
        }
    """
```

### Component 2: SEO Generator
**File**: `G:/ai/_shared_tools/publishing/seo_generator.py`

```python
def generate_seo_metadata(article_analysis: dict, platform: str) -> dict:
    """
    Generate platform-optimized SEO metadata

    Args:
        article_analysis: Output from analyze_article()
        platform: 'medium' or 'substack'

    Returns:
        Platform-specific SEO metadata dict
    """
```

### Component 3: SEO Validator
**File**: `G:/ai/_shared_tools/publishing/seo_validator.py`

```python
def validate_seo_metadata(metadata: dict, platform: str) -> tuple[bool, list[str]]:
    """
    Validate SEO metadata against platform constraints

    Returns:
        (is_valid, [list of warnings/errors])
    """
```

### Component 4: Browser Automation
**Files**:
- `medium_seo_automation.py` - Medium-specific SEO field filling
- `substack_seo_automation.py` - Substack-specific SEO field filling

---

## 🎯 Content Strategy Integration

### YAML Frontmatter Template

```yaml
---
title: "The Cinderella Index: Predicting March Madness Upsets"
subtitle: "How 40 years of NCAA data reveals predictable patterns"

# Content classification
content_type: research_analysis  # research_analysis, tutorial, opinion, news
category: Sports Analytics
tags:
  - March Madness
  - Data Science
  - NCAA Basketball
  - Predictive Modeling

# SEO metadata (can be auto-generated if omitted)
seo:
  # Shared metadata
  primary_keywords: ["March Madness", "upset prediction", "bracket accuracy"]
  target_audience: "data-literate sports fans"

  # Medium-specific (optional, auto-generated if omitted)
  medium:
    tags: ["March Madness", "Data Science", "NCAA Basketball", "Sports Analytics", "Machine Learning"]
    description: "Statistical modeling achieves 70% bracket accuracy using Elo ratings and efficiency metrics"
    custom_slug: null  # Auto-generate from title

  # Substack-specific (optional, auto-generated if omitted)
  substack:
    meta_title: "Cinderella Index: Predicting March Madness Upsets | Data Science"
    meta_description: "Statistical modeling achieves 70% accuracy: Elo ratings, efficiency metrics, upset prediction, 10-year validation"
    section: "Sports Analytics"  # Must match existing section

# Publishing config
draft: false
schedule: null  # or ISO datetime
platforms:
  - medium
  - substack
---
```

### Auto-generation Workflow

```python
# 1. Parse frontmatter
metadata = parse_yaml_frontmatter(article_path)

# 2. If SEO metadata missing, generate it
if not metadata.get('seo'):
    analysis = analyze_article(article_path)
    metadata['seo'] = {
        'medium': generate_seo_metadata(analysis, 'medium'),
        'substack': generate_seo_metadata(analysis, 'substack')
    }

# 3. Validate generated metadata
is_valid, errors = validate_seo_metadata(metadata['seo']['medium'], 'medium')
if not is_valid:
    warn_user(errors)

# 4. Apply to platforms during publishing
for platform in metadata['platforms']:
    apply_seo_metadata(platform, metadata['seo'][platform])
```

---

## 🔄 Integration with Publish-Everywhere Workflow

### Updated Phase 3: Platform Publishing

```python
# Phase 3A: Publish to Medium
if 'medium' in platforms:
    # Import article (already working)
    article_url = import_to_medium(html_url)

    # NEW: Apply SEO metadata
    apply_medium_seo(
        article_url=article_url,
        tags=metadata['seo']['medium']['tags'],
        description=metadata['seo']['medium'].get('description'),
        custom_slug=metadata['seo']['medium'].get('custom_slug')
    )

# Phase 3B: Publish to Substack
if 'substack' in platforms:
    # Create draft with substack-mcp-plus (already working)
    post_id = create_substack_draft(
        title=metadata['title'],
        subtitle=metadata['subtitle'],
        content=markdown_content,
        images=[...] # Upload images (already working)
    )

    # NEW: Apply SEO metadata
    apply_substack_seo(
        post_id=post_id,
        meta_title=metadata['seo']['substack']['meta_title'],
        meta_description=metadata['seo']['substack']['meta_description'],
        tags=metadata['seo']['substack']['tags'],
        section=metadata['seo']['substack'].get('section')
    )
```

---

## 📋 Implementation Checklist

### Phase 1: Foundation (2-3 hours)
- [ ] Create `seo_analyzer.py` - Content analysis
- [ ] Create `seo_generator.py` - Platform-optimized metadata generation
- [ ] Create `seo_validator.py` - Constraint validation
- [ ] Update YAML frontmatter template
- [ ] Test with existing articles

### Phase 2: Medium SEO Automation (2-3 hours)
- [ ] Explore Medium story settings panel (browser automation)
- [ ] Implement tag addition (find field, type, enter)
- [ ] Implement description field (find, clear, type)
- [ ] Implement custom slug (find, clear, type)
- [ ] Test with test article
- [ ] Integrate into publish workflow

### Phase 3: Substack SEO Automation (3-4 hours)
- [ ] Explore Substack Settings panel (screenshot, document fields)
- [ ] Implement meta title field (find, clear, type)
- [ ] Implement meta description field (find, clear, type, validate 140 char)
- [ ] Implement tag addition (find, type, enter)
- [ ] Implement section selection (find, click, select)
- [ ] Test with test article
- [ ] Integrate into publish workflow

### Phase 4: Integration & Testing (2 hours)
- [ ] Update `main.py` workflow orchestrator
- [ ] Test auto-generation with 3 article types
- [ ] Test manual override (user-provided SEO)
- [ ] Verify GEO+SEO balance in Substack descriptions
- [ ] Document workflow for production use

**Total estimated time**: 9-12 hours

---

## 🎯 Success Criteria

1. **Automation**: SEO metadata applied to both platforms without manual input
2. **Intelligence**: Generated metadata is contextually relevant (not generic)
3. **GEO compliance**: Substack descriptions signal depth (50% GEO / 50% SEO)
4. **Validation**: Catches platform constraint violations before publishing
5. **Flexibility**: Supports manual override via YAML frontmatter
6. **Integration**: Seamless part of existing publish-everywhere workflow

---

## 🔮 Future Enhancements

- **A/B testing**: Track which SEO strategies perform best
- **Keyword research**: Integrate Google Trends, SEMrush APIs
- **Competitor analysis**: Analyze top-performing articles in niche
- **Auto-tagging**: ML-based tag suggestion from historical performance
- **SEO scoring**: Pre-publish score (1-100) with improvement suggestions
