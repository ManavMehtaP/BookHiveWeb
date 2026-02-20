#!/usr/bin/env python3
"""
Test script for analytics functionality
Run this to verify charts are generated correctly
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from analytics import generate_all_charts
    print("Testing Analytics Module...")
    
    # Generate all charts
    charts = generate_all_charts()
    
    if charts:
        print("Charts generated successfully!")
        for chart_name, chart_path in charts.items():
            if chart_path and os.path.exists(chart_path):
                size = os.path.getsize(chart_path)
                print(f"   {chart_name}: {chart_path} ({size} bytes)")
            else:
                print(f"   {chart_name}: Failed to generate")
    else:
        print("No charts generated - check if booking data exists")
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure matplotlib and seaborn are installed:")
    print("pip install matplotlib seaborn")
except Exception as e:
    print(f"Error: {e}")
    print("Check database connection and data availability")
