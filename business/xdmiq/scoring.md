# XDMIQ Scoring Methodology

## Overview

XDMIQ (AI-native credentialing) uses preference-based questions to assess user capabilities. Scoring is transparent, explainable, and focused on what users CAN DO rather than credentials.

## Scoring Schema

### Overall Score (0-100)
Aggregate score across all domains, weighted by domain importance.

```
Overall Score = Σ(domain_score × domain_weight)
```

### Domain Scores

Each domain (e.g., Problem Solving, AI Tool Usage) produces:
- **Preference Alignment Score** (0-100): How well user preferences align with capability indicators
- **Reasoning Quality Score** (0-100): Quality of "why" responses (AI-evaluated)
- **Adaptability Score** (0-100): Diversity of preferences across questions
- **Consistency Score** (0-100): Consistency of responses within domain

### Sub-Scores

#### Proficiency Score (0-100)
Technical capability assessment based on:
- Preference patterns that indicate technical depth
- Reasoning quality showing understanding
- Portfolio analysis (if available)

#### Reasoning Score (0-100)
Quality of "why" responses evaluated by:
- Depth of explanation
- Technical accuracy
- Problem-solving insight
- AI evaluation of response quality

#### Adaptability Score (0-100)
Preference diversity indicating:
- Range of approaches user considers
- Flexibility in problem-solving
- Willingness to try different methods

## Scoring Calculation

### Step 1: Preference Answer Scoring
```python
preference_score = sum(option_weight[i] for selected_option) / max_possible_weight
```

### Step 2: Reasoning Answer Scoring
```python
reasoning_score = ai_evaluate_reasoning_quality(reasoning_text)
# Evaluated on: depth, accuracy, insight, technical understanding
```

### Step 3: Question Score
```python
question_score = (preference_score × 0.7) + (reasoning_score × 0.3)
```

### Step 4: Domain Score
```python
domain_score = (
    average_question_scores × 0.4 +      # Preference alignment
    average_reasoning_scores × 0.3 +     # Reasoning quality
    adaptability_score × 0.2 +            # Preference diversity
    consistency_score × 0.1               # Response consistency
)
```

### Step 5: Overall Score
```python
overall_score = sum(domain_score[i] × domain_weight[i] for all domains)
```

## Scoring Weights

### Problem Solving Domain
- Overall weight: 0.25
- Preference alignment: 0.4
- Reasoning quality: 0.3
- Adaptability: 0.2
- Consistency: 0.1

### AI Tool Proficiency Domain
- Overall weight: 0.30
- Preference alignment: 0.4
- Reasoning quality: 0.3
- Adaptability: 0.2
- Consistency: 0.1

### Technical Skills Domain
- Overall weight: 0.25
- Preference alignment: 0.35
- Reasoning quality: 0.25
- Portfolio analysis: 0.3
- Consistency: 0.1

### Collaboration Style Domain
- Overall weight: 0.10
- Preference alignment: 0.5
- Reasoning quality: 0.3
- Adaptability: 0.2

### Learning Approach Domain
- Overall weight: 0.10
- Preference alignment: 0.5
- Reasoning quality: 0.3
- Adaptability: 0.2

## Capability Signals

Each question option maps to capability signals:

```yaml
capability_signals:
  systematic_thinking: [high, medium, high, medium]
  research_skills: [low, high, medium, low]
  iterative_approach: [medium, low, high, low]
```

These signals inform:
- Matching algorithm (capability alignment)
- Capability assessment scoring
- Role suitability evaluation

## Transparency Requirements

- Scoring methodology must be explainable to users
- Users can see how their scores were calculated
- Capability signals are visible (what their preferences indicate)
- No "black box" scoring

## Integration with Matching

XDMIQ scores inform matching algorithm:
- Capability alignment: Match users with roles requiring similar capabilities
- Preference compatibility: Match users with teams/roles that value similar approaches
- Weight: XDMIQ scores contribute 30% to overall match score

## Related Files

- `questions/*.yaml` - Question definitions with scoring weights
- `backend/assessment/xdmiq_assessment.py` - Scoring implementation
- `backend/ai/matching_engine.py` - Matching algorithm integration

