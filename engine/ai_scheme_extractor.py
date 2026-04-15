"""
AI-Powered Scheme Extractor
Extracts government scheme details from official sources using Claude
Input: Scheme URL + 7-level filtering context
Output: Structured SchemeData with requirements, eligibility, benefits
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import json
from anthropic import Anthropic

# Initialize Anthropic client
client = Anthropic()


@dataclass
class ExtractedScheme:
    """Structure for extracted scheme data"""
    scheme_id: str
    scheme_name: str
    ministry: str
    category: str  # From 7-level Q1
    description: str
    benefits: List[str]
    eligibility_criteria: Dict[str, Any]
    requirements: Dict[str, List[str]]  # category -> [items]
    where_to_get_requirements: Dict[str, Dict[str, str]]  # requirement -> {url, physical_location}
    application_process: List[str]
    application_url: str
    contact_info: Dict[str, str]
    funding_amount: Optional[str]
    timeline_or_deadline: Optional[str]
    official_source_url: str


class SchemeExtractor:
    """Extract scheme details using Claude AI"""
    
    def __init__(self):
        self.conversation_history = []
        self.extraction_context = self._build_extraction_context()
    
    def _build_extraction_context(self) -> str:
        """Build context about 7-level filtering for better extraction"""
        return """
You are a government scheme expert analyzing Indian welfare schemes.
When extracting scheme details, pay attention to these 7-level eligibility filters:

LEVEL 1 - CATEGORY: Agriculture, Education, Health, Business, Housing, Social, Jobs, Finance, Infrastructure, Others
LEVEL 2 - LIFE STAGE: Student, Working Professional, Entrepreneur, Farmer, Senior Citizen, Homemaker, Unemployed, Retired
LEVEL 3 - SPECIFIC NEED: Financial Assistance, Training, Employment, Housing, Education, Health, Loans, Subsidies, Infrastructure, Tech (multi-select)
LEVEL 4 - DEMOGRAPHICS: SC/ST/OBC, Woman, Minority, PwD, Transgender, BPL, Ex-Serviceman, None (multi-select)
LEVEL 5 - AGE/MARITAL: Age groups (18-25, 25-40, 40-60, 60+), Marital status (single, married, widow, divorced) (multi-select)
LEVEL 6 - INCOME/REGION: Rural/Urban + Income brackets (< ₹1.5L, ₹1.5-3L, ₹3-5L, > ₹5L)

When extracting scheme details:
1. Map eligibility criteria to 7-level filters
2. Extract ALL requirements with exact names
3. For each requirement, identify WHERE to get it (URL + physical location)
4. List benefits clearly and quantify where possible
5. Extract application process step-by-step
6. Get contact information and application URLs
"""
    
    def extract_scheme(self, scheme_url: str, scheme_name: str) -> ExtractedScheme:
        """
        Extract scheme details using multi-turn conversation with Claude
        
        Args:
            scheme_url: URL of scheme details page
            scheme_name: Name of scheme to extract
            
        Returns:
            ExtractedScheme dataclass with complete details
        """
        self.conversation_history = []
        
        # Turn 1: Initial extraction request
        initial_prompt = f"""
Please extract complete details about the scheme: {scheme_name}
from this source: {scheme_url}

Extract:
1. Official scheme name and ID
2. Administering ministry
3. Category (from 7-level filter)
4. Description and purpose
5. Benefits offered (quantified)
6. Eligibility criteria (map to 7-level filters)
7. Required documents/certifications
8. Application process (step-by-step)
9. Contact information and application URLs
10. Timeline and important deadlines

Return as structured JSON.
"""
        
        response = self._send_message(initial_prompt)
        extraction_data = self._parse_response(response)
        
        # Turn 2: Requirement sourcing
        requirements_prompt = f"""
For the requirements listed in the {scheme_name} scheme, now provide WHERE TO GET each requirement:

For each document/certificate, provide:
- Official URL to apply/download
- Physical location (office/center) to obtain
- Processing time if applicable
- Fee if any

