"""
Question-based filtering engine for 5062 government schemes
Similar to https://www.india.gov.in/my-government/schemes/search
7-level hierarchy for progressive filtering
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any

class QuestionLevel(Enum):
    """7-level hierarchy for scheme filtering"""
    LEVEL_1 = "category"
    LEVEL_2 = "life_stage"
    LEVEL_3 = "specific_need"
    LEVEL_4 = "demographic"
    LEVEL_5 = "eligibility"
    LEVEL_6 = "region_income"
    LEVEL_7 = "final_schemes"

@dataclass
class Question:
    """Represents a filtering question"""
    level: QuestionLevel
    question_text: str
    options: List[Dict[str, Any]]
    help_text: Optional[str] = None
    multiple_select: bool = False

@dataclass
class SchemeRequirement:
    """What is needed to apply for a scheme"""
    category: str
    items: List[str]
    where_to_get: Dict[str, str]

@dataclass
class Scheme:
    """Complete scheme with all details"""
    id: str
    name: str
    ministry: str
    description: str
    benefits: List[str]
    eligibility_criteria: Dict[str, Any]
    requirements: List[SchemeRequirement]
    application_url: str
    contact_info: str

class QuestionEngine:
    """7-level question hierarchy for filtering 5062 schemes"""
    
    def __init__(self):
        self.all_schemes: List[Scheme] = []
        self.current_filters: Dict[str, Any] = {}
        self.question_hierarchy = self._build_questions()
        self.schemes_remaining = len(self.all_schemes)
        
    def _build_questions(self) -> Dict[QuestionLevel, Question]:
        """Build the 7-level question hierarchy"""
        return {
            QuestionLevel.LEVEL_1: Question(
                level=QuestionLevel.LEVEL_1,
                question_text="Which category are you interested in?",
                options=[
                    {"id": "agriculture", "label": "Agriculture & Rural Development"},
                    {"id": "education", "label": "Education & Learning"},
                    {"id": "health", "label": "Health & Wellness"},
                    {"id": "business", "label": "Business & Entrepreneurship"},
                    {"id": "housing", "label": "Housing & Shelter"},
                    {"id": "social", "label": "Social Welfare"},
                    {"id": "jobs", "label": "Jobs & Skill Development"},
                    {"id": "finance", "label": "Financial Services"},
                    {"id": "infrastructure", "label": "Infrastructure & Industries"},
                    {"id": "other", "label": "Others"},
                ],
                help_text="Select the area you want schemes from"
            ),
            
            QuestionLevel.LEVEL_2: Question(
                level=QuestionLevel.LEVEL_2,
                question_text="What is your life stage?",
                options=[
                    {"id": "student", "label": "Student"},
                    {"id": "working", "label": "Working Professional"},
                    {"id": "entrepreneur", "label": "Entrepreneur/Self-Employed"},
                    {"id": "farmer", "label": "Farmer"},
                    {"id": "senior_citizen", "label": "Senior Citizen"},
                    {"id": "homemaker", "label": "Homemaker"},
                    {"id": "unemployed", "label": "Unemployed"},
                    {"id": "retired", "label": "Retired"},
                ],
                help_text="This helps us find schemes best suited to your situation"
            ),
            
            QuestionLevel.LEVEL_3: Question(
                level=QuestionLevel.LEVEL_3,
                question_text="What is your specific need?",
                options=[
                    {"id": "financial_assistance", "label": "Financial Assistance"},
                    {"id": "training", "label": "Training & Skill Development"},
                    {"id": "employment", "label": "Employment Assistance"},
                    {"id": "housing", "label": "Housing Assistance"},
                    {"id": "education", "label": "Education Support"},
                    {"id": "health", "label": "Health Support"},
                    {"id": "loan", "label": "Loans/Credit"},
                    {"id": "subsidy", "label": "Subsidies"},
                ],
                multiple_select=True,
                help_text="Select all that apply"
            ),
            
            QuestionLevel.LEVEL_4: Question(
                level=QuestionLevel.LEVEL_4,
                question_text="Do any of these describe you?",
                options=[
                    {"id": "sc_st_obc", "label": "SC/ST/OBC"},
                    {"id": "woman", "label": "Woman"},
                    {"id": "minority", "label": "Minority"},
                    {"id": "pwd", "label": "Person with Disability"},
                    {"id": "transgender", "label": "Transgender"},
                    {"id": "bpl", "label": "Below Poverty Line (BPL)"},
                    {"id": "apl", "label": "Above Poverty Line (APL)"},
                    {"id": "none", "label": "None of the above"},
                ],
                multiple_select=True,
                help_text="Select all categories you belong to"
            ),
            
            QuestionLevel.LEVEL_5: Question(
                level=QuestionLevel.LEVEL_5,
                question_text="What are your eligibility criteria?",
                options=[
                    {"id": "age_18_25", "label": "Age 18-25"},
                    {"id": "age_25_40", "label": "Age 25-40"},
                    {"id": "age_40_60", "label": "Age 40-60"},
                    {"id": "age_60_above", "label": "Age 60+"},
                    {"id": "married", "label": "Married"},
                    {"id": "widow", "label": "Widow/Widower"},
                    {"id": "divorced", "label": "Divorced/Separated"},
                    {"id": "single", "label": "Single"},
                ],
                multiple_select=True
            ),
            
            QuestionLevel.LEVEL_6: Question(
                level=QuestionLevel.LEVEL_6,
                question_text="What is your region and annual family income?",
                options=[
                    {"id": "rural_low", "label": "Rural, Income < ₹1.5 Lakh"},
                    {"id": "rural_medium", "label": "Rural, Income ₹1.5-3 Lakh"},
                    {"id": "rural_high", "label": "Rural, Income ₹3-5 Lakh"},
                    {"id": "rural_very_high", "label": "Rural, Income > ₹5 Lakh"},
                    {"id": "urban_low", "label": "Urban, Income < ₹1.5 Lakh"},
                    {"id": "urban_medium", "label": "Urban, Income ₹1.5-3 Lakh"},
                    {"id": "urban_high", "label": "Urban, Income ₹3-5 Lakh"},
                    {"id": "urban_very_high", "label": "Urban, Income > ₹5 Lakh"},
                ],
                help_text="This determines scheme eligibility"
            ),
            
            QuestionLevel.LEVEL_7: Question(
                level=QuestionLevel.LEVEL_7,
                question_text="Matching schemes found!",
                options=[],
                help_text="Below are all schemes you are eligible for"
            ),
        }
    
    def get_question(self, level: QuestionLevel) -> Question:
        """Get question for a specific level"""
        return self.question_hierarchy[level]
    
    def apply_filter(self, level: QuestionLevel, answers: List[str]) -> int:
        """Apply filter at each level and return remaining schemes"""
        self.current_filters[level.value] = answers
        filtered = self.get_filtered_schemes()
        self.schemes_remaining = len(filtered)
        return self.schemes_remaining
    
    def get_filtered_schemes(self) -> List[Scheme]:
        """Get schemes matching current filters"""
        filtered = self.all_schemes.copy()
        
        if "category" in self.current_filters:
            categories = self.current_filters["category"]
            filtered = [s for s in filtered if s.eligibility_criteria.get("category") in categories]
        
        if "demographic" in self.current_filters:
            demographics = self.current_filters["demographic"]
            filtered = [s for s in filtered if any(
                d in s.eligibility_criteria.get("demographics", []) for d in demographics
            )]
        
        if "region_income" in self.current_filters:
            region_income = self.current_filters["region_income"]
            filtered = [s for s in filtered if self._check_income_eligibility(s, region_income)]
        
        return filtered
    
    def _check_income_eligibility(self, scheme: Scheme, region_income: List[str]) -> bool:
        """Check if scheme matches region/income criteria"""
        scheme_income_limit = scheme.eligibility_criteria.get("income_limit", float('inf'))
        
        for ri in region_income:
            if "low" in ri and scheme_income_limit >= 150000:
                return True
            elif "medium" in ri and scheme_income_limit >= 300000:
                return True
            elif "high" in ri and scheme_income_limit >= 500000:
                return True
            elif "very_high" in ri:
                return True
        return False
    
    def add_scheme(self, scheme: Scheme) -> None:
        """Add a scheme to database"""
        self.all_schemes.append(scheme)
    
    def get_scheme_with_requirements(self, scheme: Scheme) -> Dict[str, Any]:
        """Get scheme with requirements and where to get them"""
        result = {
            "scheme_name": scheme.name,
            "ministry": scheme.ministry,
            "description": scheme.description,
            "benefits": scheme.benefits,
            "requirements_by_category": {},
            "application_url": scheme.application_url,
            "contact_info": scheme.contact_info
        }
        
        for req in scheme.requirements:
            result["requirements_by_category"][req.category] = {
                "items": req.items,
                "where_to_get": req.where_to_get
            }
        
        return result

# Requirement sources mapping
REQUIREMENT_SOURCES = {
    "aadhaar": "https://uidai.gov.in/ | UIDAI office in your district",
    "pan_card": "https://www.incometaxindia.gov.in/ | Income Tax Department",
    "bank_account": "Your bank | NEFT/RTGS enabled",
    "ration_card": "State Food & Civil Supply Department | Online or offline",
    "caste_certificate": "SDM/Tahsil office | State-specific process",
    "income_certificate": "Taluk/Revenue office | With income proof",
    "bpl_certificate": "Municipality/Gram Panchayat | District welfare office",
    "voter_id": "Election Commission | Voter helpline",
    "domicile_certificate": "District administration | Revenue department",
    "medical_report": "ASHA worker/ANM | Government health center",
}
