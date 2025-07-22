"""
ASRS无人机事故报告智能分析系统 - 修复版
专注核心功能：智能填表 + LLM专家分析 + HFACS识别 + 因果关系分析
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

# 导入核心模块
from data_processor import ASRSDataProcessor
from ai_analyzer import AIAnalyzer
from hfacs_analyzer import HFACSAnalyzer
from smart_form_assistant import SmartFormAssistant
from translations import get_text, get_language_options
from professional_investigation_engine import ProfessionalInvestigationEngine

# 导入增强功能
try:
    from enhanced_ai_analyzer import EnhancedAIAnalyzer
    from advanced_visualizations import AdvancedVisualizations
    from causal_diagram_generator import CausalDiagramGenerator
    ENHANCED_FEATURES_AVAILABLE = True
    CAUSAL_DIAGRAM_AVAILABLE = True
except ImportError:
    ENHANCED_FEATURES_AVAILABLE = False
    CAUSAL_DIAGRAM_AVAILABLE = False
    st.sidebar.warning("⚠️ 增强功能模块未找到，使用基础功能")

# 页面配置
st.set_page_config(
    page_title="ASRS无人机事故智能分析系统",
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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
        self.csv_path = "ASRS_DBOnline 无人机事故报告).csv"
        
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
            st.session_state.selected_language = 'zh'
        
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
            
            # 语言选择
            language_options = get_language_options()
            selected_language = st.selectbox(
                get_text("language_setting", lang),
                options=list(language_options.keys()),
                format_func=lambda x: language_options[x],
                index=list(language_options.keys()).index(st.session_state.selected_language)
            )
            
            # 更新语言设置
            if selected_language != st.session_state.selected_language:
                st.session_state.selected_language = selected_language
                st.rerun()
            
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
        if os.path.exists(self.db_path) and not st.session_state.data_loaded:
            st.session_state.data_loaded = True
            st.sidebar.success(get_text("data_loaded", lang))
        elif not os.path.exists(self.db_path):
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
        st.markdown('<h2 class="sub-header">📊 数据管理</h2>', unsafe_allow_html=True)
        
        if st.button("🔄 加载ASRS历史数据"):
            if os.path.exists(self.csv_path):
                with st.spinner("正在处理ASRS数据..."):
                    try:
                        processor = ASRSDataProcessor(self.db_path)
                        processor.load_csv_data(self.csv_path)
                        st.session_state.data_loaded = True
                        st.success("✅ ASRS历史数据加载成功！")
                    except Exception as e:
                        st.error(f"❌ 数据加载失败: {e}")
            else:
                st.error(f"❌ 找不到数据文件: {self.csv_path}")

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
            # 已经提取过，显示结果
            self._display_extracted_data()
        else:
            # 开始AI提取
            with st.spinner("🧠 GPT-4o正在智能分析叙述并提取关键信息..."):
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
                    
                    st.success("✅ AI字段提取完成！")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ AI分析失败: {e}")
                    # 返回叙述输入阶段
                    if st.button("🔄 重试"):
                        st.session_state.smart_report_stage = 'narrative_input'
                        st.rerun()
    
    def _display_extracted_data(self):
        """显示AI提取的数据"""
        st.success("✅ AI智能提取完成！以下是自动识别和填写的字段：")
        
        # 显示提取统计
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("已提取字段", len(st.session_state.extracted_data))
        with col2:
            completeness = st.session_state.completeness_result.completeness_score if st.session_state.completeness_result else 0
            st.metric("数据完整度", f"{completeness:.1%}")
        with col3:
            confidence_scores = st.session_state.completeness_result.confidence_scores if st.session_state.completeness_result else {}
            avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0
            st.metric("平均置信度", f"{avg_confidence:.1%}")
        with col4:
            missing_count = len(st.session_state.completeness_result.missing_fields) if st.session_state.completeness_result else 0
            st.metric("缺失字段", missing_count)
        
        # 显示提取的字段
        st.subheader("🔍 AI提取字段详情")
        
        # 按类别分组显示
        field_categories = {
            "飞行信息": ["flight_phase", "altitude_agl", "altitude_msl", "flight_conditions", "light_conditions"],
            "天气条件": ["weather_conditions", "wind_speed", "wind_direction", "visibility", "ceiling", "temperature"],
            "无人机信息": ["aircraft_make", "aircraft_model", "aircraft_weight", "propulsion_type", "control_method"],
            "事件分析": ["anomaly_description", "primary_problem", "contributing_factors", "human_factors", "equipment_factors"],
            "其他信息": []  # 将收集其他字段
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
                            st.write(f"值: {value}")
                            st.write(f"置信度: {confidence:.1%}")
                            st.write("---")
                        
                        col_idx = 1 - col_idx
        
        # AI生成的概要
        if st.session_state.extracted_data.get('ai_synopsis'):
            st.subheader("📄 AI生成概要")
            st.info(st.session_state.extracted_data['ai_synopsis'])
        
        # 操作按钮
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 编辑提取结果"):
                st.session_state.edit_mode = True
                st.rerun()
        
        with col2:
            if st.button("➡️ 继续完整性审核", type="primary"):
                st.session_state.smart_report_stage = 'completeness_review'
                st.rerun()
        
        with col3:
            if st.button("🔄 重新提取"):
                st.session_state.extracted_data = {}
                st.rerun()
    
    def _show_completeness_review_stage(self):
        """第三阶段：完整性审核"""
        lang = st.session_state.selected_language
        
        step_title = "🔍 Step 3: AI Completeness Review" if lang == 'en' else "🔍 第三步：AI完整性审核"
        st.subheader(step_title)
        
        if not st.session_state.completeness_result:
            st.error("❌ 缺少完整性分析结果")
            return
        
        result = st.session_state.completeness_result
        
        # 完整性评估概览
        st.markdown("### 📊 完整性评估结果")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 完整性分数
            completeness = result.completeness_score
            if completeness >= 0.8:
                st.success(f"✅ 数据完整度：{completeness:.1%} - 优秀")
                completeness_desc = "数据非常完整，可以进行高质量分析"
            elif completeness >= 0.6:
                st.warning(f"🟡 数据完整度：{completeness:.1%} - 良好")
                completeness_desc = "数据基本完整，建议补充部分信息"
            else:
                st.error(f"🔴 数据完整度：{completeness:.1%} - 需要改进")
                completeness_desc = "数据不够完整，强烈建议补充更多信息"
            
            st.write(completeness_desc)
        
        with col2:
            # 缺失字段统计
            missing_count = len(result.missing_fields)
            if missing_count == 0:
                st.success("🎉 没有关键信息缺失")
            else:
                st.warning(f"⚠️ 缺失 {missing_count} 个关键字段")
        
        # 缺失字段详情
        if result.missing_fields:
            st.markdown("### ❌ 缺失的关键信息")
            for i, missing_field in enumerate(result.missing_fields, 1):
                st.write(f"{i}. {missing_field}")
        
        # AI建议的补充问题
        if result.suggested_questions:
            st.markdown("### ❓ AI建议的补充问题")
            st.info("以下是AI基于航空安全知识生成的专业问题，用于补充缺失信息：")
            
            for i, question in enumerate(result.suggested_questions, 1):
                st.write(f"**问题 {i}:** {question}")
        
        # 操作选择
        st.markdown("---")
        st.subheader("🎯 下一步操作")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("❓ 回答AI问题补充信息", type="primary"):
                st.session_state.smart_questions = result.suggested_questions
                st.session_state.smart_report_stage = 'smart_questions'
                st.rerun()
        
        with col2:
            if st.button("✅ 直接提交报告"):
                st.session_state.smart_report_stage = 'final_review'
                st.rerun()
        
        with col3:
            if st.button("🔙 返回编辑"):
                st.session_state.smart_report_stage = 'smart_extraction'
                st.rerun()
    
    def _show_smart_questions_stage(self):
        """第四阶段：智能问题回答"""
        lang = st.session_state.selected_language
        
        step_title = "❓ Step 4: Answer AI Smart Questions" if lang == 'en' else "❓ 第四步：回答AI智能问题"
        st.subheader(step_title)
        
        description = "Please answer the following AI-generated professional questions to improve report information:" if lang == 'en' else "请回答以下AI生成的专业问题，以完善报告信息："
        st.markdown(description)
        
        if not st.session_state.smart_questions:
            st.error("❌ 没有智能问题数据")
            return
        
        with st.form("smart_questions_form"):
            answers = {}
            
            for i, question in enumerate(st.session_state.smart_questions, 1):
                st.markdown(f"### 问题 {i}")
                st.write(question)
                
                answer = st.text_area(
                    f"回答问题 {i}",
                    key=f"answer_{i}",
                    placeholder="请详细回答这个问题...",
                    height=100
                )
                answers[f"question_{i}"] = {"question": question, "answer": answer}
            
            submitted = st.form_submit_button("📝 提交答案", type="primary")
        
        if submitted:
            # 过滤掉空答案
            valid_answers = {k: v for k, v in answers.items() if v["answer"].strip()}
            st.session_state.question_answers = valid_answers
            
            if valid_answers:
                st.success(f"✅ 已收集 {len(valid_answers)} 个问题的回答")
                
                # 使用LLM处理这些答案，提取更多字段信息
                with st.spinner("🧠 AI正在处理您的回答并更新报告..."):
                    try:
                        # 构建包含原始叙述和问答的完整文本
                        enhanced_narrative = st.session_state.basic_info['narrative'] + "\n\n补充信息：\n"
                        for qa in valid_answers.values():
                            enhanced_narrative += f"问：{qa['question']}\n答：{qa['answer']}\n\n"
                        
                        # 重新分析增强后的叙述
                        enhanced_result = st.session_state.form_assistant.analyze_narrative(
                            enhanced_narrative, st.session_state.extracted_data
                        )
                        
                        # 更新提取的数据
                        st.session_state.extracted_data.update(enhanced_result.extracted_fields)
                        st.session_state.extracted_data['enhanced_narrative'] = enhanced_narrative
                        st.session_state.extracted_data['final_completeness'] = enhanced_result.completeness_score
                        
                        st.success("🎉 信息更新完成！数据完整度有所提升。")
                        
                        # 设置标志表示答案已处理
                        st.session_state.answers_processed = True
                        
                    except Exception as e:
                        st.error(f"❌ 处理回答失败: {e}")
            else:
                st.warning("⚠️ 请至少回答一个问题")
        
        # 显示进入最终审核的按钮（在表单外部，避免Streamlit表单重置问题）
        if hasattr(st.session_state, 'question_answers') and st.session_state.question_answers:
            st.markdown("---")
            st.markdown("### 📋 准备进入最终审核阶段")
            st.info("✅ 您的回答已收集完成，现在可以进入最终审核阶段。")
            
            if st.button("➡️ 进入最终审核", type="primary", key="final_review_btn"):
                st.session_state.smart_report_stage = 'final_review'
                st.rerun()
        
        # 为没有回答问题的用户提供跳过选项
        else:
            st.markdown("---")
            st.markdown("### ⚠️ 跳过问题回答")
            st.warning("您可以选择跳过问题回答直接进入最终审核，但这可能会降低报告的完整性。")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⏭️ 跳过并进入最终审核", key="skip_questions_btn"):
                    # 设置空的问答记录
                    st.session_state.question_answers = {}
                    st.session_state.smart_report_stage = 'final_review'
                    st.rerun()
            
            with col2:
                if st.button("🔄 重新刷新问题", key="refresh_questions_btn"):
                    st.rerun()
    
    def _show_final_review_stage(self):
        """第五阶段：最终审核和提交"""
        lang = st.session_state.selected_language
        
        step_title = "✅ Step 5: Final Review and Submission" if lang == 'en' else "✅ 第五步：最终审核和提交"
        st.subheader(step_title)
        
        # 显示最终数据概览
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("提取字段数", len(st.session_state.extracted_data))
        
        with col2:
            final_completeness = st.session_state.extracted_data.get('final_completeness', 
                                st.session_state.completeness_result.completeness_score if st.session_state.completeness_result else 0)
            st.metric("最终完整度", f"{final_completeness:.1%}")
        
        with col3:
            qa_count = len(st.session_state.question_answers)
            st.metric("补充回答", f"{qa_count} 个")
        
        with col4:
            report_id_preview = f"ASRS_{datetime.now().strftime('%Y%m%d_%H%M')}"
            st.metric("报告ID", report_id_preview[:12])
        
        # 最终报告预览
        st.subheader("📋 最终报告预览")
        
        with st.expander("🔍 查看完整报告数据", expanded=False):
            st.json(st.session_state.extracted_data)
        
        # 提交按钮和后续操作
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 提交ASRS智能报告", type="primary", use_container_width=True):
                # 生成唯一的报告ID
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
                
                st.success("✅ ASRS智能报告提交成功！")
        
        with col2:
            if st.button("🔄 重新开始", use_container_width=True):
                # 清空所有状态
                keys_to_clear = ['smart_report_stage', 'extracted_data', 'completeness_result', 
                               'smart_questions', 'question_answers', 'basic_info', 'report_submitted']
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        # 显示后续分析选项（在提交后显示）
        if st.session_state.get('report_submitted', False):
            st.markdown("---")
            next_analysis_title = "### 🚀 Choose Follow-up Analysis" if lang == 'en' else "### 🚀 选择后续分析"
            st.markdown(next_analysis_title)
            
            success_info = "✅ Report successfully submitted! You can now choose to conduct more in-depth professional analysis:" if lang == 'en' else "✅ 报告已成功提交！现在您可以选择进行更深入的专业分析："
            st.info(success_info)
            
            subcol1, subcol2, subcol3 = st.columns(3)
            
            with subcol1:
                causal_btn_text = "🔗 " + ("Causal Analysis" if lang == 'en' else "因果关系分析")
                if st.button(causal_btn_text, key="goto_causal", use_container_width=True):
                    st.session_state.page_redirect = "causal_analysis"
                    st.rerun()
            
            with subcol2:
                investigation_btn_text = "🔬 " + ("Professional Investigation" if lang == 'en' else "专业事故调查")
                if st.button(investigation_btn_text, key="goto_investigation", use_container_width=True):
                    st.session_state.page_redirect = "professional_investigation"
                    st.rerun()
            
            with subcol3:
                hfacs_btn_text = "📋 " + ("HFACS Analysis" if lang == 'en' else "HFACS分析")
                if st.button(hfacs_btn_text, key="goto_hfacs", use_container_width=True):
                    st.session_state.page_redirect = "hfacs_analysis"
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
            st.subheader("📋 分析目标报告")
            with st.expander("报告详情", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**报告ID:** {current_report.get('id', 'N/A')}")
                    st.write(f"**事件类型:** {current_report.get('incident_type', 'N/A')}")
                with col2:
                    st.write(f"**飞行阶段:** {current_report.get('flight_phase', 'N/A')}")
                    st.write(f"**操作类型:** {current_report.get('aircraft_operator_type', 'N/A')}")
                
                narrative = current_report.get('detailed_narrative') or current_report.get('narrative', '')
                if narrative:
                    st.write("**事故叙述:**")
                    st.write(narrative[:500] + ("..." if len(narrative) > 500 else ""))
            
            # 因果分析控制
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🧠 AI因果分析", type="primary"):
                    with st.spinner("🔍 正在进行智能因果关系分析..."):
                        try:
                            # 初始化因果图生成器
                            if not st.session_state.get('causal_generator'):
                                if CAUSAL_DIAGRAM_AVAILABLE:
                                    model = st.session_state.get('selected_model', 'gpt-4o-mini')
                                    st.session_state.causal_generator = CausalDiagramGenerator(model=model)
                                else:
                                    st.error("❌ 因果图分析功能不可用")
                                    return
                            
                            # 提取叙述
                            narrative = current_report.get('detailed_narrative') or current_report.get('narrative', '')
                            
                            # 生成因果图
                            causal_diagram = st.session_state.causal_generator.generate_causal_diagram(
                                narrative, current_report
                            )
                            
                            st.session_state.current_causal_diagram = causal_diagram
                            st.success("✅ 因果关系分析完成！")
                            
                        except Exception as e:
                            st.error(f"❌ 因果分析失败: {e}")
            
            with col2:
                if st.button("🔄 重新分析"):
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
        """显示因果关系图结果"""
        lang = st.session_state.selected_language
        st.markdown("---")
        st.subheader("🔗 " + ("Causal Analysis Results" if lang == 'en' else "因果关系分析结果"))
        
        # 关键指标概览
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Central Event" if lang == 'en' else "中心事件", causal_diagram.central_event)
        with col2:
            st.metric("Causal Nodes" if lang == 'en' else "因果节点", len(causal_diagram.nodes))
        with col3:
            st.metric("Relationships" if lang == 'en' else "因果关系", len(causal_diagram.relationships))
        with col4:
            st.metric("Risk Paths" if lang == 'en' else "风险路径", len(causal_diagram.risk_paths))
        
        # 主要分析标签
        causal_tab_labels = [
            "🎯 " + ("Causal Diagram" if lang == 'en' else "因果关系图"),
            "📊 " + ("Node Analysis" if lang == 'en' else "节点分析"),
            "⏱️ " + ("Timeline" if lang == 'en' else "时间序列"),
            "🛡️ " + ("Control Points" if lang == 'en' else "控制点"),
            "📋 " + ("Analysis Report" if lang == 'en' else "分析报告")
        ]
        tab1, tab2, tab3, tab4, tab5 = st.tabs(causal_tab_labels)
        
        with tab1:
            if CAUSAL_DIAGRAM_AVAILABLE and st.session_state.get('causal_generator'):
                # 生成可视化
                try:
                    fig = st.session_state.causal_generator.create_causal_visualization(causal_diagram)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"❌ 可视化生成失败: {e}")
            else:
                st.info("🔧 因果关系图可视化功能正在加载中...")
        
        with tab2:
            st.subheader("📊 因果节点详细分析")
            
            if causal_diagram.nodes:
                # 按类型分组显示节点
                node_types = {}
                for node in causal_diagram.nodes:
                    if node.type not in node_types:
                        node_types[node.type] = []
                    node_types[node.type].append(node)
                
                for node_type, nodes in node_types.items():
                    st.markdown(f"#### {node_type.replace('_', ' ').title()}")
                    for node in nodes:
                        risk_level = "🔴" if node.impact > 0.7 else "🟡" if node.impact > 0.4 else "🟢"
                        
                        with st.expander(f"{risk_level} {node.name}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**类别:** {node.category}")
                                st.write(f"**可能性:** {node.likelihood:.1%}")
                                st.write(f"**影响度:** {node.impact:.1%}")
                            with col2:
                                st.write(f"**证据强度:** {node.evidence_strength:.1%}")
                                st.write(f"**描述:** {node.description}")
            else:
                st.info("No causal node data generated" if lang == 'en' else "未生成因果节点数据")
        
        with tab3:
            st.subheader("⏱️ " + ("Event Timeline" if lang == 'en' else "事件时间序列"))
            
            if causal_diagram.timeline:
                timeline_df = pd.DataFrame(causal_diagram.timeline)
                
                # 时间线可视化
                fig = go.Figure()
                
                colors = {'low': '#2ECC71', 'medium': '#F39C12', 'high': '#E74C3C', 'critical': '#8B0000'}
                
                for i, event in enumerate(timeline_df.itertuples()):
                    color = colors.get(event.criticality, '#7F8C8D')
                    
                    fig.add_trace(go.Scatter(
                        x=[i], y=[1],
                        mode='markers+text',
                        marker=dict(size=15, color=color, line=dict(width=2, color='white')),
                        text=[event.time],
                        textposition="top center",
                        name=event.event,
                        hovertemplate=f"<b>{event.time}</b><br>{event.event}<br>关键性: {event.criticality}<extra></extra>"
                    ))
                
                fig.update_layout(
                    title="事故发展时间序列",
                    xaxis_title="时间进程",
                    yaxis=dict(showticklabels=False),
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 详细时间线
                st.markdown("#### 详细时间线")
                for event in causal_diagram.timeline:
                    criticality_icon = {"low": "🟢", "medium": "🟡", "high": "🔴", "critical": "⚫"}.get(event.get('criticality', 'low'), "⚪")
                    st.markdown(f"**{event.get('time')}** {criticality_icon} {event.get('event')}")
            else:
                st.info("No timeline data generated" if lang == 'en' else "未生成时间序列数据")
        
        with tab4:
            st.subheader("🛡️ " + ("Safety Control Points Analysis" if lang == 'en' else "安全控制点分析"))
            
            if causal_diagram.control_points:
                for i, control_point in enumerate(causal_diagram.control_points, 1):
                    effectiveness = control_point.get('effectiveness', 0)
                    effectiveness_icon = "🟢" if effectiveness > 0.7 else "🟡" if effectiveness > 0.4 else "🔴"
                    
                    with st.expander(f"{effectiveness_icon} 控制点 {i}: {control_point.get('name', 'Unknown')}"):
                        st.write(f"**有效性:** {effectiveness:.1%}")
                        st.write(f"**描述:** {control_point.get('description', 'N/A')}")
                        
                        associated_factors = control_point.get('associated_factors', [])
                        if associated_factors:
                            st.write("**关联因素:**")
                            for factor in associated_factors:
                                st.write(f"- {factor}")
            else:
                st.info("No safety control points identified" if lang == 'en' else "未识别到安全控制点")
        
        with tab5:
            st.subheader("📋 " + ("Causal Analysis Report" if lang == 'en' else "因果分析报告"))
            
            # 生成文本报告
            if st.button("📄 " + ("Generate Complete Analysis Report" if lang == 'en' else "生成完整分析报告")):
                try:
                    if lang == 'en':
                        title = "# UAV Incident Causal Analysis Report"
                        summary = "## Analysis Summary"
                        central_event = "**Central Event:**"
                        analysis_time = "**Analysis Time:**"
                        confidence = "**Confidence:**"
                        node_analysis = "## Causal Node Analysis"
                        root_causes = "### Root Causes"
                        contributing = "### Contributing Factors"
                        immediate = "### Immediate Causes"
                        risk_path = "## Risk Path Analysis"
                        path_prefix = "Path"
                        safety_control = "## Safety Control Recommendations"
                        footer = "*This report was automatically generated by AI Causal Analysis System*"
                    else:
                        title = "# 无人机事故因果关系分析报告"
                        summary = "## 分析概要"
                        central_event = "**中心事件:**"
                        analysis_time = "**分析时间:**"
                        confidence = "**置信度:**"
                        node_analysis = "## 因果节点分析"
                        root_causes = "### 根本原因"
                        contributing = "### 贡献因素"
                        immediate = "### 直接原因"
                        risk_path = "## 风险路径分析"
                        path_prefix = "路径"
                        safety_control = "## 安全控制建议"
                        footer = "*本报告由AI因果关系分析系统自动生成*"
                    
                    report_content = f"""{title}

