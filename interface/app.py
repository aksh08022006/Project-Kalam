#!/usr/bin/env python3
"""
app.py — Flask web server for Project Kalam.

Endpoints:
  GET  /               - Main web interface
  POST /chat          - Chat endpoint (natural language)
  GET  /questions     - Get question for specific level
  POST /filter        - Apply filter and get remaining schemes
  GET  /scheme/<id>   - Get scheme with full details
  GET  /health        - Health check

Session state persists profile fields and tracks which ones are filled.
"""

import json
import os
from typing import Dict, Any, List, Tuple
from datetime import datetime
from anthropic import Anthropic

from flask import Flask, render_template, request, jsonify

# Import engine modules
from engine.rule_engine import RuleEngine
from engine.gap_analyser import GapAnalyser
from engine.doc_checklist import DocChecklist
from engine.question_engine import QuestionEngine

# Initialize Flask app
app = Flask(__name__, template_folder="interface/templates", static_folder="interface/static")
app.secret_key = os.getenv("SECRET_KEY", "dev-key-change-in-production")

# Initialize engines
try:
    with open("data/schemes/rules.json", "r") as f:
        rules_data = json.load(f)
    engine = RuleEngine(rules_data)
    gap_analyser = GapAnalyser()
    doc_checker = DocChecklist()
    
    # Initialize question engine with extracted schemes
    question_engine = QuestionEngine()
    print(f"✓ Question engine initialized with {len(question_engine.all_schemes)} schemes")
except FileNotFoundError as e:
    print(f"Error loading schemes: {e}")
    exit(1)

# Initialize Anthropic client for NL → profile conversion
client = Anthropic()

# Session state storage (in production: use database)
SESSIONS = {}


def get_or_create_session(session_id: str) -> Dict[str, Any]:
    """Get or create session state."""
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "profile": {},
            "uncertain_fields": [],
            "conversation_history": [],
            "profile_complete": False,
            "created_at": datetime.now().isoformat(),
        }
    return SESSIONS[session_id]


