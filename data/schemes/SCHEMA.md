# rules.json Schema Documentation

## Purpose
Defines all 15 government welfare schemes with explicit, machine-evaluable eligibility rules.

## Top-Level Structure
Each entry is a JSON object with these fields:

| Field | Type | Purpose |
|-------|------|---------|
| `scheme_id` | string | Unique kebab-case identifier (e.g., `pm_kisan`) |
| `scheme_name` | string | Official scheme name |
| `description` | string | Brief description of scheme purpose and benefit |
| `rules` | array | Array of eligibility rule objects |
| `ambiguity_flags` | array | Known ambiguities, contradictions, or data gaps |
| `prerequisite_schemes` | array | Schemes that must be enrolled in first (if any) |
| `documents_required` | array | List of documents needed to apply |
| `benefit_amount` | string | Monetary or in-kind benefit |
| `frequency` | string | How often benefit is disbursed |
| `last_updated` | string | Last verified from official source (YYYY-MM format) |
| `official_source` | string | Government website or document |

## Rule Object Structure
Each rule must be evaluable by the RuleEngine:

```json
{
  "field": "string",              // User profile field name
  "operator": "string",           // ==, !=, <, >, <=, >=, in, not_in
  "value": "any",                 // Value to compare against
  "rule_type": "hard|soft",       // hard = must pass, soft = preferred
  "description": "string"         // Human-readable explanation
}
```

### Operators
- `==` : Exact equality
- `!=` : Not equal
- `<`, `>`, `<=`, `>=` : Numeric comparison
- `in` : Value is in list
- `not_in` : Value is not in list

### Rule Types
- `hard` : Must pass to qualify. Failure = Not Eligible
- `soft` : Preferred but not mandatory. Failure = Partial Eligible

## Ambiguity Flag Structure
```json
{
  "issue": "string",              // Title of ambiguity
  "description": "string",        // Details and impact
  "severity": "high|medium|low"   // Confidence impact
}
```

## Decision Log for 3 Base Schemes

### PM Kisan
**Data Source:** pmkisan.gov.in official guidelines
**Key Rules:**
- Farmer status is hard (occupation field)
- Land ownership > 0 is hard
- Bank account is hard (DBT requirement)
- Aadhaar is hard (authentication)
- Income < ₹2L is soft (target demographic but not strictly enforced)

**Ambiguities Flagged:**
1. **Land ownership** - Leased land eligibility unclear
2. **High-income farmers** - Threshold not explicitly defined
3. **Family definition** - Income limits reference "family" but scope varies

**Rejected Alternative:** Attempted to model "small and marginal farmer" as a hard rule, but state-level variation made this impossible to hardcode. Marked as soft instead.

### MGNREGA
**Data Source:** nrega.nic.in, Ministry of Rural Development guidelines
**Key Rules:**
- Rural residency is hard (Census 2011 boundary)
- Age >= 18 is hard
- Indian citizenship is hard

**Ambiguities Flagged:**
1. **Rural area boundary** - Census 2011 outdated; sprawl affects definition
2. **Job guarantee vs demand** - Scheme guarantees 100 days but implementation varies
3. **Govt employee exclusion** - Casual/contractual workers have unclear status
4. **Overlap with PM Kisan** - Unclear if farmer can claim both simultaneously

**Rejected Alternative:** Attempted to include "must not be govt employee" as hard rule, but state policies differ. Removed from hard rules.

### Ayushman Bharat (PM-JAY)
**Data Source:** pmjay.gov.in, official circulars
**Key Rules:**
- SECC 2011 categories D1/D2 is hard
- BPL status is soft alternative pathway
- Income threshold is soft (APL ceiling)

**Ambiguities Flagged:**
1. **SECC data staleness** - 2011 data, 13+ years old, many excluded who should qualify
2. **SECC/BPL mismatch** - No perfect overlap; state-level supplements vary
3. **Income threshold variance** - Urban vs rural vs state modifications
4. **Family definition** - Income aggregation rules unclear

**Rejected Alternative:** Initially modeled this as purely SECC-based, but widespread data gaps necessitated BPL as soft alternative pathway.

## Next Steps
Remaining 12 schemes will be extracted via parser.py, following this schema exactly.