Return as JSON mapping: requirement_name -> {{url, physical_location, processing_time, fee}}
"""
        
        req_response = self._send_message(requirements_prompt)
        requirements_data = self._parse_response(req_response)
        
        # Turn 3: Validation and completeness check
        validation_prompt = """
Based on the scheme details extracted so far, validate:
1. Are all eligibility criteria covered?
2. Are there any missing requirements?
3. Is the application process clear (all steps listed)?
4. Are contact details complete?

Provide any missing information or clarifications.
"""
        
        validation_response = self._send_message(validation_prompt)
        
        # Compile final scheme object
        return self._compile_scheme(
            scheme_name, 
            extraction_data, 
            requirements_data, 
            scheme_url
        )
    
    def _send_message(self, user_message: str) -> str:
        """Send message to Claude and maintain conversation history"""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=self.extraction_context,
            messages=self.conversation_history
        )
        
        assistant_message = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from Claude response"""
        try:
            # Try to find JSON block in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Return as structured data from Claude's response
        return {"raw_response": response}
    
    def _compile_scheme(self, 
                       scheme_name: str, 
                       extraction: Dict, 
                       requirements: Dict, 
                       source_url: str) -> ExtractedScheme:
        """Compile extracted data into ExtractedScheme object"""
        
        scheme = ExtractedScheme(
            scheme_id=self._generate_scheme_id(scheme_name),
            scheme_name=scheme_name,
            ministry=extraction.get("ministry", "Unknown"),
            category=extraction.get("category", "Other"),
            description=extraction.get("description", ""),
            benefits=extraction.get("benefits", []),
            eligibility_criteria=extraction.get("eligibility_criteria", {}),
            requirements=extraction.get("requirements", {}),
            where_to_get_requirements=requirements.get("requirement_sources", {}),
            application_process=extraction.get("application_process", []),
            application_url=extraction.get("application_url", ""),
            contact_info=extraction.get("contact_info", {}),
            funding_amount=extraction.get("funding_amount", None),
            timeline_or_deadline=extraction.get("timeline", None),
            official_source_url=source_url
        )
        
        return scheme
    
    def _generate_scheme_id(self, scheme_name: str) -> str:
        """Generate scheme ID from name"""
        return scheme_name.lower().replace(" ", "_").replace("-", "_")[:50]
    
    def batch_extract_schemes(self, 
                            schemes_list: List[Dict[str, str]]) -> List[ExtractedScheme]:
        """
        Extract multiple schemes
        
        Args:
            schemes_list: List of {"name": str, "url": str} dicts
            
        Returns:
            List of ExtractedScheme objects
        """
        extracted_schemes = []
        
        for i, scheme_info in enumerate(schemes_list, 1):
            print(f"\n[{i}/{len(schemes_list)}] Extracting: {scheme_info['name']}")
            try:
                extracted = self.extract_scheme(
                    scheme_info['url'],
                    scheme_info['name']
                )
                extracted_schemes.append(extracted)
                print(f"✓ Successfully extracted {scheme_info['name']}")
            except Exception as e:
                print(f"✗ Error extracting {scheme_info['name']}: {str(e)}")
                continue
        
        return extracted_schemes


def save_extracted_schemes(schemes: List[ExtractedScheme], output_file: str):
    """Save extracted schemes to JSON file"""
    schemes_data = [asdict(scheme) for scheme in schemes]
    
    with open(output_file, 'w') as f:
        json.dump({
            "total_schemes": len(schemes),
            "extraction_timestamp": __import__('datetime').datetime.now().isoformat(),
            "schemes": schemes_data
        }, f, indent=2)
    
    print(f"\nSaved {len(schemes)} extracted schemes to {output_file}")


if __name__ == "__main__":
    # Example usage
    extractor = SchemeExtractor()
    
    # Sample schemes to extract
    sample_schemes = [
        {
            "name": "PM Kisan Samman Nidhi",
            "url": "https://pmkisan.gov.in/"
        },
        {
            "name": "Ayushman Bharat",
            "url": "https://ayushmanbharat.gov.in/"
        }
    ]
    
    extracted = extractor.batch_extract_schemes(sample_schemes)
    save_extracted_schemes(extracted, "data/schemes/extracted_schemes.json")