def extract_profile_fields(user_message: str, current_profile: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Use Claude API to extract structured profile fields from natural language.
    
    Args:
        user_message: User's message in Hindi/English/Hinglish
        current_profile: Current profile state (for context)
        
    Returns:
        Tuple of (extracted_fields, uncertain_fields)
    """
    
    system_prompt = """You are a profile extraction assistant for Indian welfare schemes.
    
Your task: Extract structured eligibility profile fields from the user's message.
The user may write in Hindi, English, or Hinglish.

Return ONLY valid JSON with this structure:
{
  "extracted_fields": {
    "field_name": value,
    ...
  },
  "uncertain_fields": ["field_name1", "field_name2"],
  "confidence": 0.0-1.0
}

Field types and examples:
- age: integer (18-100)
- state: string (full name or abbreviation)
- occupation: string (farmer/labour/business/govt/student/other)
- annual_income: integer (₹ per year)
- family_size: integer
- land_owned_acres: float
- caste: string (GEN/OBC/SC/ST)
- has_bank_account: boolean
- has_aadhaar: boolean
- is_woman: boolean
- bpl_card: boolean
- in_rural_area: boolean
- is_pregnant: boolean (if woman)
- is_student: boolean

Rules:
1. Only extract fields explicitly mentioned or strongly implied
2. If uncertain (e.g., "small income" but no amount), add to uncertain_fields
3. Never guess — leave field null if unclear
4. For "umar" or "sal", extract as age/annual_income
5. For contradictions, add to uncertain_fields
6. Return confidence: 1.0 if clear, 0.5-0.9 if partial, <0.5 if very unclear"""
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"""Extract profile fields from this message:
"{user_message}"

Current profile context: {json.dumps(current_profile)}

Return JSON only, no explanation."""
                }
            ]
        )
        
        response_text = response.content[0].text
        result = json.loads(response_text)
        
        extracted = result.get("extracted_fields", {})
        uncertain = result.get("uncertain_fields", [])
        
        return extracted, uncertain
    
    except Exception as e:
        print(f"Error extracting profile: {e}")
        return {}, []


def get_next_question(profile: Dict[str, Any], conversation_history: List[Tuple[str, str]]) -> str:
    """
    Decide what question to ask next based on profile completeness.
    
    Prioritization:
    1. Fields that unlock most schemes
    2. Hard requirements before soft preferences
    3. One question at a time, in Hinglish
    """
    
    # Define priority fields and questions
    questions_hinglish = {
        "age": "Aapki umar kitni hai? (How old are you?) [18-100]",
        "state": "Aap kis state mein rehte hain? (Which state are you in?)",
        "occupation": "Aapka kaam kya hai? (What is your occupation?) farmer/labour/business/student/other",
        "annual_income": "Aapke ghar ki saal ki kamai lagbhag kitni hai? (Annual family income?) [approximately ₹]",
        "has_bank_account": "Kya aapka bank account hai? (Do you have a bank account?) haan/nahi",
        "has_aadhaar": "Kya aapke paas Aadhaar card hai? (Do you have Aadhaar?) haan/nahi",
        "is_woman": "Kya aap mahila hain? (Are you a woman?) haan/nahi",
        "land_owned_acres": "Kya aapke paas kheti ki zameen hai? Kitni? (Do you own farmland? How much?)",
        "bpl_card": "Kya aapke paas BPL ya ration card hai? (Do you have BPL/ration card?) haan/nahi",
        "in_rural_area": "Kya aap gaon mein rehte hain ya sheher mein? (Village or city?)",
    }
    
    # Priority order (fields that unlock most schemes)
    priority_order = [
        "has_aadhaar", "has_bank_account", "state", "age", "occupation",
        "annual_income", "is_woman", "land_owned_acres", "bpl_card", "in_rural_area"
    ]
    
    # Find first missing critical field
    for field in priority_order:
        if field not in profile or profile[field] is None:
            return questions_hinglish.get(field, f"Aapke {field} ke baare mein batayein?")
    
    # All fields complete
    return None


def evaluate_profile_completeness(profile: Dict[str, Any]) -> Tuple[bool, float]:
    """
    Check if profile has enough info to evaluate schemes.
    
    Returns:
        Tuple of (is_complete, completeness_percentage)
    """
    essential_fields = [
        "age", "state", "has_aadhaar", "has_bank_account", "occupation"
    ]
    
    filled = sum(1 for f in essential_fields if f in profile and profile[f] is not None)
    completeness = filled / len(essential_fields)
    is_complete = completeness >= 0.8  # 80% completeness sufficient
    
    return is_complete, completeness


@app.route("/", methods=["GET"])
def index():
    """Serve main chat UI."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint.
    
    Request: {message: string, session_id: string}
    Response: {reply: string, session_state: {profile, ...}, results: {schemes: [...]}}
    """
    
    data = request.get_json()
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default")
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
    
    # Get or create session
    session = get_or_create_session(session_id)
    
    # Extract profile fields from user message
    extracted, uncertain = extract_profile_fields(user_message, session["profile"])
    session["profile"].update({k: v for k, v in extracted.items() if v is not None})
    session["uncertain_fields"].extend(uncertain)
    
    # Add to conversation history
    session["conversation_history"].append(("user", user_message))
    
    # Check if profile is complete enough
    profile_complete, completeness = evaluate_profile_completeness(session["profile"])
    
    # Decide on response
    if profile_complete:
        # Evaluate all schemes
        try:
            results = engine.evaluate_all_schemes(session["profile"])
            
            # Generate results response
            reply = f"""✓ **Profile Complete!** ({completeness*100:.0f}% filled)

Aapka profile tayyar ho gaya! Here are the schemes you qualify for:\n\n"""
            
            # Group by status
            full_eligible = [r for r in results if r.status.value == "FULL"]
            partial_eligible = [r for r in results if r.status.value == "PARTIAL"]
            
            if full_eligible:
                reply += f"**🟢 Fully Eligible ({len(full_eligible)} scheme(s)):**\n"
                for r in full_eligible:
                    reply += f"• {r.scheme_name} (Confidence: {r.confidence_score:.0%})\n"
            
            if partial_eligible:
                reply += f"\n**🟡 Almost Eligible ({len(partial_eligible)} scheme(s)):**\n"
                for r in partial_eligible:
                    reply += f"• {r.scheme_name} (Confidence: {r.confidence_score:.0%}) - See details for what's needed\n"
            
            reply += f"\n📋 **Document Checklist:** See the checklist tab for prioritized documents.\n"
            reply += "\n**Next:** Select a scheme for detailed eligibility analysis."
            
            # Format results for client
            scheme_results = []
            for result in results:
                gaps = gap_analyser.analyze_partial_match(result, session["profile"]) if result.status.value != "FULL" else []
                
                scheme_results.append({
                    "scheme_id": result.scheme_id,
                    "scheme_name": result.scheme_name,
                    "status": result.status.value,
                    "confidence": result.confidence_score,
                    "explanation": result.explanation,
                    "documents": result.documents_required,
                    "gaps": [
                        {
                            "priority": gap.priority,
                            "category": gap.category,
                            "field": gap.field,
                            "action": gap.action,
                        } for gap in gaps
                    ]
                })
            
            session["profile_complete"] = True
            session["conversation_history"].append(("assistant", reply))
            
            # Generate document checklist
            eligible_scheme_ids = [r["scheme_id"] for r in scheme_results if r["status"] in ["FULL", "PARTIAL"]]
            doc_checklist = doc_checker.generate_checklist(eligible_scheme_ids)
            
            return jsonify({
                "reply": reply,
                "session_state": {
                    "profile": session["profile"],
                    "profile_complete": True,
                    "completeness": completeness,
                },
                "results": {
                    "schemes": scheme_results,
                    "documents": doc_checklist,
                },
                "status": "complete"
            })
        
        except Exception as e:
            reply = f"Error evaluating schemes: {str(e)}"
            return jsonify({"error": reply}), 500
    
    else:
        # Ask next question
        next_question = get_next_question(session["profile"], session["conversation_history"])
        
        if next_question:
            reply = f"Thanks! {next_question}"
        else:
            reply = "I have enough info. Evaluating schemes..."
        
        session["conversation_history"].append(("assistant", reply))
        
        return jsonify({
            "reply": reply,
            "session_state": {
                "profile": session["profile"],
                "profile_complete": False,
                "completeness": completeness,
            },
            "status": "collecting"
        })


@app.route("/session/<session_id>", methods=["GET"])
def get_session(session_id: str):
    """Get current session state."""
    session = get_or_create_session(session_id)
    return jsonify(session)


# ====== NEW PHASE 1 ENDPOINTS ======

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "schemes_loaded": len(question_engine.all_schemes),
        "version": "1.0.0",
        "phase": "Phase 1"
    })


@app.route("/questions", methods=["GET"])
def get_question():
    """Get question for a specific level"""
    try:
        level = request.args.get("level", 1, type=int)
        
        if level < 1 or level > 7:
            return jsonify({
                "error": "Invalid level (1-7)"
            }), 400
        
        from engine.question_engine import QuestionLevel
        level_map = {
            1: QuestionLevel.LEVEL_1,
            2: QuestionLevel.LEVEL_2,
            3: QuestionLevel.LEVEL_3,
            4: QuestionLevel.LEVEL_4,
            5: QuestionLevel.LEVEL_5,
            6: QuestionLevel.LEVEL_6,
            7: QuestionLevel.LEVEL_7
        }
        
        question = question_engine.get_question(level_map[level])
        
        return jsonify({
            "level": level,
            "question": question.question_text,
            "options": question.options,
            "help_text": question.help_text,
            "multiple_select": question.multiple_select
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


@app.route("/filter", methods=["POST"])
def apply_filter():
    """Apply filter and get remaining schemes count"""
    try:
        data = request.json
        level = data.get("level", 1)
        answers = data.get("answers", [])
        
        if not isinstance(answers, list):
            answers = [answers]
        
        from engine.question_engine import QuestionLevel
        level_map = {
            1: QuestionLevel.LEVEL_1,
            2: QuestionLevel.LEVEL_2,
            3: QuestionLevel.LEVEL_3,
            4: QuestionLevel.LEVEL_4,
            5: QuestionLevel.LEVEL_5,
            6: QuestionLevel.LEVEL_6
        }
        
        if level not in level_map:
            return jsonify({"error": f"Invalid level: {level}"}), 400
        
        remaining = question_engine.apply_filter(level_map[level], answers)
        
        return jsonify({
            "level": level,
            "answers": answers,
            "schemes_remaining": remaining,
            "next_level": level + 1 if level < 6 else 7,
            "message": f"✓ {remaining} schemes match your criteria"
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


@app.route("/scheme/<scheme_id>", methods=["GET"])
def get_scheme_details(scheme_id):
    """Get full scheme details with requirements and where-to-get"""
    try:
        # Find scheme in database
        scheme = None
        for s in question_engine.all_schemes:
            if s.get("scheme_id") == scheme_id:
                scheme = s
                break
        
        if not scheme:
            return jsonify({
                "error": f"Scheme {scheme_id} not found"
            }), 404
        
        details = question_engine.get_scheme_with_requirements(scheme)
        return jsonify(details)
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


@app.route("/schemes", methods=["GET"])
def list_schemes():
    """List all available schemes with basic info"""
    try:
        schemes_summary = []
        for scheme in question_engine.all_schemes:
            schemes_summary.append({
                "id": scheme.get("scheme_id"),
                "name": scheme.get("scheme_name"),
                "category": scheme.get("category"),
                "ministry": scheme.get("ministry"),
                "benefits": scheme.get("benefits", [])[:1]  # First benefit
            })
        
        return jsonify({
            "total_schemes": len(schemes_summary),
            "schemes": schemes_summary
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "schemes_loaded": len(engine.schemes)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
