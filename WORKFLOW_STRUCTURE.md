# Project Kalam - New Workflow Structure

## Overview
Scaled from 15 schemes to a framework supporting **5062 government schemes** using 7-level progressive filtering.

## 7-Level Question Hierarchy

### Level 1: Category (Question 1)
**Question:** Which category are you interested in?  
**Filters:** ~5062 → ~500 schemes  
**Categories:** Agriculture, Education, Health, Business, Housing, Social, Jobs, Finance, Infrastructure, Others

### Level 2: Life Stage (Question 2)
**Question:** What is your current life stage?  
**Filters:** ~500 → ~250-300 schemes  
**Options:** Student, Working Professional, Entrepreneur, Farmer, Senior Citizen, Homemaker, Unemployed, Retired

### Level 3: Specific Need (Question 3)
**Question:** What is your specific need? (Multi-select)  
**Filters:** ~250 → ~100-150 schemes  
**Options:** Financial Assistance, Training, Employment, Housing, Education, Health, Loans, Subsidies, Infrastructure, Tech

### Level 4: Demographics (Question 4)
**Question:** Do any of these describe you? (Multi-select)  
**Filters:** ~100 → ~50-80 schemes  
**Options:** SC/ST/OBC, Woman, Minority, PwD, Transgender, BPL, Ex-Serviceman, None

### Level 5: Age & Marital Status (Question 5)
**Question:** What is your age group and marital status? (Multi-select)  
**Filters:** ~50 → ~30-50 schemes  
**Age:** 18-25, 25-40, 40-60, 60+  
**Status:** Single, Married, Widow, Divorced

### Level 6: Location & Income (Question 6)
**Question:** What is your region and annual family income?  
**Filters:** ~30 → **10-25 schemes (FINAL MATCHES)**  
**Options:** Rural/Urban + Income brackets (< ₹1.5L, ₹1.5-3L, ₹3-5L, > ₹5L)

### Level 7: Results Display (Question 7)
**Display:** All matching schemes WITH requirements and where to get documents
**Shows:**
- Scheme name & ministry
- Benefits offered
- Eligibility summary
- **NEW:** Complete requirements list
- **NEW:** Where to get each requirement
- Application URL & contact info

## NEW Feature: Requirements & Sources

For each matched scheme, users see:

```
SCHEME: PM Kisan Samman Nidhi

DOCUMENTS REQUIRED:
✓ Aadhaar Card
  → Where to get: https://uidai.gov.in/ | UIDAI office in your district

✓ Bank Account Passbook
  → Where to get: Your bank | Must be NEFT/RTGS enabled

✓ Land ownership proof
  → Where to get: Revenue office (Patwari) | District administration

CERTIFICATIONS:
✓ Income Certificate
  → Where to get: Taluk/Revenue office | With bank statements

CONTACT & APPLICATION:
- Nodal Officer: [Phone/Email]
- Apply at: https://pmkisan.gov.in
- Deadline: [Date]
- Step-by-step guide: [Link]
```

## Technical Structure

### Files
- `engine/question_engine.py` - 7-level question engine
- `data/workflow_structure.json` - Complete workflow definition
- `data/schemes/rules.json` - Scheme definitions (expandable to 5062)

### Question Engine Features
- Progressive filtering with remaining scheme count
- Multi-select and single-select questions
- Automatic requirement mapping
- Centralized requirement sources

### Database Schema
```json
{
  "scheme": {
    "id": "pm_kisan",
    "name": "PM Kisan Samman Nidhi",
    "category": "agriculture",
    "eligibility": {
      "demographics": ["farmer", "rural"],
      "income_limit": 500000
    },
    "requirements": [
      {
        "category": "Documents",
        "items": ["aadhaar", "bank_passbook"],
        "where_to_get": {
          "aadhaar": "https://uidai.gov.in/ | UIDAI office",
          "bank_passbook": "Your bank | NEFT/RTGS enabled"
        }
      }
    ]
  }
}
```

## Expansion Roadmap

| Phase | Schemes | Timeline |
|-------|---------|----------|
| Phase 1 | 15 flagship schemes | Current |
| Phase 2 | 50 major ministry schemes | Q2 2026 |
| Phase 3 | 200+ multi-category schemes | Q3 2026 |
| Phase 4 | 1000 central + state schemes | Q4 2026 |
| Phase 5 | 5062 complete database | 2027 |

## User Experience Flow

```
Start
  ↓
Q1: Category? (Multiple options)
  ↓ "Agriculture"
Q2: Life Stage? (Multiple options)
  ↓ "Farmer"
Q3: Specific Need? (Multi-select)
  ↓ "Financial Assistance" + "Subsidy"
Q4: Demographics? (Multi-select)
  ↓ "SC/ST/OBC" + "BPL"
Q5: Age/Marital? (Multi-select)
  ↓ "Age 25-40" + "Married"
Q6: Income/Region? (Single option)
  ↓ "Rural, Income ₹1.5-3 Lakh"
  ↓
Results: 12-18 matching schemes
  ↓
User clicks scheme
  ↓
See all requirements + WHERE TO GET each
  ↓
Apply button → Official scheme portal
```

## Key Advantages

✅ **Personalized Filtering** - 7 levels ensure highly targeted results  
✅ **Transparent** - Shows why you're eligible for each scheme  
✅ **Action-Oriented** - Not just what you need, but WHERE to get it  
✅ **Scalable** - Framework ready for 5062 schemes  
✅ **Requirement-Centric** - Addresses citizen pain point: "What documents do I need?"  

## Next Steps

1. Populate scheme database with 50+ schemes (Phase 2)
2. Integrate with official scheme URLs
3. Add requirement source APIs
4. Build requirement checklist feature
5. Expand to state-level schemes

---

**Status:** Framework complete, ready for 5062-scheme database integration  
**Version:** 2.0 - Multi-scheme Progressive Filtering  
**Updated:** April 15, 2026
