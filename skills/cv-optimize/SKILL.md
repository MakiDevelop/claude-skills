---
name: cv-optimize
description: Resume/CV optimization. Analyze a resume, reposition strengths, and produce an optimized PDF tailored to a target role.
argument-hint: "<resume_file_path> [target role or company name] [emphasis points]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, Agent
author: Maki
version: "1.0.0"
tags: [career, resume, cv, job-search, pdf]
required_env: []
required_bins: [uv]
platforms: [macos, linux]
safety_level: safe
---

# /cv-optimize — Resume Analysis & Optimization

Read a resume file (PDF / Markdown / DOCX), perform structured analysis, and produce a target-role-optimized PDF.

---

## Phase 0: Collect Input

1. **Resume file**: Read from user-provided path (supports PDF / Markdown)
2. **Target info** (from arguments or ask user):
   - Target role (e.g., "AI Engineer", "PM", "Data Scientist")
   - Target company name (optional, for tailoring)
   - JD content or link (optional, for keyword alignment)
   - Emphasis points (e.g., "leadership", "bilingual", "career transition")

If no target role is provided, ask once:

```
What role are you optimizing for? (e.g., AI Engineer / PM / Data Scientist / general)
Any specific strengths you want to emphasize?
```

---

## Phase 1: Resume Analysis

After reading the full resume, output a structured analysis:

```
## Resume Analysis — {Name}

### Basic Info
- Name / Target title / Total experience / Education

### Strengths (Keep)
1. ... (list 3-5 highlights worth keeping, especially quantified achievements)

### Issues (Needs Optimization)
| # | Issue | Severity | Description |
|---|-------|----------|-------------|
| 1 | ... | High/Med/Low | ... |

### Target Role Match Analysis
| Requirement | Candidate's Experience | Match Level |
|-------------|----------------------|-------------|
| ... | ... | Strong/Medium/Weak/Gap |
```

**Mandatory checks** (every resume):
- [ ] Title vs target alignment
- [ ] Summary is focused (no more than 3 key positioning statements)
- [ ] Each experience has quantified results
- [ ] Skills section aligned with target role (flag outdated skills)
- [ ] Timeline is clear and consistent
- [ ] Structure depth doesn't exceed 2 levels
- [ ] Space allocation proportional to relevance
- [ ] Each role includes Tech Stack

---

## Phase 2: Reposition & Optimize

### 2.1 Positioning Adjustment
- Redefine subtitle (role positioning statement)
- Rewrite Summary (focus on 2-3 key differentiators with numbers)
- If emphasis points were specified, highlight them in Summary and highlight box

### 2.2 Experience Restructuring
- Add Tech Stack tags to each role (blockquote or meta style)
- Expand highly relevant experiences with section-label sub-blocks
- Condense less relevant experiences to 2-4 bullets
- Every bullet follows "Action verb + what you did + quantified result"
- Avoid weak verbs ("participated", "assisted") → use "led", "designed", "built", "optimized"

### 2.3 Skills Section Rebuild
- Remove skills irrelevant to target role
- Group by category (e.g., AI/ML, Data, Infrastructure, Tools)
- Ensure target role's core keywords all appear

### 2.4 Special Sections (add when appropriate)
- **"Why I'm right for X" highlight box**: when target is clear and emphasis points exist
- **"Career transition trajectory"**: when candidate has obvious career pivots
- **Selected side projects table**: keep only 3-5 relevant to target

---

## Phase 3: Generate Optimized PDF

Use `uv run --with weasyprint` to generate PDF.

### 3.1 HTML Structure

```
Element mapping:
- h1          → Name
- .subtitle   → Role positioning statement
- .contact    → Contact info
- h2          → Major section titles (Summary / Experience / Skills)
- .job-title  → Job title per role
- .job-company → Company + location + dates
- .job-meta   → Tech Stack (blue left-border blockquote)
- .section-label → Sub-section titles (gray background)
- ul > li     → Bullet points (single level only, no nesting)
- table       → Competencies / Skills / Projects
- .highlight-box → Special emphasis block (blue left-border + light gray background)
```

### 3.2 Layout Rules
- **Target 2 pages** (max 3, never leave a near-empty trailing page)
- Font size: headings 21-22pt / body 9-9.5pt / meta 8.5pt
- Line height 1.5-1.55
- Margins 16-18mm
- Table headers: dark blue background, white text; even rows light gray
- No 3+ level nesting — flatten deep structures

### 3.3 PDF Generation

```python
# Zero-install execution with uv
uv run --with weasyprint python3 script.py
```

After generation:
1. Use Read tool to verify PDF layout
2. If trailing page is too empty, adjust margin/font-size and regenerate
3. Confirm page count is reasonable, tell user the file path

### 3.4 Output File Naming
```
{original_file_directory}/{Name}_{Target_Role}_optimized.pdf
```

---

## Phase 4: Change Summary

Output a concise comparison table:

```
| Item | Original | Optimized |
|------|----------|-----------|
| Positioning | ... | ... |
| Summary | ... | ... |
| Skills | ... | ... |
| Length | ... | ... |
```

Plus notes (e.g., sections where the candidate needs to provide specific numbers).

---

## Design Principles

1. **One resume, one narrative** — all bullets serve the same positioning story
2. **Quantify > describe** — "improved 67%" beats "significantly improved" every time
3. **Delete > shrink > keep** — irrelevant experience: cut to 2 lines, don't waste half a page
4. **ATS-friendly** — ensure target role's core keywords appear in Summary + Skills + Experience
5. **Clear visual hierarchy** — 10-second scan reveals: name → positioning → 3 key numbers → timeline
6. **No empty words** — delete "eager learner", "team player", "value creator" — they carry zero information

---

## Color System

```css
Primary (dark blue):
- Heading text:      #0d1b2a
- Section titles:    #1b263b
- Accent:            #415a77
- Light background:  #f0f4f8
- Table header:      #1b263b (white text)
- Table even rows:   #f8f9fa
- Section labels:    #e8edf2
```
