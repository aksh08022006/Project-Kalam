# Phase 1 Deployment Guide

## Overview

Deploy Project Kalam with **50 Phase 1 schemes** as a production-ready platform with:
- ✅ Intelligent 7-level progressive filtering
- ✅ Requirement mapping + "where to get" document sources
- ✅ AI-extracted scheme details
- ✅ End-to-end chat interface
- ✅ Transparent confidence scoring

---

## Pre-Deployment Checklist

### Infrastructure Requirements
- [ ] Python 3.9+ (test with `python --version`)
- [ ] PostgreSQL 12+ for production (optional for pilot)
- [ ] Docker for containerized deployment
- [ ] 2GB RAM minimum, 5GB storage for 50+ schemes
- [ ] Internet connection (for Claude API calls)

### API Setup
- [ ] Anthropic API key (https://console.anthropic.com/)
- [ ] Set `ANTHROPIC_API_KEY` environment variable
- [ ] Test API connectivity: `python -c "import anthropic"`

### Government Data Sources
- [ ] Verify all official scheme URLs are accessible
- [ ] Ensure extraction prompts match current government websites
- [ ] Contact relevant ministries for any data inconsistencies

---

## Extraction Phase: Preparing 50 Schemes

### Step 1: List Schemes to Extract

All 50 Phase 1 schemes are listed in [PHASE_1_SCHEMES.md](../PHASE_1_SCHEMES.md).

Create `data/schemes/phase1_urls.json`:

```json
{
  "agriculture": [
    {"name": "PM Kisan Samman Nidhi", "url": "https://pmkisan.gov.in/"},
    {"name": "MGNREGA", "url": "https://nrega.nic.in/"},
    {"name": "Pradhan Mantri Fasal Bima Yojana", "url": "https://pmfby.gov.in/"}
  ],
  "education": [
    {"name": "Pradhan Mantri Scholarship Scheme", "url": "https://www.pmss.gov.in/"},
    {"name": "Skill India Mission", "url": "https://www.skillindia.gov.in/"}
  ]
}
```

### Step 2: Extract Scheme Details

Run the extraction pipeline:

```bash
# Run extraction for all Phase 1 schemes
python engine/ai_scheme_extractor.py \
  --input data/schemes/phase1_urls.json \
  --output data/schemes/extracted_schemes.json \
  --batch_size 5

# Expected output:
# [1/50] Extracting: PM Kisan Samman Nidhi
# ✓ Successfully extracted PM Kisan Samman Nidhi
# [2/50] Extracting: MGNREGA
# ✓ Successfully extracted MGNREGA
# ...
# Saved 50 extracted schemes to data/schemes/extracted_schemes.json
```

### Step 3: Validate Extracted Data

```bash
# Validate schema and completeness
python -c "
import json
with open('data/schemes/extracted_schemes.json') as f:
    data = json.load(f)
    print(f'✓ Extracted {data[\"total_schemes\"]} schemes')
    for scheme in data['schemes']:
        assert scheme['scheme_name'], 'Missing scheme name'
        assert scheme['eligibility_criteria'], 'Missing eligibility'
        assert scheme['requirements'], 'Missing requirements'
    print('✓ All schemes pass validation')
"
```

### Step 4: Manual Quality Review

For each of the 50 schemes, verify:
- [ ] Benefit amounts are current (check latest govt update)
- [ ] URLs are working and point to official sources
- [ ] Application process is complete (no missing steps)
- [ ] Requirements are realistic and comprehensive
- [ ] Contact information is current

Sample review template:
```
SCHEME: PM Kisan Samman Nidhi
Extracted benefit: ₹6000/year
✓ Verified from https://pmkisan.gov.in/ (2026-04-16)
✓ Application process: 8 steps listed
✓ Requirements: Aadhaar, Bank Account, Land Cert
✓ Contact: 1800-180-1551 (tested 2026-04-16)
Status: READY FOR DEPLOYMENT
```

---

## Integration Phase: Plug into Application

### Step 1: Load Schemes into Engine

Update `engine/question_engine.py`:

```python
from engine.ai_scheme_extractor import load_extracted_schemes

class QuestionEngine:
    def __init__(self):
        self.all_schemes = load_extracted_schemes('data/schemes/extracted_schemes.json')
        self.current_filters = {}
        self.question_hierarchy = self._build_questions()
```

### Step 2: Create /questions Endpoint

Add to `interface/app.py`:

```python
@app.route('/questions', methods=['GET'])
def get_question():
    """Get question for specific level"""
    level = request.args.get('level', 1, type=int)
    
    if level < 1 or level > 7:
        return {'error': 'Invalid level (1-7)'}, 400
    
    question = question_engine.get_question(level)
    return {
        'level': level,
        'question': question.question_text,
        'options': question.options,
        'help_text': question.help_text,
        'multiple_select': question.multiple_select
    }

@app.route('/filter', methods=['POST'])
def apply_filter():
    """Apply filter and get remaining schemes count"""
    data = request.json
    level = data.get('level')
    answers = data.get('answers', [])
    
    remaining = question_engine.apply_filter(level, answers)
    
    return {
        'level': level,
        'schemes_remaining': remaining,
        'next_question_level': level + 1 if level < 6 else 7
    }

@app.route('/scheme-details/<scheme_id>', methods=['GET'])
def get_scheme_details(scheme_id):
    """Get scheme with full requirements and where-to-get information"""
    scheme = question_engine.get_scheme_by_id(scheme_id)
    details = question_engine.get_scheme_with_requirements(scheme)
    
    return details
```

### Step 3: Update Frontend (Optional)

Create progressive filtering UI:

```html
<!-- Step 1: Category Selection -->
<div id="level-1">
  <p>Which category are you interested in?</p>
  <button onclick="selectCategory('agriculture')">Agriculture</button>
  <button onclick="selectCategory('education')">Education</button>
  <!-- etc -->
</div>

<!-- Step 2-6: Progressive filtering with "X schemes remaining" -->
<div id="progress">
  <p><strong>128 schemes match your criteria so far</strong></p>
  <p>Answer more questions for better matching...</p>
</div>

<!-- Step 7: Results with Requirements -->
<div id="results">
  <div class="scheme-card">
    <h3>PM Kisan Samman Nidhi</h3>
    <p><strong>Benefit:</strong> ₹6000/year</p>
    
    <h4>Documents Required:</h4>
    <ul>
      <li>Aadhaar Card
        <p>Where to get: https://uidai.gov.in/ | UIDAI office in your district</p>
      </li>
      <li>Bank Account Passbook
        <p>Where to get: Your bank | NEFT-enabled</p>
      </li>
    </ul>
    
    <button onclick="applyScheme('pm_kisan')">Apply Now</button>
  </div>
</div>
```

---

## Deployment Phase: Launch

### Option 1: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY="sk-..."

# Run server
python interface/app.py

# Access at http://localhost:5000
```

### Option 2: Docker Deployment (Production)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV ANTHROPIC_API_KEY=""

EXPOSE 5000
CMD ["python", "interface/app.py"]
```

Build and run:

```bash
# Build image
docker build -t project-kalam:phase1 .

# Run container
docker run -e ANTHROPIC_API_KEY="sk-..." -p 5000:5000 project-kalam:phase1

# Access at http://localhost:5000
```

### Option 3: Cloud Deployment (Azure/AWS)

#### Azure Container Instances
```bash
az container create \
  --resource-group myResourceGroup \
  --name project-kalam \
  --image project-kalam:phase1 \
  --environment-variables ANTHROPIC_API_KEY="sk-..." \
  --ports 5000
```

#### AWS Lambda (Serverless)
```bash
# Package
zip -r function.zip . -x "*.git*"

# Deploy
aws lambda create-function \
  --function-name project-kalam-phase1 \
  --runtime python3.11 \
  --handler interface/app.lambda_handler \
  --zip-file fileb://function.zip
```

---

## Testing Phase

### Test 1: End-to-End Chat

```bash
pytest tests/test_e2e.py -v

# Expected output:
# test_agriculture_farmer PASSED
# test_student_education PASSED  
# test_elderly_health PASSED
# ✓ All tests passed
```

### Test 2: 7-Level Filtering

```python
# Test progressive filtering with all 50 schemes
from engine.question_engine import QuestionEngine

engine = QuestionEngine()
print(f"Total schemes: {len(engine.all_schemes)}")  # Should be 50

# Q1: Category
remaining = engine.apply_filter(1, ['agriculture'])
print(f"After Q1 (agriculture): {remaining} schemes")  # ~12

# Q2: Life Stage
remaining = engine.apply_filter(2, ['farmer'])
print(f"After Q2 (farmer): {remaining} schemes")  # ~8

# ... continue through Q6
# Final result should be 2-5 matching schemes
```

### Test 3: Requirements Display

```python
from engine.question_engine import QuestionEngine

engine = QuestionEngine()
scheme = engine.get_filtered_schemes()[0]
details = engine.get_scheme_with_requirements(scheme)

print(f"Scheme: {details['scheme_name']}")
for category, reqs in details['requirements_by_category'].items():
    print(f"\n{category}:")
    for item in reqs['items']:
        print(f"  • {item}")
        print(f"    → {reqs['where_to_get'][item]}")
```

---

## Monitoring & Maintenance

### Daily Checks
- [ ] API availability (ping /health endpoint)
- [ ] Scheme extraction errors (check logs)
- [ ] User queries (sample conversations)

### Weekly Updates
- [ ] Review failed queries
- [ ] Check for government website changes
- [ ] Update scheme deadlines if needed

### Monthly Validation
- [ ] Re-verify 5-10 random schemes
- [ ] Check for benefit amount changes
- [ ] Update requirements as per govt updates
- [ ] Review user feedback

### Quarterly Expansion
- [ ] Extract Phase 2 schemes (50 more)
- [ ] Integrate and test new schemes
- [ ] Update documentation
- [ ] Deploy updated version

---

## Roadmap Milestones

| Phase | Schemes | Timeline | Status |
|-------|---------|----------|--------|
| Phase 1 | 50 | April 2026 | 🔵 Current |
| Phase 2 | 50 | Q2 2026 | ⚪ Planned |
| Phase 3 | 200+ | Q3 2026 | ⚪ Planned |
| Phase 4 | 1000+ | Q4 2026 | ⚪ Planned |
| Phase 5 | 5062+ | 2027 | ⚪ Planned |

---

## Troubleshooting

### Issue: API Key Error
```
Error: ANTHROPIC_API_KEY not set
```
**Fix:**
```bash
export ANTHROPIC_API_KEY="sk-..."  # macOS/Linux
set ANTHROPIC_API_KEY=sk-...       # Windows
```

### Issue: Scheme Extraction Timeout
```
Error: Request timeout after 30s
```
**Fix:** Increase timeout or reduce batch size
```python
SchemeExtractor(timeout=60, batch_size=3)
```

### Issue: Low Filtering Accuracy
```
0 schemes matching after 6 questions
```
**Fix:** Review eligibility mapping in extraction prompts, may need manual adjustment

---

## Support

- **Issues:** Report on GitHub with "Phase 1 Deployment" tag
- **Questions:** Check FAQ in README.md
- **Feedback:** Contact project maintainers
