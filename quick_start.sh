#!/bin/bash

echo "🚀 Project Kalam - Phase 1 Quick Start"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✅ Python $(python3 --version | cut -d' ' -f2) found"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found - run from project root"
    exit 1
fi

echo "✅ Project directory verified"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Check if scheme data exists
if [ ! -f "data/schemes/extracted_schemes.json" ]; then
    echo "⚠️  Creating sample schemes..."
    mkdir -p data/schemes
    python3 << 'EOF'
import json
import os

sample_schemes = {
    "schemes": [
        {
            "scheme_id": "pm_kisan",
            "scheme_name": "PM Kisan Samman Nidhi",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "category": "agriculture",
            "benefits": ["₹6,000/year direct income support"],
            "eligibility_criteria": {
                "level_1": "agricultural_income",
                "level_2": "rural_farmer",
                "level_3": "landholding_limit"
            },
            "where_to_get_requirements": {
                "Aadhaar": "https://uidai.gov.in/",
                "Land Records": "Your District Revenue Office"
            },
            "contact_info": {
                "helpline": "011-2355-0700",
                "website": "https://pmkisan.gov.in/"
            }
        }
    ]
}

os.makedirs("data/schemes", exist_ok=True)
with open("data/schemes/extracted_schemes.json", "w") as f:
    json.dump(sample_schemes, f, indent=2)
EOF
    echo "✅ Sample schemes created"
fi

# Set Flask environment
export FLASK_APP=interface/app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set"
    echo "   To enable AI features, run:"
    echo "   export ANTHROPIC_API_KEY='sk-your-key-here'"
    echo "   Or set it in .env file"
fi

echo ""
echo "🌐 Starting Project Kalam..."
echo "📊 System Information:"
echo "   - Python: $(python3 --version | cut -d' ' -f2)"
echo "   - Scheme Data: data/schemes/extracted_schemes.json"
echo "   - Port: 5000"
echo "   - URL: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================"
echo ""

# Start Flask app
python3 interface/app.py
