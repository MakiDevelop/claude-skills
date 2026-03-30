---
name: vendor-eval
description: Vendor proposal evaluation. Analyze technical architecture, pricing, and market benchmarks from a proposal PDF/Doc. Output evaluation report + comparison.
argument-hint: "[PDF/Doc file path] [--scope 'OCR only'] [--exclude-competitor 'CompanyX']"
allowed-tools: Read, Bash, Write, Glob, Grep, WebSearch, Agent
author: Maki
version: "1.0.0"
tags: [business, procurement, vendor, evaluation, analysis]
required_env: []
required_bins: []
platforms: [macos, linux, windows]
safety_level: safe
---

# /vendor-eval — Vendor Proposal Evaluation

Read a vendor proposal document and produce a comprehensive evaluation report with negotiation toolkit.

## Output

1. **Markdown report** — Full evaluation (tech analysis + pricing breakdown + risk matrix + negotiation strategy)
2. **Comparison table** — Alternative solutions + PoC acceptance criteria + negotiation priorities

## Not Applicable When

- Vendor gave only a verbal quote, no written proposal → ask for written document first
- Pure price comparison with no technical content → just use a spreadsheet
- Involves confidential internal pricing strategy → handle offline

## Input

From `$ARGUMENTS` or conversation:

| Field | Required | Description |
|-------|----------|-------------|
| Proposal file | Yes | PDF path, or document URL |
| Evaluation scope | No | Default: all. Can limit to e.g., "OCR module only" |
| Excluded competitors | No | e.g., "CompanyX is our competitor, don't mention in report" |
| Audience / purpose | No | Affects report tone, e.g., "for exec negotiation" vs "internal tech review" |
| Industry context | No | Client's industry, size, IT maturity (helps judge solution fit) |

If missing the proposal file, ask user.

## Decision Model

### Phase 0: Read Proposal (Pre-flight)

1. **Identify file type**:
   - Local PDF → `Read` tool
   - URL → `WebFetch` to download then read

2. **Extract key info**, build a proposal summary card:

```
## Proposal Summary Card
- Vendor name: {name or "not specified"}
- Client: {client name}
- Module count: {N}
- Modules and pricing: {list}
- First-year total: {amount}
- Usage limits and overage fees: {list}
- Reference customers: {list}
- Timeline: {N weeks}
- Security/compliance terms: {yes/no}
```

3. **Confirm scope**: if user specified (e.g., "OCR only"), focus only on that scope from here.

### Phase 1: Technical Architecture Analysis

Analyze each module:

| Analysis Item | Content |
|---------------|---------|
| Architecture assessment | Reasonable / Over-engineered / Insufficient |
| Underlying tech inference | Which APIs / services / frameworks are likely used |
| Technical risks | Single points of failure, vendor lock-in, maintenance difficulty |
| Necessity | Is this module essential for the client's pain point? |
| Alternatives | Are there simpler or more mature alternatives? |

**Pay special attention to:**
- Dual/multi-engine designs → is it technically necessary or just marketing?
- ERP/CRM integration → confirm scope boundaries and cost ownership
- AI/ML claims → distinguish "uses API" vs "proprietary model"
- Security terms → distinguish "cloud-native built-in" vs "vendor-developed"

### Phase 2: Pricing Analysis

Conduct market benchmark comparison:

1. Each module's pricing vs market rates (provide market range)
2. Overage fees vs underlying API costs (calculate markup multiplier)
3. ROI verification — deconstruct vendor-claimed benefits, provide realistic estimates
4. Three-year TCO projection

**ROI Deconstruction Framework:**

| Item | Vendor Claims | Realistic Estimate | Discrepancy Reason |
|------|--------------|--------------------|--------------------|
| Annual labor savings | {vendor number} | {adjusted number} | {inflation point} |
| First-year ROI | {vendor %} | {adjusted %} | {calculation gap} |
| Payback period | {vendor months} | {adjusted months} | |

