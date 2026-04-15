# Project Kalam: Architecture & Data Flow (Phase 1)

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Web Chat Interface (Hinglish)                            │   │
│  │  "Main kisan hoon, 2 acre zameen hai, bank account hai"  │   │
│  └──────────────────────────┬───────────────────────────────┘   │
└─────────────────────────────┼───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FLASK APPLICATION LAYER                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  /chat (Chat endpoint)                                   │   │
│  │  /questions (7-level questions)                          │   │
│  │  /filter (Apply filters)                                 │   │
│  │  /scheme-details (Get scheme + requirements)             │   │
│  └──────────────────────────┬───────────────────────────────┘   │
└─────────────────────────────┼───────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
    ┌──────────────┐  ┌────────────────┐  ┌──────────────┐
    │ Profile      │  │ Question       │  │ Scheme       │
    │ Extraction   │  │ Engine         │  │ Matcher      │
    │              │  │                │  │              │
    │ engine/      │  │ engine/        │  │ engine/      │
    │ extract_     │  │ question_      │  │ rule_        │
    │ profile.py   │  │ engine.py      │  │ engine.py    │
    └──────┬───────┘  └────────┬───────┘  └───────┬──────┘
           │                   │                   │
           ▼                   ▼                   ▼
    ┌──────────────────────────────────────────────────────┐
    │         QUESTION HIERARCHY (7 LEVELS)                 │
    │                                                        │
    │  L1: Category (10 options) ─→ ~500 schemes remain    │
    │  L2: Life Stage (8 options) ─→ ~300 schemes remain   │
    │  L3: Specific Need (10) ─→ ~150 schemes remain       │
    │  L4: Demographics (8, multi) ─→ ~80 schemes remain   │
    │  L5: Age/Marital (8) ─→ ~50 schemes remain           │
    │  L6: Income/Region (8) ─→ 10-25 schemes (FINAL)      │
    │  L7: Results Display ─→ Schemes + Requirements       │
    └──────────────────────────┬───────────────────────────┘
                               │
                               ▼
    ┌──────────────────────────────────────────────────────┐
    │         AI SCHEME EXTRACTION LAYER                    │
    │                                                        │
    │  engine/ai_scheme_extractor.py                       │
    │                                                        │
    │  Multi-turn Claude Extraction:                        │
    │  1. Scheme Overview                                   │
    │  2. Eligibility Mapping (to 7 levels)               │
    │  3. Benefits Extraction (quantified)                 │
    │  4. Requirements Extraction (all docs)               │
    │  5. WHERE TO GET (URLs + locations)                 │
    │  6. Application Process                              │
    │  7. Contact Information                              │
    │  8. Timeline & Deadlines                             │
    │  9. Validation Checklist                             │
    └──────────────────────────┬───────────────────────────┘
                               │
                               ▼
    ┌──────────────────────────────────────────────────────┐
    │              CLAUDE API (Anthropic)                   │
    │              (External AI Service)                    │
    └──────────────────────────┬───────────────────────────┘
                               │
                               ▼
    ┌──────────────────────────────────────────────────────┐
    │         GOVERNMENT WEBSITES (Data Sources)            │
    │                                                        │
    │  pmkisan.gov.in (PM Kisan)                           │
    │  ayushmanbharat.gov.in (Health)                      │
    │  nrega.nic.in (Rural Employment)                     │
    │  skillindia.gov.in (Training)                        │
    │  ... 46 more official scheme URLs                    │
    └──────────────────────────┬───────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
    ┌──────────────────────────┐  ┌──────────────────────────┐
    │   EXTRACTED SCHEMES DB   │  │  REQUIREMENT SOURCES DB  │
    │                          │  │                          │
    │  data/schemes/           │  │  "Aadhaar Card" →        │
    │  extracted_schemes.json  │  │  {                       │
    │                          │  │    "url": "uidai.gov.in" │
    │  50+ schemes:            │  │    "location": "office"  │
    │  - PM Kisan              │  │    "time": "10-15 days"  │
    │  - Ayushman Bharat       │  │    "cost": "Free"        │
    │  - MGNREGA               │  │  }                       │
    │  - ... (47 more)         │  │                          │
    │                          │  │                          │
    │  Each scheme contains:   │  │  10+ common requirements │
    │  - name                  │  │  with full sourcing info │
    │  - eligibility_criteria  │  │                          │
    │  - requirements          │  └──────────────────────────┘
    │  - benefits              │
    │  - where_to_get_links    │
    │  - application_url       │
    │  - contact_info          │
    └──────────────────────────┘
