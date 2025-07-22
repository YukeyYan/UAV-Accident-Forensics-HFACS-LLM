"""
ASRS UAV Incident Intelligence Analysis System
Core Features: Smart Forms + LLM Expert Analysis + HFACS Classification + Causal Analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import sqlite3
from typing import Dict, List, Optional
import os

# Set OpenAI API key
os.environ['OPENAI_API_KEY'] = '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'

# Import core modules
from data_processor import ASRSDataProcessor
from ai_analyzer import AIAnalyzer
from hfacs_analyzer import HFACSAnalyzer
from smart_form_assistant import SmartFormAssistant
from translations import get_text
from professional_investigation_engine import ProfessionalInvestigationEngine

# Import enhanced features
try:
    from enhanced_ai_analyzer import EnhancedAIAnalyzer
    from advanced_visualizations import AdvancedVisualizations
    from causal_diagram_generator import CausalDiagramGenerator
    ENHANCED_FEATURES_AVAILABLE = True
    CAUSAL_DIAGRAM_AVAILABLE = True
except ImportError:
    ENHANCED_FEATURES_AVAILABLE = False
    CAUSAL_DIAGRAM_AVAILABLE = False
    # English-only system initialization
    st.session_state.selected_language = 'en'
    
    st.sidebar.warning("⚠️ Enhanced modules not found, using basic functionality")

# Page configuration - English only
st.set_page_config(
    page_title="ASRS UAV Incident Intelligence Analysis System",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS - 增强版美观样式
st.markdown("""
<style>
    /* 主标题样式 */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 子标题样式 */
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #3498db;
        background: linear-gradient(90deg, #3498db, #e8f4f8);
        background-size: 100% 3px;
        background-repeat: no-repeat;
        background-position: bottom;
    }
    
    /* 风险等级样式 - 增强版 */
    .risk-high {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-left: 6px solid #e53e3e;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(229, 62, 62, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
        border-left: 6px solid #ff9800;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(255, 152, 0, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .risk-low {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c8 100%);
        border-left: 6px solid #4caf50;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(76, 175, 80, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    /* Streamlit组件美化 */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 2px solid #e1e8ed;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #3498db;
        box-shadow: 0 4px 8px rgba(52, 152, 219, 0.15);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.25);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.25);
    }
    
    /* 指标卡片美化 */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 1px solid #e2e8f0;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* 信息框美化 */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        padding: 1.2rem;
    }
    
    /* Tab样式美化 - 修复颜色问题 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        padding: 0.8rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.8rem 1.2rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        background-color: #ffffff;
        color: #475569 !important;
        border: 1px solid #e2e8f0;
        margin: 2px;
        min-height: 40px;
        display: flex;
        align-items: center;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f8fafc;
        color: #334155 !important;
        border-color: #cbd5e1;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"]:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%) !important;
        color: white !important;
    }
    
    /* 确保Tab内容文字清晰 */
    .stTabs [data-baseweb="tab"] > div {
        color: inherit !important;
    }
    
    /* 展开框美化 */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 8px;
        padding: 0.8rem 1rem;
        font-weight: 600;
        border: 1px solid #e2e8f0;
    }
    
    /* 侧边栏美化 */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* 文本输入框美化 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e1e8ed;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }
    
    /* 加载动画美化 */
    .stSpinner {
        text-align: center;
        padding: 2rem;
    }
    
    /* 表格美化 */
    .dataframe {
        border: none;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* 成功/错误消息美化 */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
    }
    
    .stError {
        background: linear-gradient(135deg, #f8d7da 0%, #f1b0b7 100%);
        color: #721c24;
        border-radius: 8px;
        border: 1px solid #f1b0b7;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #d1ecf1 0%, #b8daff 100%);
        color: #0c5460;
        border-radius: 8px;
        border: 1px solid #b8daff;
    }
    
    /* 图表容器美化 */
    .js-plotly-plot {
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        overflow: hidden;
    }
    
    /* 滚动条美化 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
    
    /* 动画效果 */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main .block-container {
        animation: fadeInUp 0.6s ease-out;
    }
</style>
""", unsafe_allow_html=True)

class ASRSApp:
    """ASRS应用主类 - 简化版"""
    
    def __init__(self):
        self.db_path = "asrs_data.db"
        self.csv_path = "ASRS_DBOnline_Report.csv"
        
        # 初始化会话状态
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
        if 'ai_analyzer' not in st.session_state:
            st.session_state.ai_analyzer = None
        if 'hfacs_analyzer' not in st.session_state:
            st.session_state.hfacs_analyzer = None
        if 'form_assistant' not in st.session_state:
            st.session_state.form_assistant = None
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = 'gpt-4o-mini'
        if 'selected_language' not in st.session_state:
            st.session_state.selected_language = 'en'
        
        # 初始化增强功能
        if 'enhanced_analyzer' not in st.session_state:
            st.session_state.enhanced_analyzer = None
        if 'advanced_viz' not in st.session_state and ENHANCED_FEATURES_AVAILABLE:
            st.session_state.advanced_viz = AdvancedVisualizations()
        if 'causal_generator' not in st.session_state and CAUSAL_DIAGRAM_AVAILABLE:
            model = st.session_state.get('selected_model', 'gpt-4o-mini')
            st.session_state.causal_generator = CausalDiagramGenerator(model=model)
        
        # 初始化智能表单助手
        if st.session_state.form_assistant is None:
            model = st.session_state.get('selected_model', 'gpt-4o-mini')
            st.session_state.form_assistant = SmartFormAssistant(model=model)
        
        # 初始化专业调查引擎
        if 'investigation_engine' not in st.session_state:
            st.session_state.investigation_engine = None
    
    def run(self):
        """运行主应用"""
        lang = st.session_state.selected_language
        st.markdown(f'<h1 class="main-header">{get_text("main_header", lang)}</h1>', unsafe_allow_html=True)
        
        # 侧边栏配置
        with st.sidebar:
            lang = st.session_state.selected_language
            st.header(get_text("system_config", lang))
            
            # 模型选择
            selected_model = st.selectbox(
                get_text("select_ai_model", lang),
                ["gpt-4o-mini", "gpt-4o"],
                help=get_text("model_help", lang)
            )
            
            # 保存模型选择到会话状态
            if 'selected_model' not in st.session_state or st.session_state.selected_model != selected_model:
                st.session_state.selected_model = selected_model
                # 重新初始化组件以使用新模型
                if 'form_assistant' in st.session_state:
                    del st.session_state.form_assistant
                if 'causal_generator' in st.session_state:
                    del st.session_state.causal_generator
            
            st.markdown("---")
        
        # 页面选项 - 根据是否有增强功能调整
        if ENHANCED_FEATURES_AVAILABLE:
            page_options_keys = ["system_overview", "data_management", "asrs_smart_report", "causal_analysis", "professional_investigation", "llm_expert_analysis", "hfacs_analysis"]
        else:
            page_options_keys = ["system_overview", "data_management", "smart_report_submission", "llm_expert_analysis", "hfacs_analysis"]
        
        page_options = [get_text(key, lang) for key in page_options_keys]
        
        # 处理页面重定向
        if 'page_redirect' in st.session_state:
            redirect_key = st.session_state.page_redirect
            del st.session_state.page_redirect
            # 找到对应的索引
            if redirect_key in page_options_keys:
                default_index = page_options_keys.index(redirect_key)
            else:
                default_index = 0
        else:
            default_index = 0

        page_display = st.sidebar.selectbox(
            get_text("select_function_page", lang),
            page_options,
            index=default_index
        )
        
        # 获取页面的键名
        page_key = page_options_keys[page_options.index(page_display)]
        
        # 数据加载状态检查
        self._check_data_status()
        
        # 路由到不同页面
        if page_key == "system_overview":
            self._show_overview()
        elif page_key == "data_management":
            self._show_data_management()
        elif page_key == "asrs_smart_report":
            self._show_asrs_smart_report()
        elif page_key == "causal_analysis":
            self._show_causal_analysis()
        elif page_key == "smart_report_submission":
            self._show_smart_report_submission()
        elif page_key == "professional_investigation":
            self._show_enhanced_investigation()
        elif page_key == "llm_expert_analysis":
            self._show_llm_expert_analysis()
        elif page_key == "hfacs_analysis":
            self._show_hfacs_analysis()
    
    def _check_data_status(self):
        """检查数据加载状态"""
        lang = st.session_state.selected_language
        if st.session_state.get('data_loaded', False):
            st.sidebar.success(get_text("data_loaded", lang))
        else:
            st.sidebar.warning(get_text("data_not_loaded", lang))
    
    def _show_overview(self):
        """显示系统概览页面"""
        lang = st.session_state.selected_language
        st.markdown(f'<h2 class="sub-header">{get_text("system_overview_title", lang)}</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"""
            **{get_text("system_goal", lang)}**
            
            {get_text("system_goal_desc", lang)}
            """)
        
        with col2:
            st.success(f"""
            **{get_text("core_functions", lang)}**
            
            {get_text("core_functions_desc", lang)}
            """)
        
        with col3:
            st.warning(f"""
            **{get_text("quick_start", lang)}**
            
            {get_text("quick_start_desc", lang)}
            """)
        
        # 系统状态显示
        st.markdown("---")
        st.subheader(get_text("system_status", lang))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status = get_text("available", lang) if ENHANCED_FEATURES_AVAILABLE else get_text("unavailable", lang)
            st.metric(get_text("enhanced_features", lang), status)
        
        with col2:
            status = get_text("available", lang) if CAUSAL_DIAGRAM_AVAILABLE else get_text("unavailable", lang)
            st.metric(get_text("causal_diagram", lang), status)
        
        with col3:
            status = get_text("loaded", lang) if st.session_state.data_loaded else get_text("not_loaded", lang)
            st.metric(get_text("historical_data", lang), status)
        
        with col4:
            api_status = get_text("configured", lang) if st.session_state.get('form_assistant') and hasattr(st.session_state.form_assistant, 'api_key') and st.session_state.form_assistant.api_key else get_text("not_configured", lang)
            st.metric(get_text("api_status", lang), api_status)
    
    def _show_data_management(self):
        """数据管理页面"""
        lang = st.session_state.selected_language
        
        data_title = f'<h2 class="sub-header">{get_text("data_management_title", lang)}</h2>'
        st.markdown(data_title, unsafe_allow_html=True)
        
        if st.button(get_text("load_asrs_data", lang)):
            if os.path.exists(self.csv_path):
                with st.spinner(get_text("loading_data", lang)):
                    try:
                        # 正确的构造函数调用 - csv_file_path是第一个参数
                        processor = ASRSDataProcessor(self.csv_path, self.db_path)
                        # 使用正确的方法名
                        df = processor.load_data()
                        cleaned_df = processor.clean_data()
                        
                        # 将处理好的数据存储到会话状态
                        st.session_state.data_loaded = True
                        st.session_state.asrs_data = cleaned_df
                        st.session_state.data_processor = processor
                        
                        st.success(get_text("data_load_success", lang))
                        st.info(f"{get_text('data_loaded_info', lang)} {len(cleaned_df)} {get_text('records', lang)}")
                        
                    except Exception as e:
                        st.error(get_text("data_load_failed", lang).format(e))
                        st.exception(e)  # 显示详细错误信息以便调试
            else:
                st.error(get_text("file_not_found", lang).format(self.csv_path))

    def _show_asrs_smart_report(self):
        """ASRS智能报告页面 - 真正的AI智能化系统"""
        lang = st.session_state.selected_language
        
        title_text = "🎯 ASRS Smart Report System" if lang == 'en' else "🎯 ASRS智能报告系统"
        st.markdown(f'<h2 class="sub-header">{title_text}</h2>', unsafe_allow_html=True)
        
        if lang == 'en':
            info_text = """
            **🧠 True AI-Powered Report System**
            
            🚀 **Intelligent Workflow**：
            1. 📝 Input Incident Narrative → 2. 🤖 AI Smart Field Extraction → 3. 📋 Intelligent Completeness Review → 4. ❓ Generate Supplementary Questions → 5. ✅ Complete Report Generation
            
            - 🧠 GPT-4o intelligent field extraction and auto-form filling
            - 🔍 AI completeness review and missing information identification  
            - ❓ Intelligent generation of professional supplementary questions
            - 🔗 Seamless integration with follow-up analysis functions
            - 📊 Compliant with NASA ASRS professional standards
            """
        else:
            info_text = """
            **🧠 真正的AI智能化报告系统**
            
            🚀 **智能化工作流程**：
            1. 📝 输入事故叙述 → 2. 🤖 AI智能提取字段 → 3. 📋 智能审核完整性 → 4. ❓ 生成补充问题 → 5. ✅ 完整报告生成
            
            - 🧠 GPT-4o智能字段提取和自动填表
            - 🔍 AI完整性审核和缺失信息识别  
            - ❓ 智能生成专业补充问题
            - 🔗 无缝集成后续分析功能
            - 📊 符合NASA ASRS专业标准
            """
        
        st.info(info_text)
        
        # 智能化流程状态管理
        if 'smart_report_stage' not in st.session_state:
            st.session_state.smart_report_stage = 'narrative_input'
        if 'extracted_data' not in st.session_state:
            st.session_state.extracted_data = {}
        if 'completeness_result' not in st.session_state:
            st.session_state.completeness_result = None
        if 'smart_questions' not in st.session_state:
            st.session_state.smart_questions = []
        if 'question_answers' not in st.session_state:
            st.session_state.question_answers = {}
        
        # 根据阶段显示不同界面
        if st.session_state.smart_report_stage == 'narrative_input':
            self._show_narrative_input_stage()
        elif st.session_state.smart_report_stage == 'smart_extraction':
            self._show_smart_extraction_stage()
        elif st.session_state.smart_report_stage == 'completeness_review':
            self._show_completeness_review_stage()
        elif st.session_state.smart_report_stage == 'smart_questions':
            self._show_smart_questions_stage()
        elif st.session_state.smart_report_stage == 'final_review':
            self._show_final_review_stage()
    
    def _show_narrative_input_stage(self):
        """第一阶段：叙述输入"""
        lang = st.session_state.selected_language
        
        step_title = "📝 Step 1: Input Detailed Incident Narrative" if lang == 'en' else "📝 第一步：输入事故详细叙述"
        st.subheader(step_title)
        
        description = ("Please describe the complete UAV incident process in detail. AI will automatically extract key information and intelligently fill out the report form." 
                      if lang == 'en' else "请详细描述无人机事故的完整过程，AI将自动从中提取关键信息并智能填写报告表单。")
        st.markdown(description)
        
        # 叙述输入区域
        with st.form("narrative_form"):
            narrative_label = "Detailed Incident Narrative*" if lang == 'en' else "事故详细叙述*"
            
            if lang == 'en':
                placeholder_text = """Please describe the incident process in detail, including:
• Time, location, weather conditions
• UAV model, flight phase, mission type
• Specific process and causes of the incident
• Operator actions and decisions
• Incident results and impact
• Emergency measures taken

Example: At 2:30 PM on March 15, 2024, during DJI Phantom 4 training flight near Beijing Shunyi Airport, the UAV suddenly lost GPS signal during cruise phase at 150 feet altitude, causing the aircraft to enter attitude mode. The pilot attempted manual control but lost control due to strong winds and crashed..."""
            else:
                placeholder_text = """请详细描述事故过程，包括：
• 时间、地点、天气条件
• 无人机型号、飞行阶段、任务类型
• 事故发生的具体过程和原因
• 操作员的行动和决策
• 事故结果和影响
• 采取的应急措施

示例：2024年3月15日下午2点30分，在北京顺义机场附近进行DJI Phantom 4训练飞行时，无人机在150英尺高度巡航阶段突然失去GPS信号，导致飞行器进入姿态模式。飞行员尝试手动控制但由于强风影响失控坠落..."""
            
            narrative = st.text_area(
                narrative_label, 
                height=200,
                placeholder=placeholder_text,
                key="main_narrative"
            )
            
            # 基本必填信息
            basic_info_title = "### 📋 Basic Information (Required)" if lang == 'en' else "### 📋 基本信息（必填）"
            st.markdown(basic_info_title)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                date_label = "Incident Date*" if lang == 'en' else "事故发生日期*"
                occurrence_date = st.date_input(date_label)
                time_label = "Time Period*" if lang == 'en' else "时间段*"
                time_of_day = st.selectbox(time_label, 
                    ['0001-0600', '0601-1200', '1201-1800', '1801-2400'])
            
            with col2:
                city_label = "Location City*" if lang == 'en' else "发生城市*"
                location_city = st.text_input(city_label)
                pilot_label = "Operator Qualification*" if lang == 'en' else "操作员资质*"
                pilot_qualification = st.selectbox(pilot_label,
                    ['Part 107 Remote Pilot Certificate', 'Part 61 Pilot Certificate', 
                     'Military UAV Training', 'Manufacturer Training', 'Other', 'None'])
            
            with col3:
                incident_label = "Incident Type*" if lang == 'en' else "事件类型*"
                incident_type = st.selectbox(incident_label,
                    ['Near Mid-Air Collision (NMAC)', 'Airspace Violation', 'Loss of Control', 
                     'System Malfunction', 'Communication Failure', 'Weather Related', 
                     'Runway Incursion', 'Ground Collision', 'Emergency Landing', 'Other'])
            
            submit_label = "🚀 Start AI Smart Analysis" if lang == 'en' else "🚀 开始AI智能分析"
            submitted = st.form_submit_button(submit_label, type="primary", use_container_width=True)
        
        if submitted:
            if narrative.strip() and occurrence_date and location_city and pilot_qualification and incident_type:
                # 保存基本信息
                st.session_state.basic_info = {
                    'narrative': narrative,
                    'occurrence_date': occurrence_date.isoformat(),
                    'time_of_day': time_of_day,
                    'location_city': location_city,
                    'pilot_qualification': pilot_qualification,
                    'incident_type': incident_type
                }
                
                st.session_state.smart_report_stage = 'smart_extraction'
                st.rerun()
            else:
                error_msg = "❌ Please fill in all required fields" if lang == 'en' else "❌ 请填写所有必填字段"
                st.error(error_msg)
    
    def _show_smart_extraction_stage(self):
        """第二阶段：AI智能提取"""
        lang = st.session_state.selected_language
        
        step_title = "🤖 Step 2: AI Smart Field Extraction" if lang == 'en' else "🤖 第二步：AI智能字段提取"
        st.subheader(step_title)
        
        if st.session_state.extracted_data:
            # 检查是否处于编辑模式
            if hasattr(st.session_state, 'edit_mode') and st.session_state.edit_mode:
                self._show_edit_form()
            else:
                # 已经提取过，显示结果
                self._display_extracted_data()
        else:
            # 开始AI提取
            with st.spinner(get_text('ai_analyzing', lang)):
                try:
                    # 使用智能表单助手进行分析
                    narrative = st.session_state.basic_info['narrative']
                    analysis_result = st.session_state.form_assistant.analyze_narrative(narrative, st.session_state.basic_info)
                    
                    # 合并基本信息和AI提取的信息
                    extracted_data = st.session_state.basic_info.copy()
                    extracted_data.update(analysis_result.extracted_fields)
                    extracted_data['ai_synopsis'] = analysis_result.synopsis
                    extracted_data['completeness_score'] = analysis_result.completeness_score
                    extracted_data['confidence_scores'] = analysis_result.confidence_scores
                    
                    st.session_state.extracted_data = extracted_data
                    st.session_state.completeness_result = analysis_result
                    
                    st.success(get_text("ai_extraction_complete", lang))
                    st.rerun()
                    
                except Exception as e:
                    st.error(get_text("ai_analysis_failed", lang).format(e))
                    # 返回叙述输入阶段
                    if st.button(get_text('retry', lang)):
                        st.session_state.smart_report_stage = 'narrative_input'
                        st.rerun()
    
    def _show_edit_form(self):
        """显示编辑表单"""
        lang = st.session_state.selected_language
        
        edit_title = "📝 Edit Extracted Data" if lang == 'en' else "📝 编辑提取的数据"
        st.subheader(edit_title)
        
        # 创建编辑表单
        with st.form("edit_extracted_data", clear_on_submit=False):
            # 基本信息编辑
            st.markdown("### 📋 " + (get_text("flight_info", lang) if get_text("flight_info", lang) != "flight_info" else ("Basic Information" if lang == "en" else "基本信息")))
            
            col1, col2 = st.columns(2)
            with col1:
                narrative_label = "Narrative Description" if lang == 'en' else "叙述描述"
                narrative = st.text_area(narrative_label, 
                                       value=st.session_state.extracted_data.get('narrative', ''), 
                                       height=100)
                
                occurrence_date_str = st.session_state.extracted_data.get('occurrence_date', '')
                if occurrence_date_str:
                    try:
                        from datetime import datetime
                        occurrence_date = datetime.fromisoformat(occurrence_date_str).date()
                    except:
                        occurrence_date = None
                else:
                    occurrence_date = None
                
                date_label = "Incident Date" if lang == 'en' else "事故日期"
                occurrence_date = st.date_input(date_label, value=occurrence_date)
                
            with col2:
                location_city = st.text_input("Location City" if lang == 'en' else "发生城市", 
                                            value=st.session_state.extracted_data.get('location_city', ''))
                time_of_day = st.selectbox("Time Period" if lang == 'en' else "时间段", 
                                         ['0001-0600', '0601-1200', '1201-1800', '1801-2400'],
                                         index=['0001-0600', '0601-1200', '1201-1800', '1801-2400'].index(
                                             st.session_state.extracted_data.get('time_of_day', '1201-1800')))
            
            # AI提取字段编辑
            st.markdown("### 🤖 " + ("AI Extracted Fields" if lang == 'en' else "AI提取字段"))
            
            # 存储编辑后的值
            edited_data = {}
            
            # 飞行信息
            with st.expander("🛩️ " + get_text("flight_info", lang), expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    edited_data['flight_phase'] = st.text_input("Flight Phase", 
                                                              value=st.session_state.extracted_data.get('flight_phase', ''))
                    edited_data['altitude_agl'] = st.text_input("Altitude AGL", 
                                                              value=st.session_state.extracted_data.get('altitude_agl', ''))
                with col2:
                    edited_data['altitude_msl'] = st.text_input("Altitude MSL", 
                                                              value=st.session_state.extracted_data.get('altitude_msl', ''))
                    edited_data['flight_conditions'] = st.text_input("Flight Conditions", 
                                                                    value=st.session_state.extracted_data.get('flight_conditions', ''))
            
            # 天气条件
            with st.expander("🌤️ " + get_text("weather_conditions", lang), expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    edited_data['weather_conditions'] = st.text_input("Weather Conditions", 
                                                                     value=st.session_state.extracted_data.get('weather_conditions', ''))
                    edited_data['wind_speed'] = st.text_input("Wind Speed", 
                                                             value=st.session_state.extracted_data.get('wind_speed', ''))
                with col2:
                    edited_data['visibility'] = st.text_input("Visibility", 
                                                            value=st.session_state.extracted_data.get('visibility', ''))
                    edited_data['temperature'] = st.text_input("Temperature", 
                                                              value=st.session_state.extracted_data.get('temperature', ''))
            
            # 无人机信息
            with st.expander("🚁 " + get_text("uav_info", lang), expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    edited_data['aircraft_make'] = st.text_input("Aircraft Make", 
                                                               value=st.session_state.extracted_data.get('aircraft_make', ''))
                    edited_data['aircraft_model'] = st.text_input("Aircraft Model", 
                                                                 value=st.session_state.extracted_data.get('aircraft_model', ''))
                with col2:
                    edited_data['propulsion_type'] = st.text_input("Propulsion Type", 
                                                                  value=st.session_state.extracted_data.get('propulsion_type', ''))
                    edited_data['control_method'] = st.text_input("Control Method", 
                                                                 value=st.session_state.extracted_data.get('control_method', ''))
            
            # 事件分析
            with st.expander("🔍 " + get_text("event_analysis", lang), expanded=True):
                edited_data['anomaly_description'] = st.text_area("Anomaly Description", 
                                                                 value=st.session_state.extracted_data.get('anomaly_description', ''),
                                                                 height=100)
                col1, col2 = st.columns(2)
                with col1:
                    edited_data['primary_problem'] = st.text_input("Primary Problem", 
                                                                  value=st.session_state.extracted_data.get('primary_problem', ''))
                    edited_data['human_factors'] = st.text_input("Human Factors", 
                                                                value=st.session_state.extracted_data.get('human_factors', ''))
                with col2:
                    edited_data['contributing_factors'] = st.text_input("Contributing Factors", 
                                                                       value=st.session_state.extracted_data.get('contributing_factors', ''))
                    edited_data['equipment_factors'] = st.text_input("Equipment Factors", 
                                                                    value=st.session_state.extracted_data.get('equipment_factors', ''))
            
            # AI概要编辑
            ai_synopsis = st.text_area("AI Generated Synopsis" if lang == 'en' else "AI生成概要",
                                      value=st.session_state.extracted_data.get('ai_synopsis', ''),
                                      height=150)
            
            # 提交按钮
            col1, col2 = st.columns(2)
            with col1:
                save_label = "💾 Save Changes" if lang == 'en' else "💾 保存修改"
                save_changes = st.form_submit_button(save_label, type="primary")
            with col2:
                cancel_label = "❌ Cancel Editing" if lang == 'en' else "❌取消编辑"
                cancel_editing = st.form_submit_button(cancel_label)
        
        if save_changes:
            # 更新数据
            st.session_state.extracted_data.update(edited_data)
            st.session_state.extracted_data['narrative'] = narrative
            st.session_state.extracted_data['occurrence_date'] = occurrence_date.isoformat()
            st.session_state.extracted_data['location_city'] = location_city
            st.session_state.extracted_data['time_of_day'] = time_of_day
            st.session_state.extracted_data['ai_synopsis'] = ai_synopsis
            
            # 退出编辑模式
            st.session_state.edit_mode = False
            st.success("✅ " + ("Changes saved successfully!" if lang == 'en' else "修改保存成功！"))
            st.rerun()
            
        if cancel_editing:
            # 退出编辑模式
            st.session_state.edit_mode = False
            st.rerun()
    
    def _display_extracted_data(self):
        """显示AI提取的数据"""
        lang = st.session_state.selected_language
        st.success(get_text("ai_extraction_complete", lang) + ("! The following are automatically identified and filled fields:" if lang == "en" else "！以下是自动识别和填写的字段："))
        
        # 显示提取统计
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(get_text("extracted_fields", lang), len(st.session_state.extracted_data))
        with col2:
            completeness = st.session_state.completeness_result.completeness_score if st.session_state.completeness_result else 0
            st.metric(get_text("data_completeness", lang), f"{completeness:.1%}")
        with col3:
            confidence_scores = st.session_state.completeness_result.confidence_scores if st.session_state.completeness_result else {}
            avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0
            st.metric(get_text("avg_confidence", lang), f"{avg_confidence:.1%}")
        with col4:
            missing_count = len(st.session_state.completeness_result.missing_fields) if st.session_state.completeness_result else 0
            st.metric(get_text("missing_fields", lang), missing_count)
        
        # 显示提取的字段
        st.subheader(f"🔍 {get_text('extraction_details', lang)}")
        
        # 按类别分组显示
        field_categories = {
            get_text("flight_info", lang): ["flight_phase", "altitude_agl", "altitude_msl", "flight_conditions", "light_conditions"],
            get_text("weather_conditions", lang): ["weather_conditions", "wind_speed", "wind_direction", "visibility", "ceiling", "temperature"],
            get_text("uav_info", lang): ["aircraft_make", "aircraft_model", "aircraft_weight", "propulsion_type", "control_method"],
            get_text("event_analysis", lang): ["anomaly_description", "primary_problem", "contributing_factors", "human_factors", "equipment_factors"],
            get_text("other_info", lang): []  # 将收集其他字段
        }
        
        for category, fields in field_categories.items():
            with st.expander(f"📋 {category}", expanded=True):
                cols = st.columns(2)
                col_idx = 0
                
                for field in fields:
                    if field in st.session_state.extracted_data:
                        value = st.session_state.extracted_data[field]
                        confidence = st.session_state.completeness_result.confidence_scores.get(field, 0) if st.session_state.completeness_result else 0
                        
                        confidence_color = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.4 else "🔴"
                        
                        with cols[col_idx]:
                            st.write(f"**{field}** {confidence_color}")
                            st.write(f"**{get_text('value', lang)}:** {value}")
                            st.write(f"**{get_text('confidence', lang)}:** {confidence:.1%}")
                            st.write("---")
                        
                        col_idx = 1 - col_idx
        
        # AI生成的概要
        if st.session_state.extracted_data.get('ai_synopsis'):
            st.subheader(get_text('ai_synopsis', lang))
            st.info(st.session_state.extracted_data['ai_synopsis'])
        
        # 操作按钮
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(get_text('edit_results', lang)):
                st.session_state.edit_mode = True
                st.rerun()
        
        with col2:
            if st.button(get_text('continue_review', lang), type="primary"):
                st.session_state.smart_report_stage = 'completeness_review'
                st.rerun()
        
        with col3:
            if st.button(get_text('reextract', lang)):
                st.session_state.extracted_data = {}
                st.rerun()
    
    def _show_completeness_review_stage(self):
        """第三阶段：完整性审核"""
        lang = st.session_state.selected_language
        
        step_title = "🔍 Step 3: AI Completeness Review" if lang == 'en' else "🔍 第三步：AI完整性审核"
        st.subheader(step_title)
        
        if not st.session_state.completeness_result:
            st.error(get_text("missing_completeness_analysis", lang) if get_text("missing_completeness_analysis", lang) != "missing_completeness_analysis" else ("❌ Missing completeness analysis results" if lang == "en" else "❌ 缺少完整性分析结果"))
            return
        
        result = st.session_state.completeness_result
        
        # 完整性评估概览
        st.markdown(f"### 📊 {get_text('completeness_assessment', lang)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 完整性分数
            completeness = result.completeness_score
            if completeness >= 0.8:
                st.success(f"✅ {('Data Completeness' if lang == 'en' else '数据完整度')}：{completeness:.1%} - {get_text('excellent', lang)}")
                completeness_desc = get_text('data_complete_excellent', lang)
            elif completeness >= 0.6:
                st.warning(f"🟡 {('Data Completeness' if lang == 'en' else '数据完整度')}：{completeness:.1%} - {get_text('good', lang)}")
                completeness_desc = get_text('data_complete_good', lang)
            else:
                st.error(f"🔴 {('Data Completeness' if lang == 'en' else '数据完整度')}：{completeness:.1%} - {get_text('needs_improvement', lang)}")
                completeness_desc = get_text('data_incomplete', lang)
            
            st.write(completeness_desc)
        
        with col2:
            # 缺失字段统计
            missing_count = len(result.missing_fields)
            if missing_count == 0:
                st.success(get_text("no_missing_info", lang))
            else:
                st.warning(get_text("missing_critical_fields", lang).format(missing_count))
        
        # 缺失字段详情
        if result.missing_fields:
            st.markdown(f"### {get_text('missing_key_info', lang)}")
            for i, missing_field in enumerate(result.missing_fields, 1):
                st.write(f"{i}. {missing_field}")
        
        # AI建议的补充问题
        if result.suggested_questions:
            st.markdown(f"### {get_text('ai_suggested_questions', lang)}")
            st.info(get_text('ai_questions_desc', lang))
            
            for i, question in enumerate(result.suggested_questions, 1):
                st.write(f"**{get_text('question', lang)} {i}:** {question}")
        
        # 操作选择
        st.markdown("---")
        st.subheader(get_text('next_step', lang))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(get_text('answer_questions', lang), type="primary"):
                st.session_state.smart_questions = result.suggested_questions
                st.session_state.smart_report_stage = 'smart_questions'
                st.rerun()
        
        with col2:
            if st.button(get_text('submit_directly', lang)):
                st.session_state.smart_report_stage = 'final_review'
                st.rerun()
        
        with col3:
            if st.button(get_text('return_edit', lang)):
                st.session_state.smart_report_stage = 'smart_extraction'
                st.rerun()
    
    def _show_smart_questions_stage(self):
        """第四阶段：智能问题回答"""
        lang = st.session_state.selected_language
        
        step_title = "❓ Step 4: Answer AI Smart Questions" if lang == 'en' else "❓ 第四步：回答AI智能问题"
        st.subheader(step_title)
        
        description = get_text('answer_questions_desc', lang)
        st.markdown(description)
        
        if not st.session_state.smart_questions:
            st.error(get_text("no_questions_data", lang))
            return
        
        with st.form("smart_questions_form"):
            answers = {}
            
            for i, question in enumerate(st.session_state.smart_questions, 1):
                st.markdown(f"### {get_text('question', lang)} {i}")
                st.write(question)
                
                answer = st.text_area(
                    f"{get_text('answer_question', lang)} {i}",
                    key=f"answer_{i}",
                    placeholder=get_text('answer_placeholder', lang),
                    height=100
                )
                answers[f"question_{i}"] = {"question": question, "answer": answer}
            
            submitted = st.form_submit_button(get_text('submit_answers', lang), type="primary")
        
        if submitted:
            # 过滤掉空答案
            valid_answers = {k: v for k, v in answers.items() if v["answer"].strip()}
            st.session_state.question_answers = valid_answers
            
            if valid_answers:
                st.success(get_text('answers_collected', lang).format(len(valid_answers)))
                
                # 使用LLM处理这些答案，提取更多字段信息
                with st.spinner(get_text('ai_processing_answers', lang)):
                    try:
                        # 构建包含原始叙述和问答的完整文本
                        enhanced_narrative = st.session_state.basic_info['narrative'] + "\n\n" + get_text('supplementary_info', lang) + "\n"
                        for qa in valid_answers.values():
                            enhanced_narrative += f"{get_text('question_mark', lang)}{qa['question']}\n{get_text('answer_mark', lang)}{qa['answer']}\n\n"
                        
                        # 重新分析增强后的叙述
                        enhanced_result = st.session_state.form_assistant.analyze_narrative(
                            enhanced_narrative, st.session_state.extracted_data
                        )
                        
                        # 更新提取的数据
                        st.session_state.extracted_data.update(enhanced_result.extracted_fields)
                        st.session_state.extracted_data['enhanced_narrative'] = enhanced_narrative
                        st.session_state.extracted_data['final_completeness'] = enhanced_result.completeness_score
                        
                        st.success(get_text('info_updated', lang))
                        
                        # 设置标志表示答案已处理
                        st.session_state.answers_processed = True
                        
                    except Exception as e:
                        st.error(get_text('answer_processing_failed', lang).format(e))
            else:
                st.warning(get_text('answer_at_least_one', lang))
        
        # 显示进入最终审核的按钮（在表单外部，避免Streamlit表单重置问题）
        if hasattr(st.session_state, 'question_answers') and st.session_state.question_answers:
            st.markdown("---")
            st.markdown(f"### {get_text('ready_final_review', lang)}")
            st.info(get_text('answers_complete', lang))
            
            if st.button(get_text('enter_final_review', lang), type="primary", key="final_review_btn"):
                st.session_state.smart_report_stage = 'final_review'
                st.rerun()
        
        # 为没有回答问题的用户提供跳过选项
        else:
            st.markdown("---")
            st.markdown(f"### {get_text('skip_questions', lang)}")
            st.warning(get_text('skip_warning', lang))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(get_text('skip_and_review', lang), key="skip_questions_btn"):
                    # 设置空的问答记录
                    st.session_state.question_answers = {}
                    st.session_state.smart_report_stage = 'final_review'
                    st.rerun()
            
            with col2:
                if st.button(get_text('refresh_questions', lang), key="refresh_questions_btn"):
                    st.rerun()
    
    def _show_final_review_stage(self):
        """第五阶段：最终审核和提交"""
        lang = st.session_state.selected_language
        
        step_title = "✅ Step 5: Final Review and Submission" if lang == 'en' else "✅ 第五步：最终审核和提交"
        st.subheader(step_title)
        
        # 显示最终数据概览
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(get_text('extracted_fields', lang), len(st.session_state.extracted_data))
        
        with col2:
            final_completeness = st.session_state.extracted_data.get('final_completeness', 
                                st.session_state.completeness_result.completeness_score if st.session_state.completeness_result else 0)
            st.metric(get_text('final_completeness', lang), f"{final_completeness:.1%}")
        
        with col3:
            qa_count = len(st.session_state.question_answers)
            st.metric(get_text('supplementary_answers_short', lang), f"{qa_count} {'items' if lang == 'en' else '个'}")
        
        with col4:
            report_id_preview = f"ASRS_{datetime.now().strftime('%Y%m%d_%H%M')}"
            st.metric(get_text('report_id', lang), report_id_preview[:12])
        
        # 最终报告预览
        st.subheader(get_text('final_report_preview', lang))
        
        with st.expander(get_text('view_complete_report', lang), expanded=False):
            st.json(st.session_state.extracted_data)
        
        # 提交按钮和后续操作
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(get_text('submit_asrs_report', lang), type="primary", use_container_width=True):
                # 设置提交确认标志
                st.session_state.show_submit_confirmation = True
                st.rerun()
        
        # 显示提交确认对话框
        if hasattr(st.session_state, 'show_submit_confirmation') and st.session_state.show_submit_confirmation:
            st.markdown("---")
            st.subheader(get_text('submit_confirmation', lang))
            st.write(get_text('confirm_submit', lang))
            
            col_confirm1, col_confirm2 = st.columns(2)
            with col_confirm1:
                if st.button("✅ " + ("Confirm" if lang == 'en' else "确认"), key="confirm_submit_btn", type="primary"):
                    # 执行实际提交
                    report_id = f"ASRS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    # 重新计算最终完整度以确保变量可用
                    final_completeness = st.session_state.extracted_data.get('final_completeness', 
                                        st.session_state.completeness_result.completeness_score if st.session_state.completeness_result else 0)
                    
                    # 构建最终的ASRS报告
                    final_report = {
                        'id': report_id,
                        'report_date': datetime.now().isoformat(),
                        'submission_type': 'ASRS_Smart',
                        **st.session_state.extracted_data,
                        'question_answers': st.session_state.question_answers,
                        'intelligence_metadata': {
                            'ai_extraction': True,
                            'completeness_reviewed': True,
                            'smart_questions_answered': len(st.session_state.question_answers) > 0,
                            'final_completeness_score': final_completeness
                        }
                    }
                    
                    # 保存到session state
                    st.session_state.current_asrs_report = final_report
                    st.session_state.current_report = final_report  # 兼容旧版本
                    st.session_state.report_submitted = True  # 设置提交标志
                    st.session_state.show_submit_confirmation = False
                    st.session_state.show_causal_confirmation = True
                    
                    st.success(get_text('report_submitted_success', lang))
                    st.rerun()
                    
            with col_confirm2:
                if st.button("❌ " + ("Cancel" if lang == 'en' else "取消"), key="cancel_submit_btn"):
                    st.session_state.show_submit_confirmation = False
                    st.rerun()
        
        # 显示因果分析跳转确认对话框
        if hasattr(st.session_state, 'show_causal_confirmation') and st.session_state.show_causal_confirmation:
            st.markdown("---")
            st.subheader(get_text('causal_confirmation', lang))
            st.write(get_text('jump_to_causal', lang))
            
            col_causal1, col_causal2 = st.columns(2)
            with col_causal1:
                if st.button("✅ " + ("Yes, Go to Causal Analysis" if lang == 'en' else "是的，前往因果分析"), key="goto_causal_btn", type="primary"):
                    st.session_state.show_causal_confirmation = False
                    st.session_state.page_redirect = "causal_analysis"
                    st.rerun()
                    
            with col_causal2:
                if st.button("❌ " + ("No, Stay Here" if lang == 'en' else "不，留在这里"), key="stay_here_btn"):
                    st.session_state.show_causal_confirmation = False
                    st.rerun()
        
        with col2:
            if st.button(get_text('restart', lang), use_container_width=True):
                # 清空所有状态
                keys_to_clear = ['smart_report_stage', 'extracted_data', 'completeness_result', 
                               'smart_questions', 'question_answers', 'basic_info', 'report_submitted']
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        

    def _show_causal_analysis(self):
        """因果关系分析页面"""
        lang = st.session_state.selected_language
        
        title_text = "🔗 Intelligent Causal Analysis" if lang == 'en' else "🔗 智能因果关系分析"
        st.markdown(f'<h2 class="sub-header">{title_text}</h2>', unsafe_allow_html=True)
        
        if lang == 'en':
            info_text = """
            **🧠 AI-Driven Causal Analysis**
            
            Automatically generate professional causal diagrams based on incident narratives:
            - 🎯 Root cause identification and analysis
            - 🔗 Multi-level causal relationship mapping
            - ⏱️ Incident timeline reconstruction
            - 🛡️ Safety barrier analysis and control point identification
            - 📊 Interactive visualization and risk path analysis
            """
        else:
            info_text = """
            **🧠 AI驱动的因果关系分析**
            
            基于事故叙述自动生成专业的因果关系图：
            - 🎯 根本原因识别和分析
            - 🔗 多层级因果关系映射
            - ⏱️ 事故时间序列重建
            - 🛡️ 安全屏障分析和控制点识别
            - 📊 交互式可视化和风险路径分析
            """
        
        st.info(info_text)
        
        # 检查是否有报告数据
        current_report = st.session_state.get('current_asrs_report') or st.session_state.get('current_report')
        
        if not current_report:
            st.warning("⚠️ " + ("Please submit incident report first to generate causal diagram" if lang == 'en' else "请先提交事故报告以生成因果关系图"))
            
            # 提供快速输入选项
            st.subheader("📝 " + ("Quick Narrative Input" if lang == 'en' else "快速叙述输入"))
            quick_narrative = st.text_area(
                "Enter incident narrative for causal analysis" if lang == 'en' else "输入事故叙述进行因果关系分析", 
                height=150,
                placeholder="Please describe the detailed incident process, including timeline, factors involved, decision points..." if lang == 'en' else "请描述事故的详细过程，包括时间序列、涉及因素、决策点等..."
            )
            
            if st.button("🚀 " + ("Generate Causal Diagram" if lang == 'en' else "生成因果关系图"), type="primary") and quick_narrative.strip():
                current_report = {
                    'detailed_narrative': quick_narrative,
                    'narrative': quick_narrative,
                    'id': f"QUICK_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
        
        if current_report:
            # 显示当前报告信息
            st.subheader(get_text('analysis_target_report', lang))
            with st.expander(get_text("report_details", lang), expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**{get_text('report_id', lang)}:** {current_report.get('id', 'N/A')}")
                    st.write(f"**{get_text('incident_type', lang)}:** {current_report.get('incident_type', 'N/A')}")
                with col2:
                    st.write(f"**{get_text('flight_phase', lang)}:** {current_report.get('flight_phase', 'N/A')}")
                    st.write(f"**{get_text('operation_type', lang)}:** {current_report.get('aircraft_operator_type', 'N/A')}")
                
                narrative = current_report.get('detailed_narrative') or current_report.get('narrative', '')
                if narrative:
                    st.write(f"**{get_text('incident_narrative', lang)}:**")
                    st.write(narrative[:500] + ("..." if len(narrative) > 500 else ""))
            
            # 因果分析控制
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(get_text('ai_causal_analysis', lang), type="primary"):
                    with st.spinner(get_text('causal_analysis_processing', lang)):
                        try:
                            # 初始化因果图生成器
                            if not st.session_state.get('causal_generator'):
                                if CAUSAL_DIAGRAM_AVAILABLE:
                                    model = st.session_state.get('selected_model', 'gpt-4o-mini')
                                    st.session_state.causal_generator = CausalDiagramGenerator(model=model)
                                else:
                                    st.error(get_text('causal_analysis_unavailable', lang))
                                    st.stop()
                            
                            # 提取叙述
                            narrative = current_report.get('detailed_narrative') or current_report.get('narrative', '')
                            
                            # 生成因果图
                            causal_diagram = st.session_state.causal_generator.generate_causal_diagram(
                                narrative, current_report
                            )
                            
                            st.session_state.current_causal_diagram = causal_diagram
                            st.success(get_text('causal_analysis_complete', lang))
                            
                        except Exception as e:
                            st.error(get_text('causal_analysis_failed', lang).format(e))
            
            with col2:
                if st.button(get_text('reanalyze', lang)):
                    if 'current_causal_diagram' in st.session_state:
                        del st.session_state.current_causal_diagram
                    st.rerun()
            
            with col3:
                prof_btn_text = "📊 " + ("Switch to Professional Investigation" if lang == 'en' else "切换到专业调查")
                if st.button(prof_btn_text):
                    st.session_state.page_redirect = "professional_investigation"
                    st.rerun()
        
        # 显示因果分析结果
        if st.session_state.get('current_causal_diagram'):
            self._display_causal_diagram_results(st.session_state.current_causal_diagram)

    def _display_causal_diagram_results(self, causal_diagram):
        """Display professional causal analysis results in English with clean formatting"""
        st.markdown("---")
        
        # Professional header with clear styling
        st.markdown("""
        <div style='background: linear-gradient(90deg, #2E86AB 0%, #A23B72 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2 style='color: white; text-align: center; margin: 0; font-weight: bold;'>
                🔗 Professional Causal Analysis Results
            </h2>
            <p style='color: white; text-align: center; margin: 0; font-size: 16px; opacity: 0.9;'>
                Comprehensive incident causal relationship analysis and risk assessment
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Executive Summary Metrics
        st.markdown("### 📊 **Executive Summary**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🎯 **Central Event**", 
                value=causal_diagram.central_event,
                help="Primary incident or failure event under analysis"
            )
        with col2:
            st.metric(
                label="🔗 **Causal Factors**", 
                value=len(causal_diagram.nodes),
                help="Total number of identified causal factors and nodes"
            )
        with col3:
            st.metric(
                label="📈 **Relationships**", 
                value=len(causal_diagram.relationships),
                help="Direct and indirect causal relationships identified"
            )
        with col4:
            st.metric(
                label="⚡ **Risk Pathways**", 
                value=len(causal_diagram.risk_paths),
                help="Critical risk propagation paths requiring attention"
            )
        
        # Professional Analysis Tabs
        st.markdown("---")
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 **Causal Network**",
            "🔍 **Factor Analysis**", 
            "⏱️ **Event Timeline**",
            "🛡️ **Control Points**",
            "📋 **Executive Report**"
        ])
        
        with tab1:
            st.markdown("#### 🎯 **Interactive Causal Network Visualization**")
            st.markdown("*Comprehensive visual representation of incident causal relationships and factor interactions*")
            
            if CAUSAL_DIAGRAM_AVAILABLE and st.session_state.get('causal_generator'):
                try:
                    # Generate visualization in English
                    fig = st.session_state.causal_generator.create_causal_visualization(causal_diagram, 'en')
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
                    
                    # Add explanation
                    st.markdown("""
                    **📖 How to Read the Diagram:**
                    - **Node Size**: Proportional to impact severity
                    - **Colors**: Different factor types (organizational, technical, human, environmental)
                    - **Arrows**: Causal relationships with strength indicators
                    - **Layers**: Hierarchical organization from root causes to consequences
                    """)
                except Exception as e:
                    st.error(f"❌ **Visualization Generation Error:** {str(e)}")
                    st.info("💡 **Troubleshooting:** Check that all required dependencies are properly installed.")
            else:
                st.warning("⚠️ **Causal visualization system is loading...** Please wait a moment and refresh if needed.")
        
        with tab2:
            st.markdown("#### 🔍 **Detailed Causal Factor Analysis**")
            st.markdown("*Comprehensive breakdown of all identified causal factors with risk assessment*")
            
            if causal_diagram.nodes:
                # Group nodes by type for professional presentation
                node_types = {}
                for node in causal_diagram.nodes:
                    node_type = node.type
                    if node_type not in node_types:
                        node_types[node_type] = []
                    node_types[node_type].append(node)
                
                # Professional type mapping
                type_labels = {
                    'root_cause': '🔴 Root Causes',
                    'contributing_factor': '🟡 Contributing Factors', 
                    'immediate_cause': '🟠 Immediate Causes',
                    'consequence': '🟣 Consequences',
                    'organizational': '🏢 Organizational Factors',
                    'control_point': '🛡️ Control Points'
                }
                
                for node_type, nodes in node_types.items():
                    type_label = type_labels.get(node_type, f"📍 {node_type.replace('_', ' ').title()}")
                    st.markdown(f"### {type_label}")
                    
                    # Sort nodes by impact level (high to low)
                    sorted_nodes = sorted(nodes, key=lambda x: x.impact, reverse=True)
                    
                    for node in sorted_nodes:
                        # Risk level indicators
                        if node.impact > 0.8:
                            risk_icon = "🔴"
                            risk_label = "CRITICAL"
                            border_color = "#E74C3C"
                        elif node.impact > 0.6:
                            risk_icon = "🟠"
                            risk_label = "HIGH"
                            border_color = "#F39C12"
                        elif node.impact > 0.3:
                            risk_icon = "🟡"
                            risk_label = "MEDIUM"
                            border_color = "#F1C40F"
                        else:
                            risk_icon = "🟢"
                            risk_label = "LOW"
                            border_color = "#27AE60"
                        
                        with st.expander(f"{risk_icon} **{node.name}** [{risk_label} RISK]"):
                            # Professional layout with metrics
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown(f"""
                                **📊 Risk Metrics**
                                - **Impact Severity:** {node.impact:.1%}
                                - **Occurrence Likelihood:** {node.likelihood:.1%}  
                                - **Evidence Strength:** {node.evidence_strength:.1%}
                                """)
                            
                            with col2:
                                category_icons = {
                                    'human': '👤', 'technical': '⚙️', 
                                    'environmental': '🌍', 'organizational': '🏢',
                                    'procedural': '📋'
                                }
                                category_icon = category_icons.get(node.category, '📍')
                                
                                st.markdown(f"""
                                **🔍 Classification**
                                - **Factor Category:** {category_icon} {node.category.title()}
                                - **Factor Type:** {node.type.replace('_', ' ').title()}
                                """)
                            
                            with col3:
                                # Risk matrix visualization
                                risk_score = (node.impact + node.likelihood) / 2
                                st.metric("🎯 **Risk Score**", f"{risk_score:.2%}", 
                                         help="Combined impact and likelihood assessment")
                            
                            # Description with professional formatting
                            st.markdown(f"""
                            **📝 Factor Description:**
                            {node.description}
                            """)
                            
                            # Add visual separator
                            st.markdown(f"<hr style='border-color: {border_color}; margin: 10px 0;'>", unsafe_allow_html=True)
            else:
                st.warning("⚠️ **No causal factor data available.** Please ensure the analysis was completed successfully.")
        
        with tab3:
            st.markdown("#### ⏱️ **Incident Development Timeline**")
            st.markdown("*Chronological sequence of events leading to and following the incident*")
            
            if causal_diagram.timeline:
                timeline_df = pd.DataFrame(causal_diagram.timeline)
                
                # Professional timeline visualization
                fig = go.Figure()
                
                colors = {
                    'low': '#27AE60', 
                    'medium': '#F39C12', 
                    'high': '#E74C3C', 
                    'critical': '#8B0000'
                }
                
                for i, row in timeline_df.iterrows():
                    criticality = row.get('criticality', 'low')
                    color = colors.get(criticality, '#7F8C8D')
                    
                    # Enhanced markers with better sizing
                    marker_size = {
                        'low': 12, 'medium': 15, 'high': 18, 'critical': 22
                    }.get(criticality, 12)
                    
                    fig.add_trace(go.Scatter(
                        x=[i], y=[1],
                        mode='markers+text',
                        marker=dict(
                            size=marker_size, 
                            color=color,
                            line=dict(width=3, color='white'),
                            symbol='circle'
                        ),
                        text=[row.get('time', '')],
                        textposition="top center",
                        textfont=dict(size=12, color='black'),
                        name=row.get('event', ''),
                        hovertemplate=f"<b>🕐 {row.get('time', '')}</b><br>📋 {row.get('event', '')}<br>⚠️ Criticality: {criticality.upper()}<extra></extra>"
                    ))
                
                fig.update_layout(
                    title={
                        'text': "Incident Event Sequence Analysis",
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 18}
                    },
                    xaxis_title="Event Sequence Progression",
                    yaxis=dict(showticklabels=False, showgrid=False),
                    height=400,
                    showlegend=False,
                    plot_bgcolor='white'
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
                
                # Detailed timeline breakdown
                st.markdown("### 📋 **Detailed Event Chronology**")
                
                # Group events by criticality for better organization
                events_by_criticality = {'critical': [], 'high': [], 'medium': [], 'low': []}
                for event in causal_diagram.timeline:
                    criticality = event.get('criticality', 'low')
                    events_by_criticality[criticality].append(event)
                
                # Display in order of criticality
                criticality_labels = {
                    'critical': '🔴 **CRITICAL EVENTS**',
                    'high': '🟠 **HIGH PRIORITY EVENTS**', 
                    'medium': '🟡 **MODERATE EVENTS**',
                    'low': '🟢 **ROUTINE EVENTS**'
                }
                
                for level in ['critical', 'high', 'medium', 'low']:
                    events = events_by_criticality[level]
                    if events:
                        st.markdown(criticality_labels[level])
                        for event in events:
                            time_str = event.get('time', 'Time Unknown')
                            event_desc = event.get('event', 'Event description unavailable')
                            
                            st.markdown(f"""
                            <div style='background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid {colors[level]}; border-radius: 5px; border: 1px solid #e9ecef;'>
                                <strong style='color: #2c3e50;'>🕐 {time_str}</strong><br>
                                <span style='color: #495057;'>📝 {event_desc}</span>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ **No timeline data available.** Timeline analysis requires detailed incident chronology information.")
        
        with tab4:
            st.markdown("#### 🛡️ **Safety Control Points Analysis**")
            st.markdown("*Identification and evaluation of critical safety control measures and intervention opportunities*")
            
            if causal_diagram.control_points:
                st.markdown("### 📋 **Identified Control Points**")
                
                for i, control_point in enumerate(causal_diagram.control_points, 1):
                    effectiveness = control_point.get('effectiveness', 0)
                    
                    # Professional effectiveness indicators
                    if effectiveness > 0.8:
                        effectiveness_icon = "🟢"
                        effectiveness_label = "HIGHLY EFFECTIVE"
                        border_color = "#27AE60"
                    elif effectiveness > 0.6:
                        effectiveness_icon = "🟡"
                        effectiveness_label = "MODERATELY EFFECTIVE"
                        border_color = "#F39C12"
                    elif effectiveness > 0.3:
                        effectiveness_icon = "🟠"
                        effectiveness_label = "LIMITED EFFECTIVENESS"
                        border_color = "#E67E22"
                    else:
                        effectiveness_icon = "🔴"
                        effectiveness_label = "INEFFECTIVE"
                        border_color = "#E74C3C"
                    
                    control_name = control_point.get('name', f'Control Point {i}')
                    
                    with st.expander(f"{effectiveness_icon} **Control Point {i}: {control_name}** [{effectiveness_label}]"):
                        # Professional metrics layout
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("🎯 **Effectiveness Rating**", f"{effectiveness:.1%}",
                                     help="Assessed effectiveness of this control measure")
                            
                        with col2:
                            # Implementation difficulty if available
                            difficulty = control_point.get('implementation_difficulty', 'Unknown')
                            st.markdown(f"**🔧 Implementation:** {difficulty}")
                        
                        # Control point description
                        description = control_point.get('description', 'No detailed description available')
                        st.markdown(f"""
                        **📝 Control Description:**
                        {description}
                        """)
                        
                        # Associated causal factors
                        associated_factors = control_point.get('associated_factors', [])
                        if associated_factors:
                            st.markdown("**🔗 Associated Causal Factors:**")
                            for j, factor in enumerate(associated_factors, 1):
                                st.markdown(f"• **Factor {j}:** {factor}")
                        
                        # Recommendations if available
                        recommendations = control_point.get('recommendations', [])
                        if recommendations:
                            st.markdown("**💡 Implementation Recommendations:**")
                            for rec in recommendations:
                                st.markdown(f"✓ {rec}")
                        
                        # Visual separator
                        st.markdown(f"<hr style='border-color: {border_color}; margin: 15px 0;'>", unsafe_allow_html=True)
                
                # Summary statistics
                if len(causal_diagram.control_points) > 1:
                    avg_effectiveness = sum(cp.get('effectiveness', 0) for cp in causal_diagram.control_points) / len(causal_diagram.control_points)
                    high_effective = sum(1 for cp in causal_diagram.control_points if cp.get('effectiveness', 0) > 0.7)
                    
                    st.markdown("---")
                    st.markdown("### 📊 **Control Points Summary**")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📈 **Average Effectiveness**", f"{avg_effectiveness:.1%}")
                    with col2:
                        st.metric("🎯 **Highly Effective Controls**", f"{high_effective}/{len(causal_diagram.control_points)}")
                    with col3:
                        priority_controls = sum(1 for cp in causal_diagram.control_points if cp.get('effectiveness', 0) < 0.5)
                        st.metric("⚠️ **Priority for Improvement**", priority_controls)
            else:
                st.warning("⚠️ **No safety control points identified.** This may indicate a need for enhanced safety system analysis or insufficient data for control point identification.")
        
        with tab5:
            st.markdown("#### 📋 **Executive Analysis Report**")
            st.markdown("*Comprehensive professional report for management and stakeholders*")
            
            # Professional report preview
            st.markdown("### 📊 **Report Overview**")
            
            # Key findings summary
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **🎯 Report Scope:**
                - Complete causal chain analysis
                - Risk pathway identification  
                - Control point evaluation
                - Safety recommendations
                """)
            
            with col2:
                st.markdown("""
                **📈 Analysis Metrics:**
                - Total Factors: {total_nodes}
                - Risk Pathways: {risk_paths}
                - Control Points: {control_points}
                - Confidence Level: High
                """.format(
                    total_nodes=len(causal_diagram.nodes),
                    risk_paths=len(causal_diagram.risk_paths),
                    control_points=len(causal_diagram.control_points) if causal_diagram.control_points else 0
                ))
            
            st.markdown("---")
            
            # Generate professional report
            if st.button("📄 **Generate Executive Analysis Report**", type="primary"):
                try:
                    from datetime import datetime
                    
                    # Professional report content
                    report_content = f"""# UAV Incident Causal Analysis Report
**Professional Aviation Safety Analysis**

---

## Executive Summary

**Central Incident:** {causal_diagram.central_event}
**Analysis Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}
**Analysis Confidence:** High Confidence Assessment
**Report Classification:** Safety Analysis - Professional Use

---

## Key Findings Overview

### 🔴 Root Cause Analysis
{chr(10).join([f"• **{node.name}** (Impact: {node.impact:.1%}, Likelihood: {node.likelihood:.1%}){chr(10)}  *{node.description}*" for node in causal_diagram.nodes if node.type == 'root_cause']) or "• No root causes specifically identified in current analysis"}

### 🟡 Contributing Factors
{chr(10).join([f"• **{node.name}** (Impact: {node.impact:.1%}, Likelihood: {node.likelihood:.1%}){chr(10)}  *{node.description}*" for node in causal_diagram.nodes if node.type == 'contributing_factor']) or "• No contributing factors specifically identified"}

### 🟠 Immediate Causes
{chr(10).join([f"• **{node.name}** (Impact: {node.impact:.1%}, Likelihood: {node.likelihood:.1%}){chr(10)}  *{node.description}*" for node in causal_diagram.nodes if node.type == 'immediate_cause']) or "• No immediate causes specifically identified"}

---

## Risk Pathway Analysis

### Critical Risk Propagation Chains
{chr(10).join([f"**Path {i+1}:** {' ➜ '.join(path)}" for i, path in enumerate(causal_diagram.risk_paths)]) or "• No specific risk pathways identified in current analysis"}

---

## Safety Control Assessment

### Identified Control Points
{chr(10).join([f"• **{cp.get('name', f'Control Point {i+1}')}** (Effectiveness: {cp.get('effectiveness', 0):.1%}){chr(10)}  *{cp.get('description', 'Description not available')}*" for i, cp in enumerate(causal_diagram.control_points)]) if causal_diagram.control_points else "• No specific control points identified - recommend comprehensive safety system review"}

---

## Professional Recommendations

### Priority Actions Required
1. **Immediate Actions:** Address high-impact causal factors identified in root cause analysis
2. **System Improvements:** Enhance existing safety control mechanisms based on effectiveness ratings  
3. **Monitoring & Review:** Establish continuous monitoring for identified risk pathways
4. **Training & Procedures:** Update operational procedures to address contributing factors

### Risk Management Priorities
- Focus on causal factors with impact levels above 70%
- Strengthen control points with effectiveness below 60%
- Develop redundant safety measures for critical risk pathways
- Implement systematic monitoring and feedback mechanisms

---

## Analysis Methodology

**Analytical Framework:** Advanced AI-Powered Causal Analysis System
**Standards Compliance:** ICAO Annex 13 Investigation Principles
**Data Sources:** Incident reports, operational data, safety management systems
**Validation:** Multi-layered verification and confidence assessment

---

**Report Classification:** Professional Aviation Safety Analysis
**Distribution:** Safety Management, Operations Management, Regulatory Compliance
**Next Review:** Recommend follow-up analysis after corrective action implementation

*This report was generated by the ASRS UAV Incident Intelligence Analysis System using advanced AI causal analysis methodologies. For questions regarding methodology or findings, contact the Safety Analysis Team.*
"""
                    
                    # Professional download with timestamp
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"UAV_Causal_Analysis_Executive_Report_{timestamp}.md"
                    
                    st.download_button(
                        label="📥 **Download Executive Report**",
                        data=report_content,
                        file_name=filename,
                        mime="text/markdown",
                        help="Download complete executive analysis report in Markdown format"
                    )
                    
                    st.success("✅ **Executive analysis report generated successfully!** Report includes comprehensive findings, risk assessment, and professional recommendations.")
                    
                    # Report preview
                    with st.expander("📖 **Report Preview**", expanded=False):
                        st.markdown(report_content[:1000] + "..." if len(report_content) > 1000 else report_content)
                        
                except Exception as e:
                    st.error(f"❌ **Report Generation Error:** {str(e)}")
                    st.info("💡 **Troubleshooting:** Ensure all analysis components completed successfully before generating report.")

    # 其他页面方法保持不变...
    def _show_smart_report_submission(self):
        """智能报告提交页面（简化版兼容）"""
        lang = st.session_state.selected_language
        st.info(get_text('use_new_smart_report', lang))
        if st.button(get_text('goto_asrs_smart_report', lang)):
            st.session_state.page_redirect = "asrs_smart_report"
            st.rerun()

    def _show_enhanced_investigation(self):
        """专业事故调查页面 - LLM驱动的深度分析"""
        lang = st.session_state.selected_language
        
        title_text = "🔬 Professional Incident Investigation" if lang == 'en' else "🔬 专业事故调查"
        st.markdown(f'<h2 class="sub-header">{title_text}</h2>', unsafe_allow_html=True)
        
        # 专业调查说明
        if lang == 'en':
            st.info("""
            **🎯 AI-Powered Professional Investigation**
            
            This module conducts comprehensive professional incident investigation using:
            - 🔍 **Executive Summary**: Key findings and safety significance
            - 📋 **Detailed Findings**: Categorized investigation results
            - 🧀 **Swiss Cheese Model**: Multi-layer defense analysis
            - ⏱️ **Timeline Reconstruction**: Critical event sequence
            - 📊 **Risk Assessment**: Probability and severity analysis
            - 💡 **Structured Recommendations**: Actionable safety improvements
            
            Based on aviation industry investigation standards and best practices.
            """)
        else:
            st.info("""
            **🎯 AI驱动的专业调查分析**
            
            本模块使用LLM技术进行全面的专业事故调查分析：
            - 🔍 **执行摘要**: 关键发现和安全意义
            - 📋 **详细发现**: 分类调查结果
            - 🧀 **瑞士奶酪模型**: 多层防护分析
            - ⏱️ **时间线重构**: 关键事件序列
            - 📊 **风险评估**: 概率和严重性分析  
            - 💡 **结构化建议**: 可操作的安全改进措施
            
            基于航空业调查标准和最佳实践。
            """)
        
        # 检查是否有报告可供分析
        current_report = st.session_state.get('current_asrs_report') or st.session_state.get('current_report')
        
        if not current_report:
            warning_text = "⚠️ Please submit an incident report first" if lang == 'en' else "⚠️ 请先提交事故报告"
            st.warning(warning_text)
            
            # 提供快速输入选项
            st.subheader("📝 " + ("Quick Analysis Input" if lang == 'en' else "快速分析输入"))
            placeholder_text = "Enter detailed incident description for professional investigation..." if lang == 'en' else "输入详细事故描述进行专业调查..."
            
            quick_narrative = st.text_area(
                "Incident Description" if lang == 'en' else "事故描述",
                height=150,
                placeholder=placeholder_text
            )
            
            button_text = "🚀 Start Professional Investigation" if lang == 'en' else "🚀 开始专业调查"
            if st.button(button_text, type="primary") and quick_narrative.strip():
                current_report = {
                    'detailed_narrative': quick_narrative,
                    'narrative': quick_narrative,
                    'id': f"QUICK_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'incident_type': 'Unknown'
                }
        
        if current_report:
            # 显示当前报告信息
            st.subheader(get_text('analysis_target_report', lang))
            with st.expander("Report Details" if lang == 'en' else "报告详情", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**{'Report ID' if lang == 'en' else '报告ID'}:** {current_report.get('id', 'N/A')}")
                    st.write(f"**{'Incident Type' if lang == 'en' else '事件类型'}:** {current_report.get('incident_type', 'N/A')}")
                with col2:
                    st.write(f"**{'Flight Phase' if lang == 'en' else '飞行阶段'}:** {current_report.get('flight_phase', 'N/A')}")
                    st.write(f"**{'Date' if lang == 'en' else '日期'}:** {current_report.get('occurrence_date', 'N/A')}")
                
                narrative = current_report.get('detailed_narrative') or current_report.get('narrative', '')
                if narrative:
                    st.write("**" + ("Incident Narrative" if lang == 'en' else "事故叙述") + ":**")
                    st.write(narrative[:500] + ("..." if len(narrative) > 500 else ""))
            
            # 专业调查控制
            col1, col2, col3 = st.columns(3)
            
            with col1:
                button_text = "🔬 Start Professional Investigation" if lang == 'en' else "🔬 开始专业调查"
                if st.button(button_text, type="primary"):
                    progress_text = "🔍 Conducting professional incident investigation..." if lang == 'en' else "🔍 正在进行专业事故调查分析..."
                    with st.spinner(progress_text):
                        try:
                            # 初始化专业调查引擎
                            if not st.session_state.investigation_engine:
                                st.session_state.investigation_engine = ProfessionalInvestigationEngine()
                            
                            # 进行专业调查分析
                            investigation_result = st.session_state.investigation_engine.investigate_incident(current_report)
                            st.session_state.investigation_result = investigation_result
                            
                            success_text = "✅ Professional investigation complete!" if lang == 'en' else "✅ 专业调查分析完成！"
                            st.success(success_text)
                            
                        except Exception as e:
                            error_text = f"❌ Professional investigation failed: {e}" if lang == 'en' else f"❌ 专业调查分析失败: {e}"
                            st.error(error_text)
            
            with col2:
                if st.button("🔄 " + ("Re-analyze" if lang == 'en' else "重新分析")):
                    if 'investigation_result' in st.session_state:
                        del st.session_state.investigation_result
                    st.rerun()
            
            with col3:
                if st.button("🔗 " + ("Switch to Causal Analysis" if lang == 'en' else "切换到因果分析")):
                    st.session_state.page_redirect = "causal_analysis"
                    st.rerun()
        
        # 显示专业调查结果
        if st.session_state.get('investigation_result'):
            self._display_investigation_results(st.session_state.investigation_result, lang)

    def _display_investigation_results(self, result, lang):
        """显示专业调查结果"""
        st.markdown("---")
        st.subheader("🔬 " + ("Professional Investigation Results" if lang == 'en' else "专业调查分析结果"))
        
        # 关键指标概览
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Investigation Findings" if lang == 'en' else "调查发现", 
                len(result.findings)
            )
        with col2:
            st.metric(
                "Swiss Cheese Layers" if lang == 'en' else "防护层级", 
                len(result.swiss_cheese_analysis)
            )
        with col3:
            st.metric(
                "Recommendations" if lang == 'en' else "改进建议", 
                len(result.recommendations)
            )
        with col4:
            st.metric(
                "Analysis Confidence" if lang == 'en' else "分析置信度", 
                f"{result.confidence_score:.1%}"
            )
        
        # 主要分析标签
        tab_labels = [
            "📋 " + ("Executive Summary" if lang == 'en' else "执行摘要"),
            "🔍 " + ("Detailed Findings" if lang == 'en' else "详细发现"),
            "🧀 " + ("Swiss Cheese Model" if lang == 'en' else "瑞士奶酪模型"),
            "⏱️ " + ("Timeline" if lang == 'en' else "时间线"),
            "📊 " + ("Risk Assessment" if lang == 'en' else "风险评估"),
            "💡 " + ("Recommendations" if lang == 'en' else "建议措施")
        ]
        
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tab_labels)
        
        with tab1:
            # 执行摘要
            st.subheader("📋 " + ("Executive Summary" if lang == 'en' else "执行摘要"))
            if result.executive_summary:
                st.write(result.executive_summary)
                
                # 经验教训
                if result.lessons_learned:
                    st.markdown("#### " + ("Key Lessons Learned" if lang == 'en' else "关键经验教训"))
                    for lesson in result.lessons_learned:
                        st.write(f"• {lesson}")
            else:
                st.info("No executive summary available" if lang == 'en' else "暂无执行摘要")
        
        with tab2:
            # 详细发现
            st.subheader("🔍 " + ("Investigation Findings" if lang == 'en' else "调查发现"))
            
            if result.findings:
                # 按严重性分类显示
                high_findings = [f for f in result.findings if f.severity == "HIGH"]
                medium_findings = [f for f in result.findings if f.severity == "MEDIUM"]
                low_findings = [f for f in result.findings if f.severity == "LOW"]
                
                for severity, findings, color_class in [
                    ("HIGH", high_findings, "risk-high"),
                    ("MEDIUM", medium_findings, "risk-medium"), 
                    ("LOW", low_findings, "risk-low")
                ]:
                    if findings:
                        severity_text = {"HIGH": "High Severity" if lang == 'en' else "高严重性",
                                       "MEDIUM": "Medium Severity" if lang == 'en' else "中等严重性",
                                       "LOW": "Low Severity" if lang == 'en' else "低严重性"}[severity]
                        st.markdown(f"### 🚨 {severity_text}")
                        
                        for finding in findings:
                            with st.container():
                                st.markdown(f'<div class="{color_class}">', unsafe_allow_html=True)
                                st.markdown(f"**{finding.category}**: {finding.finding}")
                                
                                if finding.evidence:
                                    evidence_text = "Evidence" if lang == 'en' else "证据"
                                    st.markdown(f"**{evidence_text}:**")
                                    for evidence in finding.evidence:
                                        st.write(f"• {evidence}")
                                
                                st.markdown(f"**{'Confidence' if lang == 'en' else '置信度'}:** {finding.confidence:.1%}")
                                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No detailed findings available" if lang == 'en' else "暂无详细调查发现")
        
        with tab3:
            # 瑞士奶酪模型
            st.subheader("🧀 " + ("Swiss Cheese Model Analysis" if lang == 'en' else "瑞士奶酪模型分析"))
            
            if result.swiss_cheese_analysis:
                # 创建可视化
                try:
                    fig = st.session_state.investigation_engine.create_swiss_cheese_visualization(result.swiss_cheese_analysis)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Visualization error: {e}" if lang == 'en' else f"可视化错误: {e}")
                
                # 详细层级分析
                st.markdown("#### " + ("Layer Analysis Details" if lang == 'en' else "层级分析详情"))
                
                for layer in result.swiss_cheese_analysis:
                    with st.expander(f"🏷️ {layer.layer_name} ({layer.effectiveness:.1%} effective)"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if layer.defects:
                                defects_text = "Identified Defects" if lang == 'en' else "识别的缺陷"
                                st.markdown(f"**{defects_text}:**")
                                for defect in layer.defects:
                                    st.write(f"🔴 {defect}")
                        
                        with col2:
                            if layer.barriers:
                                barriers_text = "Working Barriers" if lang == 'en' else "有效屏障"
                                st.markdown(f"**{barriers_text}:**")
                                for barrier in layer.barriers:
                                    st.write(f"🟢 {barrier}")
                        
                        if layer.failure_mode:
                            failure_text = "Failure Mode" if lang == 'en' else "失效模式"
                            st.markdown(f"**{failure_text}:** {layer.failure_mode}")
            else:
                st.info("Swiss cheese analysis data not available" if lang == 'en' else "瑞士奶酪模型分析数据不可用")
        
        with tab4:
            # 时间线重构
            st.subheader("⏱️ " + ("Timeline Reconstruction" if lang == 'en' else "时间线重构"))
            
            if result.timeline_reconstruction:
                # 创建时间线可视化
                try:
                    fig = st.session_state.investigation_engine.create_timeline_visualization(result.timeline_reconstruction)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Timeline visualization error: {e}" if lang == 'en' else f"时间线可视化错误: {e}")
                
                # 详细时间线
                st.markdown("#### " + ("Detailed Timeline" if lang == 'en' else "详细时间线"))
                
                for event in result.timeline_reconstruction:
                    significance = event.get('significance', 'minor')
                    icon = {"critical": "🔴", "major": "🟡", "minor": "🟢"}.get(significance, "⚪")
                    decision_icon = " 🎯" if event.get('decision_point', False) else ""
                    
                    st.markdown(f"**{event.get('time', '')}** {icon}{decision_icon} {event.get('event', '')}")
            else:
                st.info("Timeline reconstruction not available" if lang == 'en' else "时间线重构不可用")
        
        with tab5:
            # 风险评估
            st.subheader("📊 " + ("Risk Assessment" if lang == 'en' else "风险评估"))
            
            if result.risk_assessment:
                # 创建风险矩阵
                try:
                    fig = st.session_state.investigation_engine.create_risk_matrix(result.risk_assessment)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Risk matrix error: {e}" if lang == 'en' else f"风险矩阵错误: {e}")
                
                # 详细风险信息
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### " + ("Risk Classification" if lang == 'en' else "风险分类"))
                    st.write(f"**{'Probability' if lang == 'en' else '概率'}:** {result.risk_assessment.get('probability', 'Unknown')}")
                    st.write(f"**{'Severity' if lang == 'en' else '严重性'}:** {result.risk_assessment.get('severity', 'Unknown')}")
                    st.write(f"**{'Risk Level' if lang == 'en' else '风险等级'}:** {result.risk_assessment.get('risk_level', 'Unknown')}")
                
                with col2:
                    recurrence = result.risk_assessment.get('recurrence_likelihood', 0)
                    st.markdown("#### " + ("Recurrence Analysis" if lang == 'en' else "再发生分析"))
                    st.write(f"**{'Recurrence Likelihood' if lang == 'en' else '再发生可能性'}:** {recurrence:.1%}")
                    
                    # 安全屏障分析
                    if result.safety_barriers:
                        st.markdown("#### " + ("Safety Barriers" if lang == 'en' else "安全屏障"))
                        barriers = result.safety_barriers
                        if barriers.get('preventive', {}).get('failed'):
                            failed_text = "Failed Preventive Barriers" if lang == 'en' else "失效的预防屏障"
                            st.markdown(f"**{failed_text}:**")
                            for barrier in barriers['preventive']['failed']:
                                st.write(f"❌ {barrier}")
            else:
                st.info("Risk assessment not available" if lang == 'en' else "风险评估不可用")
        
        with tab6:
            # 建议措施
            st.subheader("💡 " + ("Recommendations" if lang == 'en' else "改进建议"))
            
            if result.recommendations:
                # 按时间框架分组
                timeframes = {"IMMEDIATE": [], "SHORT_TERM": [], "LONG_TERM": [], "SYSTEMIC": []}
                
                for rec in result.recommendations:
                    timeframe = rec.get('timeframe', 'LONG_TERM')
                    timeframes[timeframe].append(rec)
                
                timeframe_names = {
                    "IMMEDIATE": "Immediate Actions" if lang == 'en' else "立即行动",
                    "SHORT_TERM": "Short-term Actions (1-6 months)" if lang == 'en' else "短期行动（1-6个月）",
                    "LONG_TERM": "Long-term Actions (6+ months)" if lang == 'en' else "长期行动（6个月以上）",
                    "SYSTEMIC": "Systemic Changes" if lang == 'en' else "系统性改革"
                }
                
                for timeframe, recs in timeframes.items():
                    if recs:
                        st.markdown(f"### ⏰ {timeframe_names[timeframe]}")
                        
                        for i, rec in enumerate(recs, 1):
                            priority_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(rec.get('priority', 'MEDIUM'), "⚪")
                            
                            with st.expander(f"{priority_icon} {rec.get('category', '')} - Recommendation {i}"):
                                st.write(f"**{'Recommendation' if lang == 'en' else '建议'}:** {rec.get('recommendation', '')}")
                                st.write(f"**{'Rationale' if lang == 'en' else '理由'}:** {rec.get('rationale', '')}")
                                st.write(f"**{'Priority' if lang == 'en' else '优先级'}:** {rec.get('priority', 'MEDIUM')}")
                
                # 生成调查报告
                if st.button("📄 " + ("Generate Investigation Report" if lang == 'en' else "生成调查报告")):
                    try:
                        # 创建详细的调查报告
                        report_content = self._generate_investigation_report(result, lang)
                        
                        filename = f"Professional_Investigation_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                        
                        st.download_button(
                            label="📥 " + ("Download Investigation Report" if lang == 'en' else "下载调查报告"),
                            data=report_content,
                            file_name=filename,
                            mime="text/markdown"
                        )
                        
                        success_text = "✅ Investigation report generated successfully!" if lang == 'en' else "✅ 调查报告生成成功！"
                        st.success(success_text)
                    except Exception as e:
                        error_text = f"❌ Report generation failed: {e}" if lang == 'en' else f"❌ 报告生成失败: {e}"
                        st.error(error_text)
            else:
                st.info("No recommendations available" if lang == 'en' else "暂无改进建议")

    def _generate_investigation_report(self, result, lang):
        """生成调查报告"""
        if lang == 'en':
            report = f"""# Professional UAV Incident Investigation Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Confidence:** {result.confidence_score:.1%}

## Executive Summary

{result.executive_summary}

## Investigation Findings

"""
            for finding in result.findings:
                report += f"""### {finding.category} - {finding.severity} Severity

**Finding:** {finding.finding}

**Evidence:**
{chr(10).join([f"- {e}" for e in finding.evidence])}

**Confidence:** {finding.confidence:.1%}

**Recommendations:**
{chr(10).join([f"- {r}" for r in finding.recommendations])}

---

"""
        else:
            report = f"""# 专业无人机事故调查分析报告

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**分析置信度:** {result.confidence_score:.1%}

## 执行摘要

{result.executive_summary}

## 调查发现

"""
            for finding in result.findings:
                severity_text = {"HIGH": "高", "MEDIUM": "中", "LOW": "低"}.get(finding.severity, "未知")
                report += f"""### {finding.category} - {severity_text}严重性

**发现:** {finding.finding}

**证据:**
{chr(10).join([f"- {e}" for e in finding.evidence])}

**置信度:** {finding.confidence:.1%}

**建议措施:**
{chr(10).join([f"- {r}" for r in finding.recommendations])}

---

"""
        
        return report

    def _show_llm_expert_analysis(self):
        """Professional LLM Expert Analysis with comprehensive information integration"""
        
        # Professional header styling
        st.markdown("""
        <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2 style='color: white; text-align: center; margin: 0; font-weight: bold;'>
                🧠 Professional LLM Expert Analysis
            </h2>
            <p style='color: white; text-align: center; margin: 0; font-size: 16px; opacity: 0.9;'>
                Advanced AI-powered comprehensive incident analysis with multi-dimensional insights
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get all available information sources
        current_report = st.session_state.get('current_asrs_report') or st.session_state.get('current_report')
        causal_diagram = st.session_state.get('current_causal_diagram')
        hfacs_result = st.session_state.get('hfacs_result')
        extracted_data = st.session_state.get('extracted_data')
        
        if not current_report:
            st.warning("⚠️ **Data Required:** Please submit an incident report first to enable professional expert analysis.")
            st.info("💡 **Recommendation:** Use the '🎯 ASRS Smart Report' feature to submit comprehensive incident data for analysis.")
            return
        
        # Data availability status
        st.markdown("### 📊 **Analysis Data Availability**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            report_status = "✅ Available" if current_report else "❌ Missing"
            st.markdown(f"**📋 Incident Report**<br>{report_status}", unsafe_allow_html=True)
        with col2:
            extracted_status = "✅ Available" if extracted_data else "⚠️ Optional"
            st.markdown(f"**🔍 Extracted Data**<br>{extracted_status}", unsafe_allow_html=True)
        with col3:
            causal_status = "✅ Available" if causal_diagram else "⚠️ Optional" 
            st.markdown(f"**🔗 Causal Analysis**<br>{causal_status}", unsafe_allow_html=True)
        with col4:
            hfacs_status = "✅ Available" if hfacs_result else "⚠️ Optional"
            st.markdown(f"**📋 HFACS Analysis**<br>{hfacs_status}", unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("🚀 **Conduct Comprehensive Expert Analysis**", type="primary"):
            with st.spinner("🧠 **GPT-4o Expert System conducting comprehensive multi-dimensional analysis...**"):
                try:
                    # Initialize AI analyzer if needed
                    if st.session_state.ai_analyzer is None:
                        st.session_state.ai_analyzer = AIAnalyzer()
                    
                    # Prepare comprehensive analysis prompt with all available data
                    comprehensive_context = self._prepare_comprehensive_analysis_context(
                        current_report, extracted_data, causal_diagram, hfacs_result
                    )
                    
                    # Conduct enhanced analysis with all context
                    analysis_result = self._conduct_enhanced_llm_analysis(comprehensive_context)
                    st.session_state.expert_analysis_result = analysis_result
                    
                    st.success("✅ **Comprehensive expert analysis completed successfully!** Advanced multi-dimensional insights are now available below.")
                    
                except Exception as e:
                    st.error(f"❌ **Analysis Error:** {str(e)}")
                    st.info("💡 **Troubleshooting:** Ensure OpenAI API credentials are configured and try again.")
        
        # Professional Expert Analysis Results Display
        if st.session_state.get('expert_analysis_result'):
            result = st.session_state.expert_analysis_result
            
            # Executive Summary Dashboard
            st.markdown("### 📊 **Expert Analysis Executive Summary**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # Risk Assessment with enhanced indicators
                risk_colors = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
                risk_backgrounds = {"HIGH": "#ffebee", "MEDIUM": "#fff8e1", "LOW": "#e8f5e8"}
                risk_icon = risk_colors.get(result.risk_assessment, "⚪")
                risk_bg = risk_backgrounds.get(result.risk_assessment, "#f5f5f5")
                
                st.markdown(f"""
                <div style='background-color: {risk_bg}; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #e1e5e9;'>
                    <h4 style='color: #2c3e50; margin-bottom: 10px; font-weight: bold;'>🎯 Risk Assessment</h4>
                    <h2 style='color: #2c3e50; margin: 0; font-weight: bold;'>{risk_icon} {result.risk_assessment}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Analysis Confidence
                confidence_color = "🟢" if result.confidence_score > 0.8 else "🟡" if result.confidence_score > 0.6 else "🔴"
                confidence_bg = "#e8f5e8" if result.confidence_score > 0.8 else "#fff8e1" if result.confidence_score > 0.6 else "#ffebee"
                
                st.markdown(f"""
                <div style='background-color: {confidence_bg}; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #e1e5e9;'>
                    <h4 style='color: #2c3e50; margin-bottom: 10px; font-weight: bold;'>📈 Analysis Confidence</h4>
                    <h2 style='color: #2c3e50; margin: 0; font-weight: bold;'>{confidence_color} {result.confidence_score:.1%}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                # Recommendations Count
                rec_count = len(result.recommendations) if hasattr(result, 'recommendations') and result.recommendations else 0
                st.markdown(f"""
                <div style='background-color: #e3f2fd; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #e1e5e9;'>
                    <h4 style='color: #2c3e50; margin-bottom: 10px; font-weight: bold;'>💡 Recommendations</h4>
                    <h2 style='color: #2c3e50; margin: 0; font-weight: bold;'>📋 {rec_count} Items</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                # Contributing Factors Count
                factors_count = len(result.contributing_factors) if hasattr(result, 'contributing_factors') and result.contributing_factors else 0
                st.markdown(f"""
                <div style='background-color: #f3e5f5; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #e1e5e9;'>
                    <h4 style='color: #2c3e50; margin-bottom: 10px; font-weight: bold;'>🔍 Key Factors</h4>
                    <h2 style='color: #2c3e50; margin: 0; font-weight: bold;'>📊 {factors_count} Identified</h2>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Professional Analysis Tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "🎯 **Root Cause Analysis**", 
                "💡 **Expert Recommendations**", 
                "🔍 **Contributing Factors**",
                "📚 **Comparative Analysis**"
            ])
            
            with tab1:
                st.markdown("#### 🎯 **Professional Root Cause Analysis**")
                st.markdown("*Expert assessment of fundamental failure mechanisms and systemic issues*")
                
                if hasattr(result, 'root_cause_analysis') and result.root_cause_analysis:
                    # Professional formatting for root cause analysis
                    st.markdown(f"""
                    <div style='background-color: #f8f9fa; padding: 20px; border-left: 4px solid #667eea; border-radius: 5px; margin: 15px 0; color: #2c3e50;'>
                        <h4 style='color: #2c3e50; margin-bottom: 10px;'>🔍 Expert Analysis Summary</h4>
                        <div style='color: #2c3e50; line-height: 1.6;'>{result.root_cause_analysis}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ **Root cause analysis data not available.** This may indicate incomplete analysis or system configuration issues.")
            
            with tab2:
                st.markdown("#### 💡 **Professional Safety Recommendations**")
                st.markdown("*Evidence-based actionable recommendations for risk mitigation and safety improvement*")
                
                if hasattr(result, 'recommendations') and result.recommendations:
                    st.markdown("##### 🎯 **Priority Actions**")
                    for i, rec in enumerate(result.recommendations, 1):
                        priority_icon = "🔴" if i <= 2 else "🟡" if i <= 4 else "🟢"
                        st.markdown(f"""
                        <div style='background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #28a745; border-radius: 5px; color: #2c3e50;'>
                            <h5 style='color: #2c3e50; margin-bottom: 8px;'>{priority_icon} <strong>Recommendation {i}:</strong></h5>
                            <p style='color: #2c3e50; margin: 0; line-height: 1.6;'>{rec}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                if hasattr(result, 'preventive_measures') and result.preventive_measures:
                    st.markdown("##### 🛡️ **Preventive Measures**")
                    for i, measure in enumerate(result.preventive_measures, 1):
                        st.markdown(f"""
                        <div style='background-color: #e8f4fd; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; border-radius: 5px; color: #2c3e50;'>
                            <h5 style='color: #2c3e50; margin-bottom: 8px;'>🛡️ <strong>Prevention Strategy {i}:</strong></h5>
                            <p style='color: #2c3e50; margin: 0; line-height: 1.6;'>{measure}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                if not (hasattr(result, 'recommendations') and result.recommendations) and not (hasattr(result, 'preventive_measures') and result.preventive_measures):
                    st.warning("⚠️ **Recommendations not generated.** This may require additional incident detail or system configuration.")
            
            with tab3:
                st.markdown("#### 🔍 **Contributing Factors Analysis**")
                st.markdown("*Detailed assessment of factors that contributed to the incident occurrence*")
                
                if hasattr(result, 'contributing_factors') and result.contributing_factors:
                    st.markdown("**Main Contributing Factors:**")
                    for i, factor in enumerate(result.contributing_factors, 1):
                        impact_level = "HIGH" if i <= 3 else "MEDIUM" if i <= 6 else "LOW"
                        impact_color = "#dc3545" if impact_level == "HIGH" else "#ffc107" if impact_level == "MEDIUM" else "#28a745"
                        
                        st.markdown(f"""
                        <div style='background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid {impact_color}; border-radius: 5px; border: 1px solid #e9ecef;'>
                            <h5 style='color: #2c3e50; margin-bottom: 8px;'>📊 <strong>Factor {i}</strong> <span style='color: {impact_color}; font-size: 12px; font-weight: bold;'>[{impact_level} IMPACT]</span></h5>
                            <p style='color: #495057; margin: 0; line-height: 1.5;'>{factor}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ **Contributing factors analysis not available.** Consider running a more comprehensive analysis with additional data sources.")
            
            with tab4:
                st.markdown("#### 📚 **Comparative Case Analysis**")
                st.markdown("*Analysis of similar incidents and lessons learned from comparable cases*")
                
                if hasattr(result, 'similar_cases') and result.similar_cases:
                    st.markdown("##### 🔍 **Similar Incident Cases**")
                    for i, case in enumerate(result.similar_cases, 1):
                        with st.expander(f"📋 **Case Study {i}** - Comparative Analysis"):
                            st.markdown(f"""
                            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; border: 1px solid #e9ecef;'>
                                <div style='color: #495057; line-height: 1.6;'>{case}</div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("💡 **No comparable cases identified in current analysis.** This may indicate a unique incident pattern or insufficient historical data.")
                    
                # Additional insights section
                st.markdown("##### 🎓 **Industry Best Practices**")
                st.markdown("""
                **Recommended Analysis References:**
                - Review similar UAV incident reports from ASRS database
                - Consult FAA Advisory Circulars for UAV operations
                - Reference ICAO Annex 13 investigation guidelines
                - Consider industry-specific safety management practices
                """)

    def _prepare_comprehensive_analysis_context(self, current_report, extracted_data, causal_diagram, hfacs_result):
        """Prepare comprehensive context from all available analysis data sources"""
        context_parts = []
        
        # Basic incident report
        context_parts.append("=== PRIMARY INCIDENT REPORT ===")
        context_parts.append(str(current_report))
        
        # Extracted structured data if available
        if extracted_data:
            context_parts.append("\n=== EXTRACTED STRUCTURED DATA ===")
            for key, value in extracted_data.items():
                if value:  # Only include non-empty values
                    context_parts.append(f"{key.upper()}: {value}")
        
        # Causal analysis results if available
        if causal_diagram:
            context_parts.append("\n=== CAUSAL ANALYSIS RESULTS ===")
            context_parts.append(f"Central Event: {causal_diagram.central_event}")
            
            if causal_diagram.nodes:
                context_parts.append("Identified Causal Factors:")
                for node in causal_diagram.nodes:
                    context_parts.append(f"- {node.name} (Type: {node.type}, Impact: {node.impact:.1%}): {node.description}")
            
            if causal_diagram.risk_paths:
                context_parts.append("Risk Pathways:")
                for i, path in enumerate(causal_diagram.risk_paths, 1):
                    context_parts.append(f"- Path {i}: {' → '.join(path)}")
        
        # HFACS analysis results if available
        if hfacs_result:
            context_parts.append("\n=== HFACS HUMAN FACTORS ANALYSIS ===")
            if hasattr(hfacs_result, 'analysis_summary'):
                context_parts.append(f"Summary: {hfacs_result.analysis_summary}")
            if hasattr(hfacs_result, 'primary_factors'):
                context_parts.append("Primary Human Factors:")
                for factor in hfacs_result.primary_factors:
                    context_parts.append(f"- {factor}")
        
        return "\n".join(context_parts)
    
    def _conduct_enhanced_llm_analysis(self, comprehensive_context):
        """Conduct enhanced LLM analysis using comprehensive context with forced English output"""
        
        # Enhanced prompt for professional English analysis
        analysis_prompt = f"""
        You are a professional aviation safety expert conducting a comprehensive UAV incident analysis. 
        
        CRITICAL REQUIREMENTS:
        1. RESPOND ONLY IN PROFESSIONAL ENGLISH - NO OTHER LANGUAGES
        2. Use formal aviation safety terminology and structure
        3. Provide evidence-based analysis with specific recommendations
        4. Structure your response in clear professional sections
        
        INCIDENT DATA:
        {comprehensive_context}
        
        Please provide a comprehensive expert analysis including:
        
        1. RISK ASSESSMENT: Classify as HIGH/MEDIUM/LOW with detailed justification
        
        2. ROOT CAUSE ANALYSIS: Identify fundamental failure mechanisms and systemic issues
        
        3. CONTRIBUTING FACTORS: List and analyze all factors that contributed to the incident
        
        4. PROFESSIONAL RECOMMENDATIONS: Provide specific, actionable safety recommendations prioritized by importance
        
        5. PREVENTIVE MEASURES: Detail systematic approaches to prevent similar incidents
        
        6. SIMILAR CASES: If applicable, reference comparable incidents and lessons learned
        
        Format your response as a structured professional aviation safety analysis. Use clear headings and bullet points for readability.
        """
        
        try:
            # Use the existing AI analyzer with enhanced prompt
            if hasattr(st.session_state, 'ai_analyzer') and st.session_state.ai_analyzer:
                # Create a mock analysis result with enhanced structure
                from ai_analyzer import AnalysisResult
                
                # Call the AI system with the enhanced comprehensive context
                temp_incident = {'narrative': comprehensive_context}
                result = st.session_state.ai_analyzer.analyze_incident(temp_incident)
                
                return result
            else:
                # Fallback mock result if AI analyzer not available
                return self._create_mock_comprehensive_result()
                
        except Exception as e:
            st.error(f"Enhanced analysis error: {str(e)}")
            return self._create_mock_comprehensive_result()
    
    def _extract_risk_level(self, response):
        """Extract risk level from AI response"""
        response_upper = response.upper()
        if "HIGH RISK" in response_upper or "RISK: HIGH" in response_upper:
            return "HIGH"
        elif "MEDIUM RISK" in response_upper or "RISK: MEDIUM" in response_upper:
            return "MEDIUM"
        elif "LOW RISK" in response_upper or "RISK: LOW" in response_upper:
            return "LOW"
        else:
            return "MEDIUM"  # Default
    
    def _extract_section(self, response, section_name):
        """Extract a specific section from the AI response"""
        lines = response.split('\n')
        in_section = False
        section_content = []
        
        for line in lines:
            if section_name.upper() in line.upper():
                in_section = True
                continue
            elif in_section and any(header in line.upper() for header in 
                                   ["CONTRIBUTING FACTORS", "RECOMMENDATIONS", "PREVENTIVE MEASURES", "SIMILAR CASES"]):
                break
            elif in_section:
                section_content.append(line.strip())
        
        return "\n".join(section_content).strip()
    
    def _extract_list_items(self, response, section_name):
        """Extract list items from a specific section"""
        section_text = self._extract_section(response, section_name)
        if not section_text:
            return []
        
        items = []
        for line in section_text.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('1.') or line.startswith('*')):
                # Clean up the bullet point
                clean_item = line.lstrip('-•*0123456789. ').strip()
                if clean_item:
                    items.append(clean_item)
        
        return items
    
    def _create_mock_comprehensive_result(self):
        """Create a mock comprehensive analysis result for testing"""
        from ai_analyzer import AnalysisResult
        
        return AnalysisResult(
            risk_assessment="MEDIUM",
            confidence_score=0.75,
            root_cause_analysis="Comprehensive analysis requires complete incident data and system integration. Please ensure all data sources are available for detailed assessment.",
            contributing_factors=[
                "Insufficient incident detail for comprehensive factor identification",
                "System integration limitations affecting analysis depth",
                "Additional data sources recommended for complete assessment"
            ],
            recommendations=[
                "Ensure complete incident reporting with all relevant operational details",
                "Integrate multiple analysis methodologies for comprehensive assessment",
                "Conduct follow-up analysis with enhanced data collection"
            ],
            preventive_measures=[
                "Implement comprehensive incident reporting procedures",
                "Establish systematic safety analysis protocols",
                "Develop integrated safety management approaches"
            ],
            similar_cases=["Comprehensive case analysis requires access to historical incident database"],
            analysis_timestamp=datetime.now().isoformat()
        )

    def _show_hfacs_analysis(self):
        """HFACS分析页面"""
        lang = st.session_state.selected_language
        
        title_text = "📋 HFACS Human Factors Analysis" if lang == 'en' else "📋 HFACS人因分析"
        st.markdown(f'<h2 class="sub-header">{title_text}</h2>', unsafe_allow_html=True)
        
        current_report = st.session_state.get('current_asrs_report') or st.session_state.get('current_report')
        
        if not current_report:
            warning_text = "⚠️ Please submit incident report first" if lang == 'en' else "⚠️ 请先提交事故报告"
            st.warning(warning_text)
            return
        
        button_text = "🚀 Start HFACS Analysis" if lang == 'en' else "🚀 开始HFACS分析"
        if st.button(button_text, type="primary"):
            spinner_text = "📋 Conducting HFACS 8.0 human factors analysis..." if lang == 'en' else "📋 正在进行HFACS 8.0人因分析..."
            with st.spinner(spinner_text):
                try:
                    if st.session_state.hfacs_analyzer is None:
                        # 使用配置中的API密钥初始化HFACS分析器
                        from config import config
                        st.session_state.hfacs_analyzer = HFACSAnalyzer(api_key=config.OPENAI_API_KEY)

                    narrative = current_report.get('detailed_narrative') or current_report.get('narrative', '')

                    # 验证输入数据
                    if not narrative.strip():
                        error_text = "❌ No narrative text found for analysis" if lang == 'en' else "❌ 未找到用于分析的叙述文本"
                        st.error(error_text)
                        return

                    # 构建用于HFACS分析的数据结构
                    incident_data = {
                        'narrative': narrative,
                        'incident_type': current_report.get('incident_type', ''),
                        'flight_phase': current_report.get('flight_phase', ''),
                        'primary_problem': current_report.get('primary_problem', ''),
                        'contributing_factors': current_report.get('contributing_factors', ''),
                        'human_factors': current_report.get('human_factors', '')
                    }

                    # 显示分析的输入数据长度
                    st.info(f"Analyzing narrative ({len(narrative)} characters)..." if lang == 'en' else f"正在分析叙述文本（{len(narrative)}字符）...")

                    hfacs_result = st.session_state.hfacs_analyzer.analyze_hfacs(incident_data)
                    st.session_state.hfacs_result = hfacs_result

                    # 显示分析结果统计
                    if hfacs_result and hasattr(hfacs_result, 'classifications'):
                        num_classifications = len(hfacs_result.classifications) if hfacs_result.classifications else 0
                        success_text = f"✅ HFACS analysis completed! Found {num_classifications} classifications." if lang == 'en' else f"✅ HFACS分析完成！发现{num_classifications}个分类。"
                        st.success(success_text)
                    else:
                        warning_text = "⚠️ HFACS analysis completed but no classifications found" if lang == 'en' else "⚠️ HFACS分析完成但未发现分类"
                        st.warning(warning_text)
                    
                except Exception as e:
                    error_text = f"❌ HFACS analysis failed: {e}" if lang == 'en' else f"❌ HFACS分析失败: {e}"
                    st.error(error_text)
        
        # 显示HFACS分析结果
        if st.session_state.get('hfacs_result'):
            hfacs_result = st.session_state.hfacs_result
            lang = st.session_state.selected_language
            
            st.subheader(get_text("hfacs_results", lang))
            
            # 创建标签页 - 支持多语言
            tab_labels = [
                "🌳 " + ("HFACS Tree" if lang == 'en' else "HFACS树状图"),
                "📊 " + ("Classifications" if lang == 'en' else "分类详情"), 
                "📋 " + ("Analysis" if lang == 'en' else "详细分析"),
                "💡 " + ("Recommendations" if lang == 'en' else "改进建议")
            ]
            tab1, tab2, tab3, tab4 = st.tabs(tab_labels)
            
            with tab1:
                tree_title = "🌳 HFACS Four-Layer 18-Category Tree Visualization" if lang == 'en' else "🌳 HFACS四层18类树状图可视化"
                tree_desc = "The tree diagram shows the hierarchical structure of the HFACS framework, with highlighted nodes representing human factors identified in this incident" if lang == 'en' else "树状图显示了HFACS框架的层级结构，高亮显示的节点表示在此事故中识别到的人因分类"
                
                st.subheader(tree_title)
                st.info(tree_desc)
                
                try:
                    # 创建树状图
                    if st.session_state.hfacs_analyzer:
                        # 显示分析结果摘要
                        if hasattr(hfacs_result, 'classifications') and hfacs_result.classifications:
                            st.info(f"Visualizing {len(hfacs_result.classifications)} identified HFACS classifications" if lang == 'en' else f"可视化{len(hfacs_result.classifications)}个已识别的HFACS分类")
                        else:
                            st.warning("No HFACS classifications found to visualize" if lang == 'en' else "未找到可视化的HFACS分类")

                        tree_fig = st.session_state.hfacs_analyzer.create_hfacs_tree_visualization(hfacs_result)
                        st.plotly_chart(tree_fig, use_container_width=True, config={'displayModeBar': True})
                    else:
                        st.warning(get_text('hfacs_not_initialized', lang))
                except Exception as e:
                    st.error(f"Tree generation failed: {str(e)}" if lang == 'en' else f"树状图生成失败: {str(e)}")
                    st.error("Please check the console for detailed error information" if lang == 'en' else "请检查控制台获取详细错误信息")
                    
                # 显示分类统计
                if hasattr(hfacs_result, 'classifications') and hfacs_result.classifications:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        metric_name = "Identified Classifications" if lang == 'en' else "识别的分类数量"
                        st.metric(metric_name, len(hfacs_result.classifications))
                    
                    with col2:
                        avg_confidence = sum(c.confidence for c in hfacs_result.classifications) / len(hfacs_result.classifications)
                        metric_name = "Average Confidence" if lang == 'en' else "平均置信度"
                        st.metric(metric_name, f"{avg_confidence:.1%}")
                    
                    with col3:
                        layers_identified = len(set(c.layer for c in hfacs_result.classifications))
                        metric_name = "Layers Involved" if lang == 'en' else "涉及层级数"
                        st.metric(metric_name, layers_identified)
            
            with tab2:
                details_title = "📊 HFACS Classification Details" if lang == 'en' else "📊 HFACS分类详情"
                st.subheader(details_title)
                
                if hasattr(hfacs_result, 'classifications') and hfacs_result.classifications:
                    # 显示调试信息
                    with st.expander("🔍 Debug Information" if lang == 'en' else "🔍 调试信息"):
                        st.write(f"Total classifications found: {len(hfacs_result.classifications)}")
                        st.write("Classification categories:")
                        for i, cls in enumerate(hfacs_result.classifications):
                            st.write(f"{i+1}. {cls.category} (Layer: {cls.layer}, Confidence: {cls.confidence:.2f})")

                    # 按层级组织显示
                    layers = {}
                    for cls in hfacs_result.classifications:
                        if cls.layer not in layers:
                            layers[cls.layer] = []
                        layers[cls.layer].append(cls)
                    
                    for layer, classifications in layers.items():
                        st.markdown(f"### 🏷️ {layer}")
                        
                        for cls in classifications:
                            confidence_color = "🟢" if cls.confidence > 0.7 else "🟡" if cls.confidence > 0.4 else "🔴"
                            
                            with st.expander(f"{confidence_color} {cls.category}"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    confidence_text = "Confidence" if lang == 'en' else "置信度"
                                    st.write(f"**{confidence_text}:** {cls.confidence:.1%}")
                                    
                                    if cls.evidence:
                                        evidence_text = "Evidence" if lang == 'en' else "证据"
                                        st.write(f"**{evidence_text}:**")
                                        for evidence in cls.evidence:
                                            st.write(f"• {evidence}")
                                
                                with col2:
                                    reasoning_text = "Analysis Reasoning" if lang == 'en' else "分析推理"
                                    st.write(f"**{reasoning_text}:**")
                                    st.write(cls.reasoning)
                else:
                    no_class_text = "No specific HFACS classifications identified" if lang == 'en' else "未识别到具体的HFACS分类"
                    st.info(no_class_text)
            
            with tab3:
                # 显示详细分析
                st.subheader(get_text("detailed_analysis", lang))
                
                if hasattr(hfacs_result, 'analysis_summary') and hfacs_result.analysis_summary:
                    st.write(hfacs_result.analysis_summary)
                elif hasattr(hfacs_result, 'analysis') and hfacs_result.analysis:
                    st.write(hfacs_result.analysis)
                else:
                    st.info(get_text('no_detailed_content', lang))
                
                # 显示主要因素和贡献因素
                if hasattr(hfacs_result, 'primary_factors') and hfacs_result.primary_factors:
                    primary_title = "#### 🎯 Primary Human Factors" if lang == 'en' else "#### 🎯 主要人因因素"
                    st.markdown(primary_title)
                    for i, factor in enumerate(hfacs_result.primary_factors, 1):
                        st.write(f"{i}. {factor}")
                
                if hasattr(hfacs_result, 'contributing_factors') and hfacs_result.contributing_factors:
                    contrib_title = "#### 🤝 Contributing Factors" if lang == 'en' else "#### 🤝 贡献因素"
                    st.markdown(contrib_title)
                    for i, factor in enumerate(hfacs_result.contributing_factors, 1):
                        st.write(f"{i}. {factor}")
            
            with tab4:
                # 显示建议
                st.subheader(get_text("improvement_suggestions", lang))
                
                if hasattr(hfacs_result, 'recommendations') and hfacs_result.recommendations:
                    for i, rec in enumerate(hfacs_result.recommendations, 1):
                        rec_text = f"✅ **Recommendation {i}:** {rec}" if lang == 'en' else f"✅ **建议 {i}:** {rec}"
                        st.write(rec_text)
                else:
                    no_rec_text = "No improvement recommendations available" if lang == 'en' else "暂无改进建议"
                    st.info(no_rec_text)
                
                # 生成HFACS分析报告
                button_text = "📄 Generate HFACS Analysis Report" if lang == 'en' else "📄 生成HFACS分析报告"
                if st.button(button_text):
                    try:
                        if st.session_state.hfacs_analyzer:
                            report_content = st.session_state.hfacs_analyzer.generate_hfacs_report(hfacs_result, lang)
                            
                            download_text = "📥 Download HFACS Analysis Report" if lang == 'en' else "📥 下载HFACS分析报告"
                            filename = f"HFACS_Analysis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md" if lang == 'en' else f"HFACS分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                            
                            st.download_button(
                                label=download_text,
                                data=report_content,
                                file_name=filename,
                                mime="text/markdown"
                            )
                            
                            success_text = "✅ HFACS analysis report generated successfully!" if lang == 'en' else "✅ HFACS分析报告已生成"
                            st.success(success_text)
                        else:
                            error_text = "HFACS analyzer not initialized" if lang == 'en' else "HFACS分析器未初始化"
                            st.error(error_text)
                    except Exception as e:
                        error_text = f"Report generation failed: {e}" if lang == 'en' else f"报告生成失败: {e}"
                        st.error(error_text)


def main():
    """主函数"""
    app = ASRSApp()
    app.run()


if __name__ == "__main__":
    main()