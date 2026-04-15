# Project Kalam — Prompt Log

Log of all AI interactions during development. Every prompt, output, decision documented.

---

## Prompt #1
**Tool:** Manual (no AI used)
**Task:** Create folder structure and requirements.txt
**Timestamp:** 2026-04-15
**Action:** Created full directory tree and base requirements
**Output received:** Directory structure created at ~/project-kalam
**Decision:** Accepted
**Reason:** Matches specification; non-AI foundation task

---

## Prompt #2
**Tool:** Manual research + domain knowledge
**Task:** Build rules.json for PM Kisan, MGNREGA, Ayushman Bharat
**Timestamp:** 2026-04-15
**Approach:** Reviewed official government guidelines to establish structured eligibility rules
**Sources Used:**
- pmkisan.gov.in — PM Kisan Samman Nidhi guidelines
- nrega.nic.in — MGNREGA rules
- pmjay.gov.in — Ayushman Bharat eligibility criteria
**Key Decision:** Modeled rules as explicit logical predicates (field, operator, value) rather than prose
**Ambiguities Flagged:** Identified 12 high/medium severity ambiguities across 3 schemes
**Rejected Alternatives:**
1. Prose-based rules (would require NLP to evaluate) — avoided for clarity
2. Fixed "small and marginal farmer" as hard rule — rejected due to state-level variation
3. Boolean "can apply" fields — rejected; need field-level granularity for explanations

**Rejected Alternatives:**
- ML-based confidence scoring (no training data, cannot explain)
- Gap analysis uses category + action suggestions per field
- Document prioritization is scheme-impact-aware (not uniform)

**Rejected Alternatives:**
- ML-based confidence scoring (no training data, cannot explain)
- Static document checklists (doesn't adapt to user's eligible schemes)
- Linear confidence model (now uses priority-weighted deduction)

---

## Prompt #4
**Tool:** Manual implementation
**Task:** Build conversational interface (app.py, index.html) and edge case tests
**Timestamp:** 2026-04-15
**Modules Created:**
1. **app.py** — Flask web server with /chat endpoint
   - Extracts profile from Hinglish messages using Claude API
   - Calls RuleEngine to match against schemes
   - Returns results with gaps and document checklist
   - Session management (in-memory; upgrade to Redis in production)

2. **index.html** — Chat UI with tabs for schemes and documents
   - Message bubbles (user/assistant)
   - Scheme results cards (status badge, confidence %, explanation)
   - Document checklist with processing times
   - Responsive design (mobile-friendly)

3. **test_edge_cases.py** — Test runner for 10 adversarial profiles
   - Documents what engine returned vs expected result
   - Identifies failure modes (wrong answer, overconfident, correctly flagged)
   - Generates test report with diagnostic information

**Key Decisions:**
- Used Claude API for profile extraction (no training data needed)
- Prioritized fields by scheme impact (Aadhaar > bank account > income)
- UI shows confidence % to users (not just FULL/PARTIAL/NO)

**Rejected Alternatives:**
- Form-based questionnaire (too rigid for Hinglish input)
- Free-form conversation (Claude hallucinates profile fields)
- Async evaluation (added latency; profile typically complete in 5 turns)

---

## Prompt #5
**Tool:** Manual research + domain knowledge
**Task:** Build cross-scheme ambiguity analysis (ambiguity_map.json)
**Timestamp:** 2026-04-15
**Approach:** Analyzed 15 schemes for contradictions, overlaps, ambiguous terms
**Key Findings:**
- CONTRADICTIONS: PM Kisan/MGNREGA overlap on govt employee exclusion (unclear)
- OVERLAPS: PM Ujjwala + PM Jan Dhan both target BPL (non-conflicting)
- AMBIGUOUS TERMS: "Small and marginal farmer", "economically weaker section", "family", "land holding" all vary by state
- STATE VARIATIONS: MGNREGA wages, PMAY cost ceilings, BPL lists all state-dependent
- DATA QUALITY: SECC 2011 is 13 years old; no automatic update mechanism

**Document:** Created `ambiguity_map.json` with:
- 2 contradictions documented
- 4 major overlaps identified
- 8 ambiguous terms flagged with severity levels
- 4 state-level variations noted
- 4 data quality issues flagged

**Workarounds Suggested:**
- Always verify with local Tehsildar/Panchayat
- Get written confirmation for ambiguous criteria
- Start document collection early (some take 60 days)

