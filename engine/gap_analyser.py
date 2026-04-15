#!/usr/bin/env python3
"""
gap_analyser.py — Analyzes gaps for PARTIAL eligibility matches.

For users who are PARTIAL matches, this module generates actionable guidance:
- What hard requirements are blocking them
- What soft requirements would strengthen their case
- What ambiguities need clarification
- Priority-ordered action list to become fully eligible
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from rule_engine import MatchResult, MatchStatus


@dataclass
class GapItem:
    """Single actionable gap."""
    priority: int  # 1 = most urgent, 3 = nice-to-have
    category: str  # "hard_failure" | "soft_failure" | "ambiguity"
    field: str
    current_value: Any
    required_value: Any
    reason: str
    action: str  # What user should do


class GapAnalyser:
    """Analyzes eligibility gaps for users."""
    
    def analyze_partial_match(self, result: MatchResult, profile: Dict[str, Any]) -> List[GapItem]:
        """
        Analyze gaps for a PARTIAL eligibility match.
        
        Args:
            result: MatchResult from RuleEngine
            profile: User profile dict
            
        Returns:
            List of GapItems, sorted by priority
        """
        if result.status == MatchStatus.FULLY_ELIGIBLE:
            return []  # No gaps
        
        gaps = []
        
        # Hard failures: CRITICAL
        for failure in result.triggered_hard_failures:
            gap = GapItem(
                priority=1,  # Most critical
                category="hard_failure",
                field=failure.field,
                current_value=failure.user_value,
                required_value=failure.rule.get('value'),
                reason=failure.reason,
                action=self._suggest_action_hard_failure(failure)
            )
            gaps.append(gap)
        
        # Soft failures: RECOMMENDED
        for failure in result.triggered_soft_failures:
            gap = GapItem(
                priority=2,  # Recommended
                category="soft_failure",
                field=failure.field,
                current_value=failure.user_value,
                required_value=failure.rule.get('value'),
                reason=failure.reason,
                action=self._suggest_action_soft_failure(failure)
            )
            gaps.append(gap)
        
        # Ambiguities: NEEDS CLARIFICATION
        for i, flag in enumerate(result.ambiguity_flags):
            gap = GapItem(
                priority=3,  # Lowest priority but still important
                category="ambiguity",
                field="<ambiguity>",
                current_value=None,
                required_value=None,
                reason=flag.get('description', ''),
                action=f"Get clarification: {flag.get('issue')}. Contact local welfare office for your state's interpretation."
            )
            gaps.append(gap)
        
        # Sort by priority (1 first)
        gaps.sort(key=lambda g: g.priority)
        
        return gaps
    
    @staticmethod
    def _suggest_action_hard_failure(failure) -> str:
        """Suggest action to fix a hard failure."""
        field = failure.field
        required = failure.rule.get('value')
        operator = failure.rule.get('operator')
        current = failure.user_value
        
        actions = {
            "age": f"You need to be at least {required} years old. Wait {required - current} years, or check if there's an age-exemption for your category.",
            "annual_income": f"Your income {failure.user_value} exceeds the limit of {required}. This scheme targets lower-income households.",
            "has_bank_account": "Open a bank account immediately. Most government schemes require direct benefit transfer (DBT).",
            "has_aadhaar": "Enroll for Aadhaar using your nearest Aadhaar Enrollment Center. It's now mandatory for most schemes.",
            "occupation": f"This scheme is for {required}. Your current occupation ({current}) doesn't qualify.",
            "bpl_card": "Obtain a BPL card from your local municipality or revenue office.",
            "land_owned_acres": f"Land ownership is required. You currently have {current} acres; minimum is > 0.",
            "in_rural_area": "This scheme is for rural areas only. Check if your location qualifies under Census 2011 definitions.",
        }
        
        return actions.get(field, f"Fix '{field}' to meet the requirement: {operator} {required}")
    
    @staticmethod
    def _suggest_action_soft_failure(failure) -> str:
        """Suggest action to improve a soft requirement."""
        field = failure.field
        
        recommendations = {
            "annual_income": "While not disqualifying, lower income strengthens your case. Document all sources.",
            "has_bank_account": "Having a bank account helps with faster fund transfer.",
            "bpl_card": "A BPL card helps prove your economic status even if not strictly required.",
            "land_owned_acres": "Land ownership is preferred. Check if leased land counts in your state.",
        }
        
        return recommendations.get(field, f"Strengthening '{field}' would improve your eligibility case.")
    
    def generate_priority_roadmap(self, gaps: List[GapItem]) -> str:
        """
        Generate a step-by-step action plan to become fully eligible.
        
        Args:
            gaps: List of GapItems
            
        Returns:
            Human-readable action plan
        """
        if not gaps:
            return "No gaps — you're already fully eligible!"
        
        roadmap = ["# Action Plan to Become Fully Eligible\n"]
        
        # Group by priority
        priorities = {1: "🔴 CRITICAL (Must Fix):", 2: "🟡 RECOMMENDED (Strongly Advised):", 3: "🔵 VERIFY (For Clarity):"}
        
        for priority in [1, 2, 3]:
            priority_gaps = [g for g in gaps if g.priority == priority]
            if not priority_gaps:
                continue
            
            roadmap.append(f"\n{priorities[priority]}\n")
            for i, gap in enumerate(priority_gaps, 1):
                roadmap.append(f"{i}. {gap.field.upper()}: {gap.action}")
        
        roadmap.append("\n---\n")
        roadmap.append("**Estimated time:** Critical items typically take 1-2 weeks to fix.\n")
        roadmap.append("**Next step:** Contact your local welfare office for personalized guidance.")
        
        return "\n".join(roadmap)


def format_gap_report(scheme_name: str, profile_summary: str, gaps: List[GapItem], analyzer: GapAnalyser) -> str:
    """
    Format a complete gap analysis report for display.
    
    Args:
        scheme_name: Name of the scheme
        profile_summary: Summary of user's profile
        gaps: List of GapItems
        analyzer: GapAnalyser instance for roadmap generation
        
    Returns:
        Formatted report
    """
    report = [
        f"## Gap Analysis: {scheme_name}\n",
        f"**Your Profile:** {profile_summary}\n",
    ]
    
    if not gaps:
        report.append("✓ No gaps identified — you may be eligible!")
        return "\n".join(report)
    
    # Summary
    hard_count = len([g for g in gaps if g.priority == 1])
    soft_count = len([g for g in gaps if g.priority == 2])
    ambig_count = len([g for g in gaps if g.priority == 3])
    
    report.append(f"**Gap Summary:** {hard_count} critical, {soft_count} recommended, {ambig_count} need clarification\n")
    
    # Roadmap
    report.append(analyzer.generate_priority_roadmap(gaps))
    
    return "\n".join(report)


# Example usage
if __name__ == "__main__":
    import json
    from rule_engine import RuleEngine
    
    # Load rules and test profile
    try:
        with open("data/schemes/rules.json", "r") as f:
            rules_data = json.load(f)
    except FileNotFoundError:
        print("Error: data/schemes/rules.json not found")
        exit(1)
    
    engine = RuleEngine(rules_data)
    
    # Test profile with some gaps
    test_profile = {
        "age": 28,
        "state": "Rajasthan",
        "annual_income": 250000,  # Above PM Kisan limit
        "occupation": "farmer",
        "land_owned_acres": 0,  # No land!
        "has_bank_account": False,  # Missing bank account
        "has_aadhaar": True,
        "in_rural_area": True,
        "bpl_card": False,
    }
    
    # Evaluate PM Kisan
    result = engine.match_scheme("pm_kisan", test_profile)
    
    print(f"Scheme: {result.scheme_name}")
    print(f"Status: {result.status.value}\n")
    
    analyzer = GapAnalyser()
    gaps = analyzer.analyze_partial_match(result, test_profile)
    
    report = format_gap_report(
        result.scheme_name,
        f"Farmer, {test_profile['age']} years, income ₹{test_profile['annual_income']}",
        gaps,
        analyzer
    )
    
    print(report)
