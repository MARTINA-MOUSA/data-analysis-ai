"""
Main Streamlit Application Entry Point
"""
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from front.dashboard import Dashboard

if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.render()

