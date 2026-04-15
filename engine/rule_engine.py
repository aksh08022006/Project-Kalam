#!/usr/bin/env python3
"""
rule_engine.py — Core eligibility matching with explainable confidence scores.
"""

from dataclasses import dataclass, field as dc_field
from typing import Any, Dict, List, Optional
from enum import Enum


class RuleStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    UNKNOWN = "unknown"


class MatchStatus(Enum):
    FULLY_ELIGIBLE = "FULL"
    PARTIALLY_ELIGIBLE = "PARTIAL"
    NOT_ELIGIBLE = "NO"


@dataclass
class RuleTrace:
    """Single rule evaluation result."""
    field: str
    operator: str
    required_value: Any
    user_value: Optional[Any]
    passed: bool
    reason: str


@dataclass
class RuleEvaluation:
    """Result of evaluating a single rule."""
    field: str
    rule: Dict[str, Any]
    status: RuleStatus
    reason: str
    user_value: Optional[Any] = None


@dataclass
class MatchResult:
    """Result of matching user against a scheme."""
    scheme_id: str
    scheme_name: str
    status: MatchStatus
    confidence_score: float
    rule_trace: List[RuleTrace] = dc_field(default_factory=list)
    ambiguity_flags: List[Dict[str, Any]] = dc_field(default_factory=list)
    triggered_hard_failures: List[RuleEvaluation] = dc_field(default_factory=list)
    triggered_soft_failures: List[RuleEvaluation] = dc_field(default_factory=list)
    explanation: str = ""
    documents_required: List[str] = dc_field(default_factory=list)
    score_breakdown: str = ""


def normalize_boolean(value: Any) -> Optional[bool]:
    """Convert various boolean representations to Python bool."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return True if value == 1 else (False if value == 0 else None)
    if isinstance(value, str):
        n = value.lower().strip()
        if n in ("yes", "y", "true", "t", "1", "haan", "ha", "ji"):
            return True
        if n in ("no", "n", "false", "f", "0", "nahi", "na", "nahin"):
            return False
    return None


class RuleEngine:
    """Evaluates user profiles against scheme eligibility rules."""
    
    def __init__(self, rules_data: List[Dict[str, Any]]):
        self.schemes = {s["scheme_id"]: s for s in rules_data}
    
    def evaluate_rule(self, rule: Dict[str, Any], profile: Dict[str, Any]) -> tuple:
        """Evaluate single rule. Returns (RuleEvaluation, RuleTrace)."""
        field = rule.get("field")
        operator = rule.get("operator")
        rule_value = rule.get("value")
        
        if field not in profile:
            ev = RuleEvaluation(
                field=field, rule=rule, status=RuleStatus.UNKNOWN,
                reason=f"Field '{field}' not provided", user_value=None
            )
            return ev, None
        
        user_value = profile.get(field)
        
        if isinstance(rule_value, bool):
            normalized = normalize_boolean(user_value)
            if normalized is not None:
                user_value = normalized
        
        passed = False
        try:
            if operator == "==":
                passed = user_value == rule_value
            elif operator == "!=":
                passed = user_value != rule_value
            elif operator == "<":
                passed = user_value < rule_value
            elif operator == ">":
                passed = user_value > rule_value
            elif operator == "<=":
                passed = user_value <= rule_value
            elif operator == ">=":
                passed = user_value >= rule_value
            elif operator == "in":
                passed = user_value in rule_value
            elif operator == "not_in":
                passed = user_value not in rule_value
        except TypeError:
            pass
        
        status = RuleStatus.PASSED if passed else RuleStatus.FAILED
        reason = f"{field} {operator} {rule_value}: user has {user_value}"
        
        ev = RuleEvaluation(
            field=field, rule=rule, status=status,
            reason=reason, user_value=user_value
        )
        
        trace = RuleTrace(
            field=field, operator=operator, required_value=rule_value,
            user_value=user_value, passed=passed, reason=reason
        )
        
        return ev, trace
    
    def match_scheme(self, scheme_id: str, profile: Dict[str, Any]) -> MatchResult:
        """Evaluate profile against scheme."""
        if scheme_id not in self.schemes:
            raise ValueError(f"Unknown scheme: {scheme_id}")
        
        scheme = self.schemes[scheme_id]
        hard_f = []
        soft_f = []
        traces = []
        
        for rule in scheme.get("rules", []):
            ev, trace = self.evaluate_rule(rule, profile)
            if trace:
                traces.append(trace)
            if ev.status == RuleStatus.FAILED:
                if rule.get("rule_type") == "hard":
                    hard_f.append(ev)
                else:
                    soft_f.append(ev)
        
        ambig_f = scheme.get("ambiguity_flags", [])
        rules_passed = len([t for t in traces if t.passed])
        total_rules = len(traces)
        
        if hard_f:
            status = MatchStatus.NOT_ELIGIBLE
            score = 0.0
            score_bd = f"{len(hard_f)} hard requirement(s) failed"
            exp = f"Does not qualify: {len(hard_f)} hard requirement(s) not met."
        elif soft_f or ambig_f:
            status = MatchStatus.PARTIALLY_ELIGIBLE
            base = 0.85
            soft_ded = len(soft_f) * 0.05
            ambig_ded = len(ambig_f) * 0.08
            score = max(0.5, base - soft_ded - ambig_ded)
            score_bd = f"{rules_passed} of {total_rules} rules passed. {len(ambig_f)} ambiguity/ies flagged. Score: {score:.2f}"
            exp = f"Partially qualifies: {len(soft_f)} preference(s) not met, {len(ambig_f)} ambiguity/ies flagged."
        else:
            status = MatchStatus.FULLY_ELIGIBLE
            score = 1.0
            score_bd = f"All {total_rules} rules passed. Perfect match: {score:.2f}"
            exp = "Fully qualifies for this scheme."
        
        return MatchResult(
            scheme_id=scheme_id, scheme_name=scheme.get("scheme_name", scheme_id),
            status=status, confidence_score=score, rule_trace=traces,
            ambiguity_flags=ambig_f, triggered_hard_failures=hard_f,
            triggered_soft_failures=soft_f, explanation=exp,
            documents_required=scheme.get("documents_required", []),
            score_breakdown=score_bd
        )
    
    def evaluate_all_schemes(self, profile: Dict[str, Any]) -> List[MatchResult]:
        """Evaluate profile against all schemes."""
        results = [self.match_scheme(sid, profile) for sid in self.schemes]
        results.sort(key=lambda r: (r.status.value != "FULL", r.status.value != "PARTIAL", -r.confidence_score))
        return results
    
    def get_gap_analysis(self, match_result: MatchResult) -> Dict[str, Any]:
        """Generate improvement suggestions for PARTIAL match."""
        return {
            "scheme_id": match_result.scheme_id,
            "scheme_name": match_result.scheme_name,
            "current_status": match_result.status.value,
            "confidence": match_result.confidence_score,
            "score_breakdown": match_result.score_breakdown,
            "hard_failures": [{
                "field": f.field, "required": f.rule.get("value"),
                "user_has": f.user_value, "description": f.rule.get("description", "")
            } for f in match_result.triggered_hard_failures],
            "soft_failures": [{
                "field": f.field, "required": f.rule.get("value"),
                "user_has": f.user_value, "description": f.rule.get("description", "")
            } for f in match_result.triggered_soft_failures],
            "ambiguities": match_result.ambiguity_flags
        }
