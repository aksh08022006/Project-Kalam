#!/usr/bin/env python3
"""
test_edge_cases.py — Runs all 10 adversarial test profiles through the RuleEngine.

For each profile, documents:
1. What the engine returned
2. What the expected result should be
3. Whether the engine succeeded, failed, or correctly flagged ambiguity
4. Root cause analysis of any failures
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

from rule_engine import RuleEngine, MatchStatus


def load_test_profiles() -> List[Dict[str, Any]]:
    """Load test profiles from JSON."""
    with open("data/edge_cases/test_profiles.json", "r") as f:
        return json.load(f)


def load_rules() -> List[Dict[str, Any]]:
    """Load scheme rules from JSON."""
    with open("data/schemes/rules.json", "r") as f:
        return json.load(f)


def run_test(profile_data: Dict[str, Any], engine: RuleEngine, output: List[str]):
    """
    Run a single test profile through the engine.
    
    Args:
        profile_data: Test profile definition
        engine: Initialized RuleEngine
        output: List to accumulate output lines
    """
    test_id = profile_data.get("id")
    name = profile_data.get("name")
    description = profile_data.get("description")
    profile = profile_data.get("profile", {})
    expected = profile_data.get("expected_result", {})
    focus = profile_data.get("test_focus")
    
    output.append(f"\n{'='*70}")
    output.append(f"TEST: {test_id} — {name}")
    output.append(f"{'='*70}")
    output.append(f"Description: {description}")
    output.append(f"Focus: {focus}\n")
    
    # Run engine
    try:
        results = engine.evaluate_all_schemes(profile)
    except Exception as e:
        output.append(f"❌ ENGINE ERROR: {e}")
        return
    
    # Check results against expectations
    expected_schemes = expected.get("schemes", {})
    
    output.append("ENGINE RESULTS:")
    for result in results:
        scheme_id = result.scheme_id
        expected_status = None
        expected_note = ""
        
        if scheme_id in expected_schemes:
            expected_info = expected_schemes[scheme_id]
            expected_status = expected_info.get("status")
            expected_note = expected_info.get("note", "")
        
        output.append(f"\n  {result.scheme_name}")
        output.append(f"    Status: {result.status.value} (Confidence: {result.confidence_score:.2f})")
        output.append(f"    {result.explanation}")
        
        if expected_status:
            if expected_status == "AMBIGUOUS":
                output.append(f"    ✓ CORRECTLY FLAGGED AS AMBIGUOUS: {expected_note}")
                if result.ambiguity_flags:
                    output.append(f"      Flags: {len(result.ambiguity_flags)} ambiguity/ies detected")
            elif expected_status in ["FULL", "PARTIAL", "NO"]:
                actual_status = result.status.value
                if actual_status == expected_status:
                    output.append(f"    ✓ CORRECT: {expected_note}")
                else:
                    output.append(f"    ❌ INCORRECT: Expected {expected_status}, got {actual_status}")
                    output.append(f"       Expected: {expected_note}")
                    
                    # Diagnose failure
                    output.append(f"       Diagnosis:")
                    if result.triggered_hard_failures:
                        output.append(f"         - Hard failures: {len(result.triggered_hard_failures)}")
                        for failure in result.triggered_hard_failures:
                            output.append(f"           • {failure.field}: {failure.reason}")
                    if result.triggered_soft_failures:
                        output.append(f"         - Soft failures: {len(result.triggered_soft_failures)}")
                    if result.ambiguity_flags:
                        output.append(f"         - Ambiguities: {len(result.ambiguity_flags)}")
    
    output.append(f"\n{'─'*70}")


def generate_report(test_results: List[Dict[str, Any]]) -> str:
    """
    Generate summary report of all tests.
    
    Args:
        test_results: Results from all tests
        
    Returns:
        Summary report string
    """
    report = ["\n", "="*70, "TEST SUMMARY", "="*70]
    
    ambiguity_tests = len([t for t in test_results if "AMBIGUOUS" in t.get("focus", "")])
    edge_tests = len(test_results)
    
    report.append(f"Total edge case tests: {edge_tests}")
    report.append(f"Tests focusing on ambiguities: {ambiguity_tests}")
    report.append(f"Tests focusing on exclusion/barriers: {edge_tests - ambiguity_tests}")
    
    report.append("\nKey insights:")
    report.append("1. AMBIGUITY DETECTION: Engine should flag conflicting/unclear rules")
    report.append("2. HARD FAILURES: Engine should clearly explain hard requirement failures")
    report.append("3. PREREQUISITE AWARENESS: Engine should hint at prerequisite schemes")
    report.append("4. STATE/CONTEXT SENSITIVITY: Engine should note jurisdiction-specific rules")
    
    return "\n".join(report)


def main():
    """Main test runner."""
    print("Loading test data...")
    
    try:
        test_profiles = load_test_profiles()
        rules_data = load_rules()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Initialize engine
    engine = RuleEngine(rules_data)
    
    # Run all tests
    output = []
    output.append("PROJECT KALAM — EDGE CASE TEST REPORT")
    output.append(f"Total schemes in engine: {len(rules_data)}")
    output.append(f"Total edge case tests: {len(test_profiles)}\n")
    
    for profile_data in test_profiles:
        run_test(profile_data, engine, output)
    
    # Add summary
    output.append(generate_report(test_profiles))
    
    # Print and save
    full_report = "\n".join(output)
    print(full_report)
    
    # Save report
    with open("logs/edge_case_test_report.txt", "w") as f:
        f.write(full_report)
    
    print(f"\n✓ Report saved to logs/edge_case_test_report.txt")


if __name__ == "__main__":
    main()
