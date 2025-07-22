"""
Multi-language Internationalization Support Module
English-only version for streamlined interface
"""

# English translations dictionary
TRANSLATIONS = {
    'en': {
        # Page titles
        'page_title': 'ASRS UAV Incident Intelligence Analysis System',
        'page_icon': '🚁',
        'main_header': '🚁 ASRS UAV Incident Intelligence Analysis System',
        
        # Sidebar
        'system_config': '⚙️ System Configuration',
        'select_ai_model': '🤖 Select AI Model',
        'model_help': 'gpt-4o provides higher quality analysis, gpt-4o-mini responds faster',
        'select_function_page': 'Select Function Page',
        'language_setting': '🌐 Language Setting',
        
        # Function page options
        'system_overview': 'System Overview',
        'data_management': 'Data Management',
        'asrs_smart_report': '🎯 ASRS Smart Report',
        'causal_analysis': '🔗 Causal Analysis',
        'professional_investigation': '🔬 Professional Investigation',
        'llm_expert_analysis': 'LLM Expert Analysis',
        'hfacs_analysis': 'HFACS Analysis',
        'smart_report_submission': 'Smart Report Submission',
        
        # System status
        'data_loaded': '✅ Historical data loaded',
        'data_not_loaded': '⚠️ Please load historical data in Data Management page first',
        
        # System overview page
        'system_overview_title': '📊 System Overview',
        'system_goal': '🎯 System Goal',
        'system_goal_desc': '''Based on ASRS data, using LLM technology to provide:
- 🤖 Smart form filling
- 🧠 Expert-level incident analysis
- 📋 HFACS 8.0 human factors identification
- 📊 Professional analysis reports''',
        'core_functions': '✨ Core Functions',
        'core_functions_desc': '''🎯 **ASRS Smart Report**: True AI intelligent reporting system
🔗 **Causal Analysis**: Intelligent causal relationship diagram generation
🔬 **Professional Investigation**: Multi-dimensional professional analysis
📋 **HFACS Analysis**: Human factors analysis''',
        'quick_start': '🚀 Quick Start',
        'quick_start_desc': '''1. Select "🎯 ASRS Smart Report"
2. Enter detailed incident narrative
3. Click "🤖 AI Smart Extraction"
4. Review and complete the report''',
        
        # Data management
        'data_management_title': '📂 Data Management',
        'load_historical_data': '📊 Load ASRS Historical Data',
        'upload_csv_file': 'Upload ASRS CSV file',
        'csv_file_help': 'Please upload ASRS UAV incident data CSV file',
        'load_data_button': '🚀 Load Data',
        'loading_data': '⏳ Loading data...',
        'data_loaded_success': '✅ Data loaded successfully!',
        'total_records': 'Total records',
        'data_preview': '📋 Data Preview',
        'no_file_uploaded': '⚠️ Please upload a CSV file first',
        
        # Smart report
        'asrs_smart_report_title': '🎯 ASRS Smart Report - Next Generation AI Analysis',
        'incident_description': '📝 Incident Description',
        'incident_description_help': 'Please describe the incident in detail, including time, location, aircraft type, weather conditions, personnel involved, sequence of events, etc.',
        'ai_extraction': '🤖 AI Smart Extraction',
        'ai_extraction_help': 'Use AI to automatically identify and extract key information from the narrative',
        'completeness_assessment': '📊 Completeness Assessment',
        'analysis_target_report': '📋 Analysis Target Report',
        
        # Analysis results
        'risk_assessment': 'Risk Assessment',
        'root_cause_analysis': 'Root Cause Analysis',
        'contributing_factors': 'Contributing Factors',
        'recommendations': 'Recommendations',
        'preventive_measures': 'Preventive Measures',
        'similar_cases': 'Similar Cases',
        'confidence': 'Confidence',
        'analysis_timestamp': 'Analysis Timestamp',
        
        # Causal analysis
        'causal_analysis_title': '🔗 Professional Incident Causal Analysis',
        'causal_analysis_results': '🎯 Causal Analysis Results',
        'ai_causal_analysis': '🤖 AI Causal Analysis',
        'causal_confirmation': 'Causal Analysis Confirmation',
        'confirm_causal_analysis': 'Would you like to jump to Causal Analysis?',
        'yes_go_causal_analysis': 'Yes, Go to Causal Analysis',
        
        # HFACS analysis
        'hfacs_analysis_title': '📋 HFACS 8.0 Human Factors Analysis',
        'hfacs_tree_visualization': '🌳 HFACS Four-Layer 18-Category Tree Visualization',
        'hfacs_classification_results': 'HFACS Classification Results',
        'hfacs_report_title': 'HFACS Analysis Report',
        'primary_human_factors': 'Primary Human Factors',
        'improvement_recommendations': 'Improvement Recommendations',
        
        # Professional investigation
        'professional_investigation_title': '🔬 Professional Incident Investigation',
        'investigation_report': 'Investigation Report',
        'expert_analysis_summary': 'Expert Analysis Summary',
        
        # Common terms
        'analysis': 'Analysis',
        'evidence': 'Evidence',
        'excellent': 'Excellent',
        'good': 'Good',
        'needs_improvement': 'Needs Improvement',
        'high': 'High',
        'medium': 'Medium',
        'low': 'Low',
        'yes': 'Yes',
        'no': 'No',
        'error': 'Error',
        'warning': 'Warning',
        'success': 'Success',
        'loading': 'Loading',
        'complete': 'Complete',
        'processing': 'Processing',
        'analysis_time': 'Analysis Time',
        'summary': 'Summary',
        'details': 'Details',
        'report': 'Report',
        'data': 'Data',
        'results': 'Results',
        'information': 'Information',
        'description': 'Description',
        'narrative': 'Narrative',
        'incident': 'Incident',
        'accident': 'Accident',
        'safety': 'Safety',
        'aviation': 'Aviation',
        'uav': 'UAV',
        'drone': 'Drone',
        'pilot': 'Pilot',
        'operator': 'Operator',
        'weather': 'Weather',
        'location': 'Location',
        'altitude': 'Altitude',
        'date': 'Date',
        'time': 'Time',
        'phase': 'Phase',
        'mission': 'Mission',
        'equipment': 'Equipment',
        'system': 'System',
        'procedure': 'Procedure',
        'training': 'Training',
        'communication': 'Communication',
        'coordination': 'Coordination',
        'supervision': 'Supervision',
        'management': 'Management',
        'organization': 'Organization',
        'culture': 'Culture',
        'policy': 'Policy',
        'resource': 'Resource',
        'direct_cause': 'Direct Cause',
        'contributing_cause': 'Contributing Factor',
        'enabling_condition': 'Enabling Condition'
    }
}

def get_text(key: str, language: str = 'en') -> str:
    """
    Get translated text for given key and language
    
    Args:
        key: Translation key
        language: Language code (only 'en' supported now)
        
    Returns:
        Translated text or key if not found
    """
    # Always return English since we removed Chinese support
    return TRANSLATIONS.get('en', {}).get(key, key)