**Common inflation patterns:**
- "Saves N hours of labor" ≠ direct salary savings (efficiency gain ≠ headcount reduction)
- "AI automates 90%" → still needs human review, actual automation usually 60-70%
- ROI counts only benefits, ignores hidden costs (training, process change, exception handling)

### Phase 3: Market Intelligence

Use WebSearch to research:
- Vendor background: funding, team size, key clients, technical credibility
- Reference customer verification: do these companies publicly cite this vendor?
- Alternative vendors: at least 3-4 alternatives with pricing and features

If WebSearch is unavailable, note the gaps and suggest the user research them manually.

### Phase 4: Integrated Analysis

After collecting all data, synthesize into:

1. **Risk Matrix** (Critical / High / Medium)
2. **Alternative Solutions Comparison** (at least 3 options)
3. **Negotiation Strategy** (priority order + talking points)
4. **Recommended Path** (suggested decision path with fallback)

**Risk Classification:**

| Level | Criteria |
|-------|----------|
| Critical | Could cause project failure, must resolve before signing |
| High | Will increase cost or risk by 30%+, should constrain in contract |
| Medium | Monitor, have a backup plan |

### Phase 5: Output

#### 5a: Evaluation Report (Markdown)

Structure:
```
Title: {Client} {Module Type} Evaluation Report
Executive Summary (one-line conclusion + recommended action)
Chapter 1: Proposal Summary (factual, no judgment)
Chapter 2: Technical Architecture Analysis
Chapter 3: Pricing Analysis
Chapter 4: Market Intelligence & Vendor Verification
Chapter 5: Risk Matrix
Chapter 6: Alternative Solutions Comparison
Chapter 7: Financial Model (adjusted ROI + 3-year TCO)
Chapter 8: Negotiation Strategy
Appendix (methodology, data sources, disclaimers)
```

#### 5b: Comparison & Negotiation Sheet (Markdown tables)

**Table 1: Solution Comparison**
| Comparison Item | Option A | Option B | Option C | Recommendation | Notes |

**Table 2: PoC Acceptance Criteria**
| Acceptance Item | Pass Criteria | Test Method | Notes |

**Table 3: Negotiation Priorities**
| Priority | Negotiation Item | Target | Talking Point / Rationale |

## Competitor Exclusion Handling

If user specified "exclude certain competitors":

1. Don't recommend that competitor as alternative
2. Don't cite their pricing in market comparisons
3. Scan full report to remove all mentions
4. Note the exclusion in the report's methodology section

## Quality Gates

- [ ] Proposal summary card is complete
- [ ] Every module has "assessment + risk + alternative"
- [ ] ROI is deconstructed, not copied from vendor
- [ ] Overage fees have underlying cost and markup calculated
- [ ] Reference customers verified (public case study exists? yes/no)
- [ ] Risk matrix has Critical / High / Medium classification
- [ ] At least 3 alternatives with first-year cost estimates
- [ ] Negotiation strategy has priority order + specific talking points
- [ ] Report contains no excluded competitor names

## Heuristics

### Common Red Flags

- **Reference customers have no public case studies** → strongest negotiation leverage, demand PoC
- **Dual/multi-engine architecture** → usually marketing packaging, single engine suffices
- **Overage fee markup >10x underlying cost** → vendor's real profit pool, must negotiate
- **ROI claims >100% in year 1** → almost certainly inflated, deconstruct and verify
- **"Proprietary AI" but company <50 people** → likely API wrapper, not proprietary
- **Security terms are just buzzword lists** → probably cloud-native built-in, not vendor-developed
- **ERP integration "included in quote"** → confirm which ERPs, how many, cost ownership

### Negotiation Principles

1. **PoC before pricing** — for vendors with unproven track record, PoC is the strongest weapon
2. **Negotiate per module** — module-by-module beats whole-package discount
3. **Overage fees matter more than annual fees** — 10% off annual saves thousands; wrong overage structure costs tens of thousands long-term
4. **IP ownership matters more than price** — can't take anything with you when you leave = permanent lock-in
5. **Show alternatives** — naming specific alternative vendors shows you have options