```

---

## 7-Level Filtering Flow (With Remaining Counts)

```
START: User Profile Input
│
├─ "Main kisan hoon, Bihar, bank account hai"
│
▼
LEVEL 1: CATEGORY
┌──────────────────────────────────────────────────────────┐
│ "Which category are you interested in?"                  │
│                                                           │
│ ◉ Agriculture     ○ Education      ○ Health              │
│ ○ Housing         ○ Employment      ○ Finance            │
│ ○ Business        ○ Infrastructure  ○ Social             │
│                                                           │
│ → Selected: Agriculture                                 │
│ → Remaining: ~12 AGRICULTURE schemes                    │
└──────────────────────────────────────────────────────────┘
│
▼
LEVEL 2: LIFE STAGE
┌──────────────────────────────────────────────────────────┐
│ "What is your life stage?"                              │
│                                                           │
│ ◉ Farmer           ○ Student         ○ Senior            │
│ ○ Entrepreneur     ○ Working         ○ Retired           │
│ ○ Homemaker        ○ Unemployed                           │
│                                                           │
│ → Selected: Farmer                                      │
│ → Remaining: ~8 FARMER schemes                          │
│ → These: PM Kisan, MGNREGA, Crop Insurance, etc.       │
└──────────────────────────────────────────────────────────┘
│
▼
LEVEL 3: SPECIFIC NEED (MULTI-SELECT)
┌──────────────────────────────────────────────────────────┐
│ "What do you need? (select all that apply)"             │
│                                                           │
│ ☑ Financial Assistance  ☐ Training                      │
│ ☐ Employment            ☐ Housing                       │
│ ☐ Education             ☑ Subsidies                     │
│ ☐ Health                ☐ Loans                         │
│                                                           │
│ → Selected: Financial Assistance, Subsidies            │
│ → Remaining: ~5 schemes                                │
│ → These: PM Kisan, Soil Health Card, Irrigation       │
└──────────────────────────────────────────────────────────┘
│
▼
LEVEL 4: DEMOGRAPHICS (MULTI-SELECT)
┌──────────────────────────────────────────────────────────┐
│ "Do any of these apply? (select all that apply)"        │
│                                                           │
│ ☐ SC/ST/OBC         ☐ Woman           ☐ Minority        │
│ ☐ PwD               ☐ Transgender     ☐ BPL             │
│ ☐ Ex-Serviceman     ☑ None                              │
│                                                           │
│ → Selected: None                                        │
│ → Remaining: ~5 schemes (all agricultural)             │
└──────────────────────────────────────────────────────────┘
│
▼
LEVEL 5: AGE / MARITAL STATUS (MULTI-SELECT)
┌──────────────────────────────────────────────────────────┐
│ "Age group and marital status?"                          │
│                                                           │
│ ☑ 25-40 years       ☐ 18-25            ☐ 40-60         │
│ ☐ 60+               ☑ Married          ☐ Single        │
│ ☐ Widow             ☐ Divorced                           │
│                                                           │
│ → Selected: 25-40, Married                             │
│ → Remaining: ~5 schemes                                │
└──────────────────────────────────────────────────────────┘
│
▼
LEVEL 6: INCOME / REGION (SINGLE SELECT)
┌──────────────────────────────────────────────────────────┐
│ "Where do you live and what's your income?"             │
│                                                           │
│ ◉ Rural, < ₹1.5L     ○ Rural, ₹1.5-3L                  │
│ ○ Rural, ₹3-5L       ○ Rural, > ₹5L                     │
│ ○ Urban, < ₹1.5L     ○ Urban, ₹1.5-3L                  │
│ ○ Urban, ₹3-5L       ○ Urban, > ₹5L                     │
│                                                           │
│ → Selected: Rural, < ₹1.5L                             │
│ → Remaining: 3-4 FINAL MATCHING SCHEMES               │
└──────────────────────────────────────────────────────────┘
│
▼
LEVEL 7: RESULTS WITH REQUIREMENTS
┌──────────────────────────────────────────────────────────┐
│ ✅ PERFECTLY MATCHING SCHEMES (3)                       │
├──────────────────────────────────────────────────────────┤
│ [1] PM KISAN SAMMAN NIDHI                               │
│     Benefit: ₹6,000/year                                │
│     Ministry: Agriculture                               │
│                                                           │
│     📋 DOCUMENTS REQUIRED:                              │
│     • Aadhaar Card                                       │
│       ► https://uidai.gov.in/                           │
│       ► UIDAI office in your district                   │
│       ► Processing: 10-15 days, Free                    │
│                                                           │
│     • Bank Account Passbook                              │
│       ► Your bank (NEFT-enabled)                        │
│       ► Already have (mentioned in profile)             │
│                                                           │
│     • Land Ownership Certificate                         │
│       ► Revenue office (Patwari) in your taluk          │
│       ► Processing: 5-7 days, ₹50                       │
│                                                           │
│     📞 APPLY:                                           │
│     • Helpline: 1800-180-1551                           │
│     • Website: https://pmkisan.gov.in/                  │
│     • Apply at: Gram Panchayat office                   │
│     • Next deadline: 30 June 2026                       │
│                                                           │
│     [APPLY NOW] [WHERE TO GET DOCS] [MORE INFO]        │
├──────────────────────────────────────────────────────────┤
│ [2] MGNREGA (100 Days Work)                             │
│ [3] SOIL HEALTH CARD SCHEME                             │
│                                                           │
│ 🟡 ALMOST ELIGIBLE SCHEMES (1)                         │
│ [4] PRADHAN MANTRI FASAL BIMA                           │
│     ⚠️ Missing: Crop insurance ID                       │
│                                                           │
│ [DOWNLOAD PDF OF REQUIREMENTS]                          │
│ [SHARE RESULTS] [FEEDBACK]                              │
└──────────────────────────────────────────────────────────┘
```

---

## Data Flow: From Government Website → User Result

```
GOVERNMENT OFFICIAL SOURCE
│
│ gov.in website
│ (pmkisan.gov.in, etc.)
│
▼
┌─────────────────────────────────────────┐
│  AI SCHEME EXTRACTOR                    │
│  (Claude Multi-turn Extraction)         │
│                                          │
│  Turn 1: Overview extraction             │
│  "Extract name, ministry, purpose"       │
│  → Returns: scheme_overview JSON        │
│                                          │
│  Turn 2: Eligibility mapping             │
│  "Map to 7-level questions"              │
│  → Returns: eligibility_criteria JSON   │
│                                          │
│  Turn 3: Requirements extraction         │
│  "List all documents needed"             │
│  → Returns: requirements array           │
│                                          │
│  Turn 4: WHERE TO GET mapping            │
│  "For each doc, find official URL + office"
│  → Returns: where_to_get_sources JSON   │
│                                          │
│  ... 5 more extraction turns ...         │
│                                          │
│  → COMPLETE SCHEME OBJECT               │
└──────────────┬──────────────────────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ EXTRACTED_SCHEMES.JSON   │
    │ (50+ schemes database)   │
    │                          │
    │ {                        │
    │   "schemes": [           │
    │     {                    │
    │       "id": "pm_kisan",  │
    │       "name": "...",     │
    │       "benefits": "...", │
    │       "requirements": [  │
    │         {               │
    │           "item": "Aadhaar"
    │           "where_to_get": {
    │             "url": "..."
    │             "location": "..."
    │           }
    │         }
    │       ]
    │     }
    │   ]
    │ }
    └──────────────┬───────────┘
                   │
         ┌─────────┼─────────┐
         ▼         ▼         ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │ Cache  │ │Database│ │  API   │
    │(Redis) │ │(JSON)  │ │Endpoint│
    └────────┘ └────────┘ └────────┘
         │         │         │
         └─────────┼─────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │  QUESTION ENGINE                 │
    │  (7-level progressive filtering) │
    │                                  │
    │  Input: User profile             │
    │  Process: Apply 7 filters        │
    │  Output: Matching schemes        │
    └──────────────┬───────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │  RESULT FORMATTER                │
    │  (Add requirements + URLs)        │
    │                                  │
    │  For each matched scheme:        │
    │  - Show eligibility status       │
    │  - Display ALL requirements      │
    │  - Show WHERE TO GET each        │
    │  - Provide application link      │
    │  - Show contact info             │
    └──────────────┬───────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │  USER INTERFACE                  │
    │  (Hinglish Chat + Web UI)        │
    │                                  │
    │  "Aapko ye 3 scheme mil gaye!" │
    │  [Schemes with requirements]     │
    │  [Apply buttons]                 │
    │  [Download checklist]            │
    └──────────────────────────────────┘