{summary}
- {central_event} {causal_diagram.central_event}
- {analysis_time} {causal_diagram.metadata.get('generation_time', 'N/A')}
- {confidence} {causal_diagram.metadata.get('confidence', 'N/A')}

{node_analysis}
{root_causes}
{chr(10).join([f"- {node.name}: {node.description}" for node in causal_diagram.nodes if node.type == 'root_cause'])}

{contributing}
{chr(10).join([f"- {node.name}: {node.description}" for node in causal_diagram.nodes if node.type == 'contributing_factor'])}

{immediate}
{chr(10).join([f"- {node.name}: {node.description}" for node in causal_diagram.nodes if node.type == 'immediate_cause'])}

{risk_path}
{chr(10).join([f"{path_prefix} {i+1}: {' → '.join(path)}" for i, path in enumerate(causal_diagram.risk_paths)])}

{safety_control}
{chr(10).join([f"- {cp.get('name', '')}: {cp.get('description', '')}" for cp in causal_diagram.control_points])}

---
{footer}
"""
                    
                    download_label = "📥 " + ("Download Causal Analysis Report" if lang == 'en' else "下载因果分析报告")
                    file_prefix = "Causal_Analysis_Report" if lang == 'en' else "因果分析报告"
                    
                    st.download_button(
                        label=download_label,
                        data=report_content,
                        file_name=f"{file_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown"
                    )
                    
                    success_msg = "✅ " + ("Causal analysis report generated" if lang == 'en' else "因果分析报告已生成")
                    st.success(success_msg)
                    
                except Exception as e:
                    st.error(f"❌ 报告生成失败: {e}")

    # 其他页面方法保持不变...
    def _show_smart_report_submission(self):
        """智能报告提交页面（简化版兼容）"""
        st.info("🚀 请使用新的'🎯 ASRS智能报告'功能，它提供了更智能化的报告体验！")
        if st.button("🔗 前往ASRS智能报告"):
            st.session_state.page_redirect = "🎯 ASRS智能报告"
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
            st.subheader("📋 " + ("Analysis Target Report" if lang == 'en' else "分析目标报告"))
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
                    st.session_state.page_redirect = get_text("causal_analysis", lang)
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
        """LLM专家分析页面"""
        lang = st.session_state.selected_language
        
        title_text = "🧠 LLM Expert Analysis" if lang == 'en' else "🧠 LLM专家分析"
        st.markdown(f'<h2 class="sub-header">{title_text}</h2>', unsafe_allow_html=True)
        
        current_report = st.session_state.get('current_asrs_report') or st.session_state.get('current_report')
        
        if not current_report:
            warning_text = "⚠️ Please submit incident report first" if lang == 'en' else "⚠️ 请先提交事故报告"
            st.warning(warning_text)
            return
        
        button_text = "🚀 Start LLM Expert Analysis" if lang == 'en' else "🚀 开始LLM专家分析"
        if st.button(button_text, type="primary"):
            spinner_text = "🧠 GPT-4o expert conducting in-depth analysis..." if lang == 'en' else "🧠 GPT-4o专家正在深度分析中..."
            with st.spinner(spinner_text):
                try:
                    if st.session_state.ai_analyzer is None:
                        st.session_state.ai_analyzer = AIAnalyzer()
                    
                    analysis_result = st.session_state.ai_analyzer.analyze_incident(current_report)
                    st.session_state.expert_analysis_result = analysis_result
                    
                    st.success("✅ LLM专家分析完成！")
                    
                except Exception as e:
                    st.error(f"❌ 分析失败: {e}")
        
        # 显示专家分析结果
        if st.session_state.get('expert_analysis_result'):
            result = st.session_state.expert_analysis_result
            
            # 分析结果展示
            col1, col2, col3 = st.columns(3)
            
            with col1:
                risk_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(result.risk_assessment, "⚪")
                st.metric("风险等级", f"{risk_color} {result.risk_assessment}")
            
            with col2:
                confidence_color = "🟢" if result.confidence_score > 0.7 else "🟡" if result.confidence_score > 0.4 else "🔴"
                st.metric("分析置信度", f"{confidence_color} {result.confidence_score:.1%}")
            
            with col3:
                st.metric("建议措施", len(result.recommendations))
            
            # 详细分析结果
            tab1, tab2, tab3 = st.tabs(["🎯 根本原因", "💡 专家建议", "📚 相似案例"])
            
            with tab1:
                st.subheader("根本原因分析")
                st.write(result.root_cause_analysis)
                
                if result.contributing_factors:
                    st.write("**主要贡献因素:**")
                    for i, factor in enumerate(result.contributing_factors, 1):
                        st.write(f"{i}. {factor}")
            
            with tab2:
                if result.recommendations:
                    st.subheader("专家建议措施")
                    for i, rec in enumerate(result.recommendations, 1):
                        st.write(f"✅ **建议 {i}:** {rec}")
                
                if result.preventive_measures:
                    st.subheader("预防措施")
                    for i, measure in enumerate(result.preventive_measures, 1):
                        st.write(f"🛡️ **预防 {i}:** {measure}")
            
            with tab3:
                if result.similar_cases:
                    st.subheader("相似案例分析")
                    for i, case in enumerate(result.similar_cases, 1):
                        with st.expander(f"相似案例 {i}"):
                            st.write(case)
                else:
                    st.info("未找到相似案例")

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
                        st.session_state.hfacs_analyzer = HFACSAnalyzer()
                    
                    narrative = current_report.get('detailed_narrative') or current_report.get('narrative', '')
                    # 构建用于HFACS分析的数据结构
                    incident_data = {
                        'narrative': narrative,
                        'incident_type': current_report.get('incident_type', ''),
                        'flight_phase': current_report.get('flight_phase', ''),
                        'primary_problem': current_report.get('primary_problem', ''),
                        'contributing_factors': current_report.get('contributing_factors', ''),
                        'human_factors': current_report.get('human_factors', '')
                    }
                    hfacs_result = st.session_state.hfacs_analyzer.analyze_hfacs(incident_data)
                    st.session_state.hfacs_result = hfacs_result
                    
                    success_text = "✅ HFACS analysis completed!" if lang == 'en' else "✅ HFACS分析完成！"
                    st.success(success_text)
                    
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
                        tree_fig = st.session_state.hfacs_analyzer.create_hfacs_tree_visualization(hfacs_result)
                        st.plotly_chart(tree_fig, use_container_width=True)
                    else:
                        st.warning("HFACS分析器未初始化")
                except Exception as e:
                    st.error(f"树状图生成失败: {e}")
                    
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
                    st.info("暂无详细分析内容")
                
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
                            report_content = st.session_state.hfacs_analyzer.generate_hfacs_report(hfacs_result)
                            
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