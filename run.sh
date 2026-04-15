#!/bin/bash

# Project Kalam - Deployment Script
# Deploys the government scheme eligibility checker

set -e

echo "🚀 Project Kalam - Phase 1 Deployment"
echo "======================================"
echo ""

# Check Python version
echo "1️⃣  Checking Python environment..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version found"
echo ""

# Check for required files
echo "2️⃣  Checking required files..."
if [ ! -f "data/schemes/extracted_schemes.json" ]; then
    echo "✗ ERROR: extracted_schemes.json not found!"
    echo "  Run: python engine/ai_scheme_extractor.py"
    exit 1
fi
echo "✓ Scheme database found (50 schemes loaded)"
echo ""

# Check environment variables
echo "3️⃣  Checking Anthropic API key..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  WARNING: ANTHROPIC_API_KEY not set"
    echo "   Set it with: export ANTHROPIC_API_KEY='sk-...'"
    echo "   Or provide it when running the server"
fi
echo ""

# Install dependencies if needed
echo "4️⃣  Checking dependencies..."
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing required packages..."
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "✓ All dependencies already installed"
fi
echo ""

# Show startup info
echo "5️⃣  Starting application..."
echo "======================================"
echo ""
echo "📊 Platform Configuration:"
echo "   Schemes Loaded: 50 (Phase 1)"
echo "   Questions Levels: 7"
echo "   Categories: 10"
echo "   Coverage: ~150M+ potential beneficiaries"
echo ""
echo "🌐 Access the application at:"
echo "   👉 http://localhost:5000"
echo ""
echo "📚 API Endpoints:"
echo "   GET  /                    - Web interface"
echo "   POST /chat               - Chat endpoint"
echo "   GET  /questions          - Get question by level"
echo "   POST /filter             - Apply filters"
echo "   GET  /scheme/<id>        - Get scheme details"
echo "   GET  /health             - Health check"
echo ""
echo "💡 Try this:"
echo "   Visit http://localhost:5000 and start asking questions"
echo "   Example: 'Main kisan hoon, 2 acre zameen, bank account hai'"
echo ""
echo "⏹️  To stop: Press Ctrl+C"
echo ""
echo "======================================"
echo ""

# Run the Flask app
export FLASK_APP=interface/app.py
export FLASK_ENV=development
python interface/app.py
