#!/usr/bin/env python3
"""
Content Generator - Main entry point for Hugging Face Spaces

This root-level app.py imports and runs the web interface from src/web/web_app.py
for compatibility with HF Spaces deployment.
"""

# Import and run the web application
from src.web.web_app import create_demo

if __name__ == "__main__":
    # Create and launch the Gradio app
    demo = create_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(__import__("os").getenv("PORT", 7860)),
        show_error=True,
        share=False  # Disable public sharing for production
    )
