---
name: roundtable
description: Virtual expert roundtable. Multiple thinkers analyze a document with different frameworks, then synthesize consensus/disagreements/blind spots.
argument-hint: "[file_path] [--experts rumelt,meadows,taleb,grove] [--rounds 1]"
allowed-tools: [Bash, Read, Write, Glob, Grep, Agent]
author: Maki
version: "1.0.0"
tags: [analysis, decision-making, strategy, multi-perspective]
required_env: []
required_bins: []
platforms: [macos, linux, windows]
safety_level: safe
---

# Virtual Expert Roundtable

Analyze a document through multiple analytical frameworks, producing a structured report of consensus, disagreements, blind spots, and emergent insights.

## Architecture: Supervisor + N Agents + Synthesizer

```
Input Document
  │
  ▼
Stage 1: Independent Expert Analysis (parallel)
  ├── Expert A ──→ Structured analysis + confidence score
  ├── Expert B ──→ Structured analysis + confidence score
  ├── Expert C ──→ Structured analysis + confidence score
  └── Expert D ──→ Structured analysis + confidence score
  │
  ▼
Stage 2: Cross-Critique (optional, --rounds N)
  Each expert sees others' conclusions, points out disagreements and self-critiques
  │
  ▼
Stage 3: Roundtable Synthesis (Moderator)
  Claude as Moderator integrates all perspectives
  │
  ▼
Stage 4: Blind Spot Detection + Emergent Insight Extraction
  Dedicated prompts find hidden assumptions and cross-expert inferences
  │
  ▼
Output: Structured Markdown Report
```

## Flow

### Step 0: Parse Input

Read arguments:
- `file_path`: Document to analyze (required, or take from conversation context)
- `--experts`: Expert combination (default `rumelt,meadows,taleb,grove`)
- `--rounds`: Cross-critique rounds (default 0; set 1-2 for deeper but slower analysis)

Read the file. If over 3000 words, auto-summarize to under 3000 words for analysis input.

### Step 1: Independent Expert Analysis

Select experts from the roster (see below), **launch analysis requests in parallel** using Agent subagents.

Each expert's prompt structure:

```
You are {expert_name}, {expert_identity}.
Your analytical framework is: {framework_description}.

Analyze the following document using your framework. Reply in strict JSON:

Document:
---
{document_content}
---

Reply format:
{
  "key_observations": ["Observation 1", "Observation 2", ...],
  "risks_and_concerns": ["Risk 1", "Risk 2", ...],
  "recommendations": ["Recommendation 1", "Recommendation 2", ...],
  "confidence": <1-5 integer, confidence in your analysis>,
  "one_line_verdict": "One-sentence summary judgment"
}
```

### Step 2: Cross-Critique (optional)

If `--rounds >= 1`, run cross-critique:

```
You are {expert_name}. Below are other experts' analyses of the same document:

{other_experts_summaries}

Please:
1. Identify your top 3 disagreements with other experts
2. List where you might be wrong (self-critique)
3. After seeing others' reasoning, update your conclusions and confidence score

Reply JSON:
{
  "top_disagreements": ["Disagreement 1", ...],
  "self_critique": ["Possible error 1", ...],
  "updated_recommendations": ["Updated recommendation 1", ...],
  "updated_confidence": <1-5>
}
```

### Step 3: Roundtable Synthesis (Moderator)

Claude as Moderator, input all experts' final conclusions:

```
You are the roundtable moderator. Below are multiple experts' independent analyses of the same document.

{all_expert_outputs}

Produce a structured synthesis report:

1. **Consensus**: Conclusions all or most experts agree on
2. **Major Disagreements**: Opposing views + each side's arguments
3. **Points of Contention**: Key assumption differences, missing information
4. **Actionable Next Steps**: Specific investigations or decisions needed
5. **Confidence Boost**: Label conclusions where multiple frameworks converge as "high confidence"

For each consensus and disagreement, note which experts support/oppose.
```

### Step 4: Blind Spot Detection + Emergent Insights

**Blind spot detection prompt**:

```
You are a planning blind spot auditor.
Multiple experts have analyzed this document.
Your task is NOT to repeat their views, but to:

1. Find "hidden assumptions" implied but not stated by all experts
2. Find "critical unknowns" not covered by any expert but impactful to the decision
3. Explicitly note: if these blind spots prove false, how would that overturn current conclusions

Original document summary: {document_summary}
Expert conclusions: {all_expert_outputs}

Output:
- "Hidden Assumptions" list: assumption content, which experts imply it, impact if wrong
- "Missing Information" list: what info is needed, why it matters, suggested verification method
- "Risk Ranking": Top 5 blind spots ranked by impact
```

**Emergent insights prompt**:

```
You are a strategy consultant specializing in discovering emergent insights from multiple expert viewpoints.
Given analyses from multiple experts with different backgrounds on the same document:

{all_expert_outputs}

Please:
1. From their "intersection", find conclusions everyone overlooked but multiple pieces of side evidence point to
2. Find inferences that "accepting Expert A's point X AND Expert B's point Y would lead to, but nobody stated"
3. For each emergent insight, explain how it was "assembled" from multiple viewpoints

Output format (per insight):
- Emergent Insight: one-line summary
- Source Combination: Expert A's which point + Expert B's which point
- Reasoning Chain: 1→2→3
- Potential Impact: implications for product/architecture/decision
```

