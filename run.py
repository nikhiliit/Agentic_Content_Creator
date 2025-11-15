#!/usr/bin/env python3
"""
Quick launcher for the Content Generator application.

Usage:
    python run.py          # Launch web interface
    python run.py --cli    # Use command line interface
    python run.py --setup  # Run setup wizard
"""

import sys
import subprocess

def main():
    """Launch the appropriate interface based on arguments."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--cli":
            # Launch CLI interface
            print("🚀 Launching Content Generator CLI...")
            # Pass through all additional arguments
            subprocess.run([sys.executable, "src/cli/cli.py"] + sys.argv[2:])
        elif sys.argv[1] == "--setup":
            # Run setup wizard
            print("⚙️  Running Content Generator Setup...")
            subprocess.run([sys.executable, "scripts/setup.py"])
        else:
            print("Usage: python run.py [--cli|--setup]")
            print("  (no args): Launch web interface")
            print("  --cli: Launch command line interface")
            print("  --setup: Run setup wizard")
            sys.exit(1)
    else:
        # Launch web interface (default)
        print("🚀 Launching Content Generator Web Interface...")
        print("📱 Open your browser to http://localhost:7860")
        subprocess.run([sys.executable, "src/web/web_app.py"])

if __name__ == "__main__":
    main()
