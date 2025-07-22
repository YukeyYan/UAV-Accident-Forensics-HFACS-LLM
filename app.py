"""
Hugging Face Spaces Entry Point for ASRS UAV Incident Analysis System
This file serves as the entry point for deployment on Hugging Face Spaces
"""

import streamlit as st
import os

# Set page configuration first
st.set_page_config(
    page_title="ASRS UAV Incident Intelligence Analysis System",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-username/uav-incident-analysis',
        'Report a bug': 'https://github.com/your-username/uav-incident-analysis/issues',
        'About': """
        # ASRS UAV Incident Intelligence Analysis System
        
        A professional aviation safety analysis tool using:
        - 🤖 AI-powered incident analysis
        - 📋 HFACS 8.0 human factors framework
        - 🔗 Causal relationship mapping
        - 📊 Professional investigation reports
        
        Built with ❤️ using Streamlit and OpenAI GPT-4
        """
    }
)

# Import and run the main application
try:
    from streamlit_app import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    st.error("❌ Application modules not found. Please check the deployment configuration.")
    st.error(f"Import error: {str(e)}")
    
    st.info("🔧 This appears to be a deployment issue. Please check:")
    st.code("""
    1. All Python files are present
    2. requirements.txt includes all dependencies  
    3. File paths are correctly configured
    4. Environment variables are set
    """)
    
except Exception as e:
    st.error("❌ An unexpected error occurred while starting the application.")
    st.error(f"Error details: {str(e)}")
    
    st.info("🆘 If you're seeing this error, please:")
    st.code("""
    1. Check the application logs
    2. Verify your OpenAI API key is configured
    3. Ensure all dependencies are installed
    4. Contact support if the issue persists
    """)