#!/usr/bin/env python3
"""
parser.py — PDF to Structured Eligibility Rules Converter

This script reads a government welfare scheme PDF, extracts text using pdfplumber,
sends it to the Claude API, and receives back structured JSON eligibility rules
and ambiguity flags.

Rules are returned as explicit logical predicates: {field, operator, value}
Each rule must be evaluable by RuleEngine without additional NLP.

Usage:
    python parser.py <pdf_path> <scheme_id> <scheme_name>
    
Example:
    python parser.py data/raw_pdfs/pm_ujjwala.pdf pm_ujjwala "PM Ujjwala Yojana"
"""

import json
import sys
import os
from pathlib import Path
from typing import Optional
import pdfplumber
from anthropic import Anthropic

# Initialize Anthropic client
client = Anthropic()

EXTRACTION_SYSTEM_PROMPT = """You are an expert government policy analyst specializing in Indian welfare schemes.

Your task: Extract eligibility rules from government welfare scheme PDFs and return them as structured JSON.

CRITICAL RULES FOR OUTPUT:
1. Each eligibility criterion must become ONE rule object with: {field, operator, value, rule_type, description}
2. Operators MUST be one of: ==, !=, <, >, <=, >=, in, not_in
3. rule_type MUST be "hard" (must pass to qualify) or "soft" (preferred, not mandatory)
4. NEVER return prose descriptions as rules. Convert prose into logical predicates.
5. For ANY ambiguous, contradictory, or unclear criterion, add to ambiguity_flags array
6. If a criterion has multiple valid values, use "in" operator with an array
7. ALL numeric values must be actual numbers, not strings

FIELD NAMING CONVENTION:
- age, annual_income, family_size (integers)
- occupation (string: farmer/labour/business/govt/student/other)
- state (string: state name or abbreviation)
- has_bank_account, has_aadhaar, is_woman, bpl_card (booleans)
- in_rural_area, in_urban_area, is_student, is_pregnant (booleans)
- land_owned_acres, monthly_income (floats)
- caste (string: GEN/OBC/SC/ST)
- secc_2011_rating (string: code like d1, d2, etc)

EXAMPLE OUTPUT STRUCTURE:
{
  "scheme_id": "pm_ujjwala",
  "scheme_name": "Pradhan Mantri Ujjwala Yojana",
  "description": "LPG connection for BPL households",
  "rules": [
    {
      "field": "bpl_card",
      "operator": "==",
      "value": true,
      "rule_type": "hard",
      "description": "Must have BPL card"
    },
    {
      "field": "annual_income",
      "operator": "<=",
      "value": 100000,
      "rule_type": "soft",
      "description": "Income ceiling for eligibility"
    }
  ],
  "ambiguity_flags": [
    {
      "issue": "BPL definition varies",
      "description": "BPL criteria differ across states; no uniform income threshold",
      "severity": "high"
    }
  ],
  "prerequisite_schemes": [],
  "documents_required": ["BPL Certificate", "Photo ID", "Address Proof"],
  "benefit_amount": "LPG connection subsidy",
  "frequency": "One-time"
}

NOW: Extract rules from the provided PDF text."""

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file using pdfplumber."""
    text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text.append(f"--- PAGE {i} ---\n{page_text}")
        return "\n".join(text)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        raise

def parse_scheme_from_pdf(pdf_path: str, scheme_id: str, scheme_name: str) -> dict:
    """
    Parse a scheme PDF and extract structured eligibility rules.
    
    Args:
        pdf_path: Path to the PDF file
        scheme_id: Unique scheme identifier (kebab-case)
        scheme_name: Official scheme name
        
    Returns:
        Dictionary with extracted rules, ambiguities, and metadata
    """
    print(f"Reading PDF: {pdf_path}")
    pdf_text = extract_text_from_pdf(pdf_path)
    
    print(f"Sending to Claude API for extraction...")
    
    # Send to Claude with explicit instruction for JSON output
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        system=EXTRACTION_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""Extract eligibility rules from this government welfare scheme PDF.

Scheme ID: {scheme_id}
Scheme Name: {scheme_name}

PDF CONTENT:
{pdf_text}

Return ONLY valid JSON. No preamble, no explanation, just the JSON object."""
            }
        ]
    )
    
    # Extract the response text
    response_text = message.content[0].text
    
    # Parse JSON
    try:
        result = json.loads(response_text)
        print(f"✓ Successfully extracted rules for {scheme_name}")
        print(f"  - {len(result.get('rules', []))} rules found")
        print(f"  - {len(result.get('ambiguity_flags', []))} ambiguities flagged")
        return result
    except json.JSONDecodeError as e:
        print(f"ERROR: Claude response was not valid JSON")
        print(f"Response: {response_text[:500]}...")
        raise

