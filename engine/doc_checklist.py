#!/usr/bin/env python3
"""
doc_checklist.py — Generates priority-ordered document checklists.

For a user eligible for multiple schemes, this module prioritizes documents by:
1. How many schemes they unlock
2. Processing time (fast/slow documents)
3. Prerequisite dependencies (some docs unlock others)
"""

from typing import List, Dict, Set, Any
from dataclasses import dataclass
from enum import Enum


class DocPriority(Enum):
    """Priority level for obtaining a document."""
    CRITICAL = 1  # Unlocks many schemes, quick to obtain
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class DocumentInfo:
    """Information about a government document."""
    name: str
    priority: DocPriority
    processing_time_days: int
    schemes_unlocked: List[str]  # scheme_ids this doc unlocks
    prerequisites: List[str]  # docs needed before this one
    obtainable_from: str  # Where to get it
    estimated_cost: str  # Approximate cost


class DocChecklist:
    """Generates optimized document checklists for users."""
    
    # Master registry of documents and their properties
    DOCUMENTS = {
        "aadhaar": DocumentInfo(
            name="Aadhaar Card",
            priority=DocPriority.CRITICAL,
            processing_time_days=7,
            schemes_unlocked=["pm_kisan", "mgnrega", "pmjay", "pmay_gramin", "pmay_urban", 
                             "pm_ujjwala", "pm_jan_dhan", "pm_suraksha_bima", "pm_jeevan_jyoti",
                             "apy", "pm_matru_vandana", "pm_poshan", "svaniidhi"],
            prerequisites=[],
            obtainable_from="Nearest UIDAI Enrollment Center",
            estimated_cost="Free"
        ),
        "bank_account": DocumentInfo(
            name="Bank Account",
            priority=DocPriority.CRITICAL,
            processing_time_days=3,
            schemes_unlocked=["pm_kisan", "pm_jan_dhan", "pm_suraksha_bima", 
                             "pm_jeevan_jyoti", "apy", "pm_matru_vandana"],
            prerequisites=["aadhaar"],  # Easier with Aadhaar (Jan Dhan scheme)
            obtainable_from="Any Scheduled Bank",
            estimated_cost="Free (some banks charge service fees)"
        ),
        "bpl_card": DocumentInfo(
            name="BPL / Ration Card",
            priority=DocPriority.HIGH,
            processing_time_days=30,
            schemes_unlocked=["pmjay", "pm_ujjwala", "pm_poshan"],
            prerequisites=[],
            obtainable_from="Local Municipality / Revenue Office",
            estimated_cost="Free (may require small application fee)"
        ),
        "land_records": DocumentInfo(
            name="Land Records (Khasra/Khatauni)",
            priority=DocPriority.HIGH,
            processing_time_days=14,
            schemes_unlocked=["pm_kisan", "pmay_gramin"],
            prerequisites=[],
            obtainable_from="District Revenue Office / Patwari",
            estimated_cost="₹50–200 per copy"
        ),
        "address_proof": DocumentInfo(
            name="Address Proof",
            priority=DocPriority.MEDIUM,
            processing_time_days=0,  # Usually have this already
            schemes_unlocked=["mgnrega", "pm_ujjwala"],
            prerequisites=[],
            obtainable_from="Issued by various authorities",
            estimated_cost="Free (electricity/water bill typically used)"
        ),
        "income_cert": DocumentInfo(
            name="Income Certificate",
            priority=DocPriority.MEDIUM,
            processing_time_days=7,
            schemes_unlocked=["nsp", "stand_up_india"],
            prerequisites=[],
            obtainable_from="Local Revenue Office / Tehsildar",
            estimated_cost="Free to ₹50"
        ),
        "caste_cert": DocumentInfo(
            name="Caste Certificate",
            priority=DocPriority.HIGH,
            processing_time_days=30,
            schemes_unlocked=["stand_up_india", "pm_matru_vandana"],  # For SC/ST reservations
            prerequisites=[],
            obtainable_from="District Welfare Office",
            estimated_cost="Free to ₹100"
        ),
        "photo_id": DocumentInfo(
            name="Photo ID (Voter Card / Driving License / Passport)",
            priority=DocPriority.MEDIUM,
            processing_time_days=30,  # If acquiring Voter Card
            schemes_unlocked=["all"],  # Accepted by all schemes
            prerequisites=[],
            obtainable_from="Election Commission / RTO / Passport Office",
            estimated_cost="Free (Voter) to ₹1000+ (Passport)"
        ),
        "school_enrollment": DocumentInfo(
            name="School Enrollment Certificate",
            priority=DocPriority.LOW,
            processing_time_days=1,
            schemes_unlocked=["pm_poshan", "nsp"],
            prerequisites=[],
            obtainable_from="School Principal",
            estimated_cost="Free"
        ),
        "covid_vending_cert": DocumentInfo(
            name="Pre-COVID Street Vending Certificate",
            priority=DocPriority.HIGH,
            processing_time_days=60,  # Can be slow if not on record
            schemes_unlocked=["svaniidhi"],
            prerequisites=[],
            obtainable_from="Municipal Corporation / ULB",
            estimated_cost="Free to ₹500"
        ),
        "disability_cert": DocumentInfo(
            name="Disability Certificate",
            priority=DocPriority.MEDIUM,
            processing_time_days=14,
            schemes_unlocked=["multiple"],  # Unlocks various disability schemes
            prerequisites=[],
            obtainable_from="District Medical Board / Hospital",
            estimated_cost="₹100–500"
        ),
    }
    
    def generate_checklist(self, eligible_scheme_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Generate optimized document checklist for multiple schemes.
        
        Args:
            eligible_scheme_ids: List of scheme IDs user qualifies for
            
        Returns:
            Sorted list of documents with metadata
        """
        # Collect documents needed for all schemes
        docs_needed = {}
        
        for scheme_id in eligible_scheme_ids:
            # Map scheme to documents (this would come from rules.json in production)
            scheme_docs = self._get_documents_for_scheme(scheme_id)
            
            for doc_name in scheme_docs:
                if doc_name not in docs_needed:
                    docs_needed[doc_name] = set()
                docs_needed[doc_name].add(scheme_id)
        
        # Convert to list and score
        checklist = []
        for doc_name, schemes in docs_needed.items():
            if doc_name in self.DOCUMENTS:
                doc_info = self.DOCUMENTS[doc_name]
                
                # Score: more schemes unlocked + faster processing = higher priority
                scheme_score = len(schemes)
                speed_bonus = max(0, 30 - doc_info.processing_time_days)  # Normalize
                
                checklist.append({
                    "document": doc_info.name,
                    "priority": doc_info.priority.value,
                    "priority_label": doc_info.priority.name,
                    "processing_days": doc_info.processing_time_days,
                    "unlocks_schemes": list(schemes),
                    "unlocks_count": len(schemes),
                    "prerequisite_docs": doc_info.prerequisites,
                    "obtainable_from": doc_info.obtainable_from,
                    "estimated_cost": doc_info.estimated_cost,
                    "scheme_score": scheme_score,
                    "speed_bonus": speed_bonus,
                })
        
        # Sort by: (1) priority, (2) speed, (3) schemes unlocked
        checklist.sort(
            key=lambda d: (d['priority'], -d['processing_days'], -d['unlocks_count'])
        )
        
        return checklist
    
    @staticmethod
    def _get_documents_for_scheme(scheme_id: str) -> List[str]:
        """
        Get documents required for a specific scheme.
        In production, this would query rules.json.
        """
        scheme_docs = {
            "pm_kisan": ["aadhaar", "bank_account", "land_records", "photo_id"],
            "mgnrega": ["aadhaar", "address_proof", "photo_id"],
            "pmjay": ["bpl_card", "aadhaar", "photo_id"],
            "pmay_gramin": ["aadhaar", "land_records", "address_proof"],
            "pmay_urban": ["aadhaar", "address_proof"],
            "pm_ujjwala": ["bpl_card", "aadhaar", "address_proof"],
            "pm_jan_dhan": ["aadhaar", "address_proof"],
            "pm_suraksha_bima": ["aadhaar", "bank_account"],
            "pm_jeevan_jyoti": ["aadhaar", "bank_account"],
            "apy": ["aadhaar", "bank_account"],
            "nsp": ["school_enrollment", "income_cert"],
            "pm_matru_vandana": ["aadhaar", "address_proof"],
            "pm_poshan": ["school_enrollment"],
            "stand_up_india": ["aadhaar", "income_cert", "caste_cert"],
            "svaniidhi": ["aadhaar", "covid_vending_cert"],
        }
        
        return scheme_docs.get(scheme_id, [])
    
    def format_checklist_display(self, checklist: List[Dict[str, Any]]) -> str:
        """
        Format checklist for user-friendly display.
        
        Args:
            checklist: From generate_checklist()
            
        Returns:
            Formatted string
        """
        output = ["# 📋 Document Checklist\n"]
        output.append("**Obtain these documents in order. Earlier documents are more critical.**\n")
        
        for i, doc in enumerate(checklist, 1):
            emoji = "🔴" if doc['priority'] == 1 else "🟡" if doc['priority'] == 2 else "🟢"
            
            output.append(f"{emoji} **{i}. {doc['document']}**")
            output.append(f"   - Get from: {doc['obtainable_from']}")
            output.append(f"   - Processing time: {doc['processing_days']} days")
            output.append(f"   - Estimated cost: {doc['estimated_cost']}")
            output.append(f"   - Unlocks {doc['unlocks_count']} scheme(s): {', '.join(doc['unlocks_schemes'])}")
            
            if doc['prerequisite_docs']:
                output.append(f"   - Requires first: {', '.join(doc['prerequisite_docs'])}")
            
            output.append("")
        
        output.append("---")
        total_days = sum(d['processing_days'] for d in checklist)
        output.append(f"**Total time: ~{total_days} days** (can be parallelized)")
        output.append(f"**Total cost: Variable** (most are free or <₹500)")
        
        return "\n".join(output)


# Example usage
if __name__ == "__main__":
    checker = DocChecklist()
    
    # User qualifies for these schemes
    eligible_schemes = ["pm_kisan", "mgnrega", "pmjay", "pm_ujjwala"]
    
    checklist = checker.generate_checklist(eligible_schemes)
    
    print(checker.format_checklist_display(checklist))
    
    print("\n\n=== RAW CHECKLIST DATA ===\n")
    import json
    print(json.dumps(checklist, indent=2))
