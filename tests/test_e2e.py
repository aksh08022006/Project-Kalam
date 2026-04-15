#!/usr/bin/env python3
"""
test_e2e.py — End-to-end conversation tests through /chat endpoint
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"
OUTPUT_FILE = "tests/test_e2e_results.md"

def print_and_log(text, file_obj=None):
    """Print and optionally log to file."""
    print(text)
    if file_obj:
        file_obj.write(text + "\n")

def run_conversation(name: str, messages: list, file_obj=None):
    """Run a complete conversation and return results."""
    print_and_log(f"\n{'='*70}", file_obj)
    print_and_log(f"CONVERSATION: {name}", file_obj)
    print_and_log(f"{'='*70}", file_obj)
    
    session_id = f"test_{int(time.time() * 1000)}"
    scheme_results = {}
    
    for i, message in enumerate(messages, 1):
        print_and_log(f"\n[User {i}]: {message}", file_obj)
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"message": message, "session_id": session_id},
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            reply = data.get("reply", "")
            print_and_log(f"[Bot]: {reply}", file_obj)
            
            # Extract scheme results if present
            if "schemes" in data:
                scheme_results = data["schemes"]
        
        except requests.exceptions.ConnectionError:
            print_and_log("❌ ERROR: Cannot connect to server. Is Flask running on port 5000?", file_obj)
            return None
        except Exception as e:
            print_and_log(f"❌ ERROR: {str(e)}", file_obj)
            return None
    
    print_and_log(f"\n{'─'*70}", file_obj)
    print_and_log("FINAL RESULTS:", file_obj)
    
    if scheme_results:
        eligible_count = len([s for s in scheme_results if s.get("status") == "FULL"])
        partial_count = len([s for s in scheme_results if s.get("status") == "PARTIAL"])
        ineligible_count = len([s for s in scheme_results if s.get("status") == "NO"])
        
        print_and_log(f"  Fully Eligible: {eligible_count}", file_obj)
        print_and_log(f"  Partially Eligible: {partial_count}", file_obj)
        print_and_log(f"  Not Eligible: {ineligible_count}", file_obj)
        
        print_and_log(f"\nTop matches:", file_obj)
        for s in scheme_results[:5]:
            print_and_log(f"  • {s.get('scheme_name', 'Unknown')}: {s.get('status')} (confidence: {s.get('confidence_score', 0):.2f})", file_obj)
        
        return len(scheme_results) >= 2  # Assert at least 2 schemes returned
    
    return False


def main():
    """Run all test conversations."""
    
    print("\n🧪 Starting end-to-end chat tests...")
    print("   Ensure Flask app is running: python interface/app.py")
    print("   Waiting 2 seconds for server readiness...\n")
    time.sleep(2)
    
    # Test if server is available
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except:
        print("❌ Server not running. Start with: python interface/app.py")
        return
    
    with open(OUTPUT_FILE, "w") as f:
        f.write("# Project Kalam — End-to-End Chat Test Results\n\n")
        f.write(f"Test Date: {datetime.now().isoformat()}\n\n")
        
        # Conversation 1: Farmer from UP
        conv1_passed = run_conversation(
            "Farmer from UP with land and bank account",
            [
                "Namaste, main Uttar Pradesh ka kisan hoon",
                "Mere paas 2 acre zameen hai",
                "Mere paas Aadhaar card bhi hai",
                "Aur mere paas bank account bhi hai",
                "Meri annual income around 80,000 rupees hai"
            ],
            f
        )
        
        # Conversation 2: Urban widow in Mumbai
        conv2_passed = run_conversation(
            "Urban widow in Mumbai without house",
            [
                "Main ek widow hoon, Mumbai mein rehti hoon",
                "Mere paas koi apna ghar nahi hai",
                "Mere paas BPL card hai",
                "Mere paas Aadhaar card bhi hai",
                "Meri monthly income around 10,000 rupees hai"
            ],
            f
        )
        
        # Conversation 3: Young student from Bihar, SC category
        conv3_passed = run_conversation(
            "22-year-old SC student from Bihar",
            [
                "Namaste, main Bihar se hoon",
                "Meri age 22 saal hai",
                "Main ek student hoon",
                "Main SC category se hoon",
                "Mere family ki annual income 1,80,000 rupees hai"
            ],
            f
        )
        
        # Summary
        f.write(f"\n{'='*70}\n")
        f.write("SUMMARY\n")
        f.write(f"{'='*70}\n\n")
        f.write(f"Conversation 1 (Farmer): {'✅ PASSED' if conv1_passed else '❌ FAILED'}\n")
        f.write(f"Conversation 2 (Widow): {'✅ PASSED' if conv2_passed else '❌ FAILED'}\n")
        f.write(f"Conversation 3 (Student): {'✅ PASSED' if conv3_passed else '❌ FAILED'}\n\n")
        
        all_passed = conv1_passed and conv2_passed and conv3_passed
        f.write(f"Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}\n")
    
    print(f"\n📝 Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
