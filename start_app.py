#!/usr/bin/env python3

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import and run the app
from interface.app import app

if __name__ == '__main__':
    print("🚀 Starting Project Kalam...")
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