### Step 5: Generate Report

Assemble into final Markdown report, save to `docs/roundtable/YYYYMMDD-{slug}.md`:

```markdown
# Virtual Expert Roundtable Report

- **Date**: YYYY-MM-DD
- **Document**: {file_path}
- **Experts**: {expert_list}
- **Cross-critique rounds**: {rounds}
- **Overall confidence**: {overall_confidence}

## Individual Expert Analyses

### {Expert A Name} ({Framework})
{structured output}

### {Expert B Name} ({Framework})
{structured output}

...

## Roundtable Synthesis

### Consensus
...

### Major Disagreements
...

### Points of Contention
...

## Blind Spot Detection

### Hidden Assumptions
...

### Missing Information
...

### Risk Ranking
...

## Emergent Insights

### Insight 1
...

## Actionable Recommendations

1. ...
2. ...
3. ...

---
*Generated by /roundtable skill*
```

## Expert Roster

### Strategy & Competition

| ID | Expert | Framework | One-line positioning |
|----|--------|-----------|---------------------|
| `rumelt` | Richard Rumelt | Good Strategy Bad Strategy | Does a strategy kernel exist? Is complexity justified? |
| `porter` | Michael Porter | Five Forces / Value Chain | Industry structure, competitive positioning, value chain analysis |
| `christensen` | Clayton Christensen | Innovator's Dilemma | Disruptive innovation risk, low-end market opportunities |
| `blueocean` | W. Chan Kim & Renée Mauborgne | Blue Ocean Strategy | Value innovation, Strategy Canvas, Eliminate-Reduce-Raise-Create |
| `lafley` | A.G. Lafley | Playing to Win | Winning aspiration, where to play, how to win |

### Management & Organization

| ID | Expert | Framework | One-line positioning |
|----|--------|-----------|---------------------|
| `grove` | Andy Grove | High Output Management | Management leverage, output-oriented, OKR |
| `drucker` | Peter Drucker | Management by Objectives | Effectiveness vs efficiency, knowledge worker management |
| `deming` | W. Edwards Deming | Total Quality Management | System variation, continuous improvement, PDCA |
| `goldratt` | Eliyahu Goldratt | Theory of Constraints | Bottleneck identification, maximum system throughput |

### Systems Thinking & Complexity

| ID | Expert | Framework | One-line positioning |
|----|--------|-----------|---------------------|
| `meadows` | Donella Meadows | Thinking in Systems / Leverage Points | System loops, leverage points, paradigm hierarchy |
| `senge` | Peter Senge | The Fifth Discipline | Learning organization, mental models, system archetypes |
| `snowden` | Dave Snowden | Cynefin Framework | Complex vs complicated, probe-sense-respond |

### Risk & Decision Making

| ID | Expert | Framework | One-line positioning |
|----|--------|-----------|---------------------|
| `taleb` | Nassim Taleb | Antifragile / Lindy Effect | Antifragility, black swans, Lindy validation |
| `kahneman` | Daniel Kahneman | Thinking Fast and Slow | Cognitive biases, System 1/2, prospect theory |
| `tetlock` | Philip Tetlock | Superforecasting | Forecast calibration, foxes vs hedgehogs |

### Innovation & Disruption

| ID | Expert | Framework | One-line positioning |
|----|--------|-----------|---------------------|
| `ries` | Eric Ries | Lean Startup | MVP, Build-Measure-Learn, validated learning |
| `thiel` | Peter Thiel | Zero to One | 0→1 vs 1→N, monopoly thinking, secrets |
| `moore` | Geoffrey Moore | Crossing the Chasm | Technology adoption lifecycle, chasm strategy |

### Design & Product

| ID | Expert | Framework | One-line positioning |
|----|--------|-----------|---------------------|
| `norman` | Don Norman | Design of Everyday Things | Usability, mental models, affordance, feedback |
| `cagan` | Marty Cagan | Empowered / Inspired | Product discovery vs delivery, empowered teams |

### Philosophy & Ethics

| ID | Expert | Framework | One-line positioning |
|----|--------|-----------|---------------------|
| `rawls` | John Rawls | Theory of Justice | Justice as fairness, original position, veil of ignorance |
| `harari` | Yuval Noah Harari | Sapiens / Homo Deus | Human history perspective, AI future |

### Quick Presets

| Preset | Expert Combination | Best for |
|--------|-------------------|----------|
| `default` | rumelt, meadows, taleb, grove | General system/architecture review |
| `product` | christensen, ries, norman, thiel | Product decisions |
| `risk` | taleb, kahneman, tetlock, meadows | Risk assessment |
| `strategy` | rumelt, porter, lafley, christensen | Competitive strategy |
| `build` | grove, deming, goldratt, ries | Engineering/build decisions |
| `ethics` | rawls, harari, meadows, snowden | Ethics/governance topics |

Custom example: `/roundtable doc.md --experts "thiel,kahneman,meadows,grove"`

## Notes

- All experts run as Claude subagents in parallel (fastest mode)
- Each expert's prompt is kept under 1000 words (including document summary)
- Documents over 3000 words are auto-summarized
- Report is saved to docs/roundtable/, not auto-committed