def interactive_refinement(scheme_data: dict) -> dict:
    """
    Allow user to interactively refine extracted rules through multi-turn conversation.
    
    Args:
        scheme_data: Initial extracted scheme data
        
    Returns:
        Refined scheme data
    """
    print(f"\n{'='*60}")
    print("INTERACTIVE REFINEMENT SESSION")
    print(f"{'='*60}")
    print(f"Scheme: {scheme_data.get('scheme_name')}")
    print(f"Current rules: {len(scheme_data.get('rules', []))}")
    print(f"Current ambiguities: {len(scheme_data.get('ambiguity_flags', []))}")
    print("\nEnter questions or corrections (type 'done' to finish):")
    print("Examples:")
    print("  - 'Is age a hard or soft rule?'")
    print("  - 'Add a rule for land ownership'")
    print("  - 'Is this scheme superseded by another?'")
    print("-" * 60)
    
    conversation_history = [
        {
            "role": "user",
            "content": f"Here is the extracted scheme data: {json.dumps(scheme_data, indent=2)}"
        }
    ]
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'done':
            break
        
        conversation_history.append({"role": "user", "content": user_input})
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system="You are helping refine government welfare scheme eligibility rules. Provide concise, actionable feedback. If the user suggests changes to the JSON, return updated JSON.",
            messages=conversation_history
        )
        
        assistant_message = response.content[0].text
        conversation_history.append({"role": "assistant", "content": assistant_message})
        print(f"\nAssistant: {assistant_message}")
    
    return scheme_data

def save_rules(scheme_data: dict, output_path: str = "data/schemes/rules.json"):
    """
    Save extracted scheme to rules.json, appending or updating as needed.
    
    Args:
        scheme_data: Scheme dictionary to save
        output_path: Path to rules.json file
    """
    # Load existing rules
    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            all_rules = json.load(f)
    else:
        all_rules = []
    
    # Check if scheme already exists
    scheme_id = scheme_data['scheme_id']
    existing_index = next(
        (i for i, s in enumerate(all_rules) if s.get('scheme_id') == scheme_id),
        None
    )
    
    if existing_index is not None:
        print(f"Updating existing scheme: {scheme_id}")
        all_rules[existing_index] = scheme_data
    else:
        print(f"Adding new scheme: {scheme_id}")
        all_rules.append(scheme_data)
    
    # Save back to file
    with open(output_path, 'w') as f:
        json.dump(all_rules, f, indent=2)
    
    print(f"✓ Saved to {output_path}")

def main():
    """Main entry point for parser."""
    if len(sys.argv) < 2:
        print("Usage: python parser.py <pdf_path> [scheme_id] [scheme_name]")
        print("Example: python parser.py data/raw_pdfs/ujjwala.pdf pm_ujjwala 'PM Ujjwala Yojana'")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    scheme_id = sys.argv[2] if len(sys.argv) > 2 else Path(pdf_path).stem
    scheme_name = sys.argv[3] if len(sys.argv) > 3 else scheme_id.replace('_', ' ').title()
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found: {pdf_path}")
        sys.exit(1)
    
    # Extract rules
    scheme_data = parse_scheme_from_pdf(pdf_path, scheme_id, scheme_name)
    
    # Optional: Interactive refinement
    print("\nProceed with refinement? (y/n): ", end="")
    if input().strip().lower() == 'y':
        scheme_data = interactive_refinement(scheme_data)
    
    # Save
    save_rules(scheme_data)
    
    print(f"\n✓ Scheme {scheme_id} ready for RuleEngine evaluation")

if __name__ == "__main__":
    main()
