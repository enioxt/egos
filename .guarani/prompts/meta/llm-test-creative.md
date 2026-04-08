---
description: Meta-prompt para teste de modelos LLM - Categoria Creative/Copywriting
trigger: llm.test.creative
---

# LLM Test Suite: Creative Writing & Copywriting

## Objective
Evaluate the model's ability to generate engaging, brand-appropriate, and effective creative content for various use cases.

## Test Structure

### Test 1: Brand Voice Adaptation (Basic)
**Brand Guidelines:**
```
EGOS Brand Voice:
- Technical but accessible
- Confident but not arrogant
- Innovation-focused
- Brazilian heritage with global ambition
- Avoid: buzzwords, hype, overpromising
- Prefer: concrete examples, evidence-based claims
```

**Prompt:**
```
Write a product announcement tweet for EGOS Guard Brasil's new usage-based pricing feature.

Constraints:
- Max 280 characters
- Include one specific benefit
- Match brand voice
- No emojis
- End with clear CTA
```

**Evaluation Criteria:**
- Fits brand voice guidelines
- Meets technical constraints
- Engaging and shareable
- Clear value proposition

### Test 2: Multi-Format Adaptation (Intermediate)
**Source Content:**
```
EGOS Kernel v2.5 Release Notes:
- Added MemPalace integration for persistent memory across sessions
- New CORAL pattern for knowledge reuse between agents
- Improved Hindsight operations (Retain/Recall/Reflect)
- 40% reduction in context token usage
- AAAK compression algorithm for conversation history
```

**Task:**
Adapt this content for 3 different formats:
1. X thread (5 tweets, engaging, technical but accessible)
2. LinkedIn post (professional, business value focused)
3. Developer blog excerpt (technical deep-dive, code examples)

**Evaluation Criteria:**
- Each format matches its platform conventions
- Core message preserved across all
- Appropriate tone for each audience
- Technical accuracy maintained

### Test 3: Headline Generation (Advanced)
**Task:**
Generate 10 headline variations for a blog post about:
```
Topic: How the EGOS framework prevents force-push disasters through multi-layer branch protection

Target audience: Engineering leaders, DevOps practitioners
Goal: Drive clicks and social shares
```

**Constraints:**
- 5 informative/direct headlines
- 3 curiosity-driven headlines
- 2 contrarian/thought-provoking headlines
- All must be accurate (no clickbait that disappoints)

**Evaluation Criteria:**
- Variety of angles covered
- Accurate representation of content
- Engaging without being misleading
- Target audience appropriate

### Test 4: Email Sequence (Advanced)
**Scenario:**
Create a 3-email onboarding sequence for new EGOS users.

**User Journey:**
- Email 1: Immediately after signup (welcome + quick win)
- Email 2: Day 3 (feature deep-dive based on their first action)
- Email 3: Day 7 (community + advanced features)

**Constraints:**
- Each email: 150-250 words
- Personal but professional tone
- Clear single CTA per email
- Progressive disclosure (don't overwhelm)

**Evaluation Criteria:**
- Logical progression across sequence
- Appropriate tone for relationship stage
- Clear CTAs
- Value-driven (not just promotional)

## Scoring Rubric (1-10)

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Brand Alignment | 30% | Matches voice and guidelines |
| Engagement | 25% | Compelling and interesting |
| Technical Accuracy | 20% | Content is correct |
| Format Appropriateness | 15% | Fits platform/audience |
| Creativity | 10% | Fresh angles and ideas |

## Creative Use Cases

| Use Case | Priority | Test Focus |
|----------|----------|------------|
| Social Media | High | Test 1, 2 |
| Documentation | Medium | Test 2 |
| Marketing Copy | High | Test 1, 3 |
| Email Sequences | Medium | Test 4 |
| Blog Content | Medium | Test 2, 3 |

## Output Format

```json
{
  "test_id": "creative-001",
  "model_id": "model-name",
  "overall_score": 8.3,
  "latency_ms": 1800,
  "token_usage": { "prompt": 400, "completion": 900 },
  "test_results": [
    {
      "test": "brand-voice-adaptation",
      "score": 9,
      "passed": true,
      "brand_compliance": "Excellent",
      "engagement_score": 8.5
    },
    {
      "test": "multi-format-adaptation",
      "score": 8,
      "passed": true,
      "platform_fit": {
        "x_thread": 8,
        "linkedin": 8,
        "blog": 8
      }
    }
  ],
  "recommendation": "A-tier for creative tasks"
}
```

## Thresholds

- **S-tier (8.5+)**: Primary for all creative/copywriting
- **A-tier (7.5-8.4)**: Secondary creative tasks
- **B-tier (6.5-7.4)**: Technical writing only
- **C-tier (<6.5)**: Not recommended for creative use

## EGOS Integration

Store results in `llm_models` table with:
- `creative_score`: Overall score
- `brand_adherence`: Compliance with EGOS voice
- `multi_format_capability`: Score on adaptation tests
- Recommended for `TASK_TYPE=content,summary` in fallback chain

## X.com Content Specifics

Additional test for X.com content:
- Hook quality (first line must stop scroll)
- Thread flow (logical progression)
- Engagement triggers (questions, contrarian takes)
- Character optimization
- No em-dash rule compliance (EGOS specific)