```

---

## Data Structures

### Scheme Object
```json
{
  "scheme_id": "pm_kisan",
  "scheme_name": "PM Kisan Samman Nidhi",
  "ministry": "Ministry of Agriculture & Farmers Welfare",
  "category": "agriculture",
  "description": "Direct income support of ₹6000/year to all landholding farmers",
  
  "eligibility_criteria": {
    "level_1_category": "agriculture",
    "level_2_life_stage": ["farmer"],
    "level_3_specific_need": ["financial_assistance"],
    "level_4_demographics": ["none"],
    "level_5_age_marital": ["all"],
    "level_6_income_region": ["rural", "all_income_brackets"],
    "exclusion_criteria": "Farmers with monthly income > ₹15,000"
  },
  
  "benefits": {
    "amount": "6000",
    "currency": "INR",
    "frequency": "yearly",
    "payment_mode": "Direct transfer to bank account",
    "max_beneficiary_benefit": "6000 per year"
  },
  
  "requirements": [
    {
      "category": "Documents",
      "items": ["aadhaar_card", "bank_account_passbook"],
      "where_to_get": {
        "aadhaar_card": {
          "official_website": "https://uidai.gov.in/",
          "physical_location": "UIDAI Enrollment Center in your district",
          "processing_time": "10-15 days",
          "cost": "Free for residents"
        },
        "bank_account_passbook": {
          "official_website": "Your bank website",
          "physical_location": "Your bank branch (NEFT/RTGS enabled)",
          "processing_time": "Same day",
          "cost": "Free"
        }
      }
    }
  ],
  
  "application_process": [
    "Step 1: Visit PM Kisan official website",
    "Step 2: Click 'Farmer Registration'",
    "Step 3: Enter Aadhaar and bank details",
    "Step 4: Upload documents",
    "Step 5: Submit application",
    "Step 6: Wait for verification (5-7 days)"
  ],
  
  "contact_information": {
    "helpline": "1800-180-1551",
    "email": "pmkisan-ict@nic.in",
    "website": "https://pmkisan.gov.in/",
    "mobile_app": "mKisan"
  },
  
  "timeline": {
    "application_window": "Ongoing",
    "current_deadline": "30 June 2026",
    "disbursement_timeline": "Quarterly (Jan, Apr, Jul, Oct)",
    "scheme_validity": "Ongoing since 2018"
  }
}
```

### Question Object
```json
{
  "level": 1,
  "level_name": "CATEGORY",
  "question_text": "Which category are you interested in?",
  "help_text": "Select the main area you need help with",
  "multiple_select": false,
  "options": [
    {
      "value": "agriculture",
      "label": "Agriculture & Farming",
      "description": "For farmers and agricultural activities",
      "emoji": "🌾"
    },
    {
      "value": "education",
      "label": "Education & Training",
      "description": "For students and skill development",
      "emoji": "📚"
    },
    // ... 8 more options
  ]
}
```

### Extraction Template
```json
{
  "name": "requirements_extraction",
  "description": "Extract ALL required documents and certifications",
  "prompt_template": "For the scheme '{scheme_name}', list EVERY requirement needed...",
  "required_fields": ["documents", "certifications", "digital_requirements"],
  "quality_checks": [
    "Benefit amount must be quantified",
    "Application URL must be valid",
    "Processing time must be realistic"
  ]
}
```

---

## Technology Stack

```
┌─────────────────────────────────────────────────┐
│            FRONTEND                              │
│ HTML5 + CSS3 + JavaScript + Bootstrap            │
│ Responsive Web UI                               │
│ Hinglish Chat Interface                         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│            BACKEND (Flask)                       │
│ Python 3.11 + Flask 3.0.0                       │
│ /chat, /questions, /filter, /scheme-details    │
│ JSON API endpoints                              │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
    ┌────────────────────────────────┐
    │  BUSINESS LOGIC LAYER           │
    │                                 │
    │ • QuestionEngine (7-level)     │
    │ • RuleEngine (eligibility)     │
    │ • SchemeExtractor (AI)         │
    │ • ProfileExtractor             │
    └────────────────┬────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │Schemes   │ │Rules     │ │Ambiguity │
    │DB        │ │DB        │ │Map       │
    │(JSON)    │ │(JSON)    │ │(JSON)    │
    └──────────┘ └──────────┘ └──────────┘
        │
        ▼
    ┌─────────────────────────┐
    │  EXTERNAL SERVICES      │
    │                         │
    │ • Anthropic Claude API  │
    │ • Government APIs       │
    │ • Official gov.in sites │
    └─────────────────────────┘
```

---

**Architecture Documentation Complete**  
**All 50 Phase 1 schemes ready for extraction and deployment**  
**Status:** Ready for next phase ✅