---

## Prompt #6
**Tool:** Manual architecture design
**Task:** Write architecture.md and complete documentation
**Timestamp:** 2026-04-15
**Document Structure:**
1. Executive summary and system diagram
2. Component descriptions (Interface, Engine, Data layers)
3. Technical decision log (3 key decisions with alternatives)
4. Production readiness assessment (6 critical gaps identified)
5. Scalability considerations
6. Testing strategy
7. Maintenance runbook
8. Future enhancements

**Critical Gaps Identified:**
1. Rule freshness (no auto-update for yearly scheme changes)
2. Ground truth validation (AI-extracted rules need expert review)
3. Session persistence (in-memory storage not scalable)
4. SECC 2011 data staleness (13 years old)
5. Internationalization (Hinglish only; no regional languages)
6. Privacy & security (no encryption, compliance checks)

**Decision:** All gaps documented for pre-production deployment checklist.

---

## Prompt #7
**Tool:** Manual documentation
**Task:** Write comprehensive README.md
**Timestamp:** 2026-04-15
**Content:**
- Quick start guide
- Example conversation
- 15 schemes table with benefits
- System architecture diagram
- Project folder structure
- Key concepts (rules, confidence, status)
- Testing instructions
- Limitations & gaps
- Production readiness path
- FAQ & support

**Tone:** User-friendly for both developers and policy makers

---

## PROJECT COMPLETION SUMMARY

**Total Prompts:** 7 (0 AI API calls for business logic; only profile extraction & parsing use Claude)
**Files Created:** 15+
**Schemes Implemented:** 3 base (manual) + framework for 12 more (via parser.py)
**Test Cases:** 10 edge cases fully documented
**Documentation:** 4 comprehensive docs (architecture, README, schema, prompt log)

**Key Achievements:**
✓ Rule-based matching engine (deterministic, explainable)
✓ Gap analysis for partial matches (actionable suggestions)
✓ Document prioritization (unlocks most schemes first)
✓ Web interface with Hinglish support
✓ Edge case testing (ambiguity detection validated)
✓ Comprehensive documentation (architecture decisions documented)
✓ Production readiness assessment (gaps identified, paths to fix outlined)

**Production Deployment Checklist:**
- [ ] Domain experts validate all 15 schemes
- [ ] Implement rule freshness update pipeline
- [ ] Migrate sessions to Redis/DB
- [ ] Security audit & encryption
- [ ] Regional language support
- [ ] Beta test with 100+ real users
- [ ] State government partnership

**Maintenance Plan:**
- Weekly: Monitor logs, check scheme updates
- Monthly: Regression test edge cases
- Quarterly: Expert review of ambiguities
- Annually: Full compliance audit, strategy review

---


## Prompt #3
**Tool:** Manual implementation
**Task:** Build engine modules (rule_engine.py, gap_analyser.py, doc_checklist.py)
**Timestamp:** 2026-04-15
**Modules Created:**
1. **rule_engine.py** — RuleEngine class evaluates user profiles against scheme rules
   - Returns MatchResult with status (FULL/PARTIAL/NO), confidence scores, rule traces
   - Confidence logic: 1.0 if all hard rules pass, degrades by 0.05 per soft failure + 0.08 per ambiguity
   - Provides gap analysis for PARTIAL matches
   
2. **gap_analyser.py** — GapAnalyser class generates actionable fix suggestions
   - Categorizes gaps: hard_failures (critical), soft_failures (recommended), ambiguities (clarify)
   - Generates priority roadmap for user to become fully eligible
   - Suggests specific actions per field
   
3. **doc_checklist.py** — DocChecklist class prioritizes documents
   - Registry of 10+ documents with processing times, costs, prereqs
   - Sorts by: (1) priority level, (2) schemes unlocked, (3) processing speed
   - Aadhaar = CRITICAL (unlocks 13/15 schemes, 7 days)
   - Bank account = CRITICAL (unlocks 6 schemes, 3 days)

**Key Decisions:**
- Confidence scoring is rule-trace-based (explainable) not ML-based (black box)
- Gap analysis uses category + action suggestions per field
- Document prioritization is scheme-impact-aware (not uniform)

**Rejected Alternatives:**
- ML-based confidence scoring (no training data, cannot explain)
- Static document checklists (doesn't adapt to user's eligible schemes)
- Linear confidence model (now uses priority-weighted deduction)

---

