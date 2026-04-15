#!/usr/bin/env python3
"""
Simple startup for Project Kalam Phase 1
"""
import sys
import os
import json

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Flask
from flask import Flask, render_template, request, jsonify

# Create app
app = Flask(__name__, template_folder="interface/templates", static_folder="interface/static")
app.secret_key = os.getenv("SECRET_KEY", "dev-key")

# Load schemes
schemes = []
try:
    with open("data/schemes/extracted_schemes.json", "r") as f:
        data = json.load(f)
        schemes = data.get("schemes", [])
    print(f"✅ Loaded {len(schemes)} schemes")
except Exception as e:
    print(f"⚠️  Could not load schemes: {e}")

# Routes
@app.route('/')
def index():
    return jsonify({"message": "Project Kalam Phase 1 API", "schemes": len(schemes)})

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "schemes_loaded": len(schemes),
        "phase": "Phase 1"
    })

@app.route('/schemes')
def list_schemes():
    return jsonify({
        "total": len(schemes),
        "schemes": schemes
    })

@app.route('/scheme/<scheme_id>')
def get_scheme(scheme_id):
    for scheme in schemes:
        if scheme.get("scheme_id") == scheme_id:
            return jsonify(scheme)
    return jsonify({"error": f"Scheme {scheme_id} not found"}), 404

# Main
if __name__ == '__main__':
    print("🚀 Project Kalam - Phase 1")
    print(f"📊 Schemes Loaded: {len(schemes)}")
    print("🌐 Starting server on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
