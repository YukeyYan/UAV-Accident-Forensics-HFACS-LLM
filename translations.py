"""
多语言国际化支持模块
支持中英文切换功能
"""

# 中英文翻译字典
TRANSLATIONS = {
    'zh': {
        # 页面标题
        'page_title': 'ASRS无人机事故智能分析系统',
        'page_icon': '🚁',
        'main_header': '🚁 ASRS无人机事故智能分析系统',
        
        # 侧边栏
        'system_config': '⚙️ 系统配置',
        'select_ai_model': '🤖 选择AI模型',
        'model_help': 'gpt-4o提供更高质量分析，gpt-4o-mini响应更快',
        'select_function_page': '选择功能页面',
        'language_setting': '🌐 语言设置',
        
        # 功能页面选项
        'system_overview': '系统概览',
        'data_management': '数据管理',
        'asrs_smart_report': '🎯 ASRS智能报告',
        'causal_analysis': '🔗 因果关系分析',
        'professional_investigation': '🔬 专业事故调查',
        'llm_expert_analysis': 'LLM专家分析',
        'hfacs_analysis': 'HFACS分析',
        'smart_report_submission': '智能报告提交',
        
        # 系统状态
        'data_loaded': '✅ 历史数据已加载',
        'data_not_loaded': '⚠️ 请先在数据管理页面加载历史数据',
        
        # 系统概览页面
        'system_overview_title': '📊 系统概览',
        'system_goal': '🎯 系统目标',
        'system_goal_desc': '''基于ASRS数据，使用LLM技术提供：
- 🤖 智能表单填写
- 🧠 专家级事故分析
- 📋 HFACS 8.0人因识别
- 📊 专业分析报告''',
        'core_functions': '✨ 核心功能',
        'core_functions_desc': '''🎯 **ASRS智能报告**: 真正的AI智能化报告系统
🔗 **因果关系分析**: 智能生成因果关系图
🔬 **专业事故调查**: 多维度专业分析
📋 **HFACS分析**: 人因分析''',
        'quick_start': '🚀 快速开始',
        'quick_start_desc': '''1. 选择"🎯 ASRS智能报告"
2. 输入详细事故叙述
3. AI自动提取关键信息
4. 选择后续分析类型''',
        'system_status': '🔧 系统状态',
        'enhanced_features': '增强功能',
        'causal_diagram': '因果图分析',
        'historical_data': '历史数据',
        'api_status': 'API状态',
        'available': '✅ 可用',
        'unavailable': '❌ 不可用',
        'loaded': '✅ 已加载',
        'not_loaded': '⚠️ 未加载',
        'configured': '✅ 已配置',
        'not_configured': '❌ 未配置',
        
        # 数据管理页面
        'data_management_title': '📊 数据管理',
        'load_asrs_data': '🔄 加载ASRS历史数据',
        'loading_data': '正在处理ASRS数据...',
        'data_load_success': '✅ ASRS历史数据加载成功！',
        'data_load_failed': '❌ 数据加载失败: {}',
        'file_not_found': '❌ 找不到数据文件: {}',
        
        # ASRS智能报告页面
        'asrs_smart_report_title': '🎯 ASRS智能报告系统',
        'ai_smart_report_desc': '''🧠 真正的AI智能化报告系统
        
🚀 **智能化工作流程**：
1. 📝 输入事故叙述 → 2. 🤖 AI智能提取字段 → 3. 📋 智能审核完整性 → 4. ❓ 生成补充问题 → 5. ✅ 完整报告生成

- 🧠 GPT-4o智能字段提取和自动填表
- 🔍 AI完整性审核和缺失信息识别  
- ❓ 智能生成专业补充问题
- 🔗 无缝集成后续分析功能
- 📊 符合NASA ASRS专业标准''',
        
        # 智能报告流程
        'step1_input_narrative': '📝 第一步：输入事故详细叙述',
        'narrative_input_desc': '请详细描述无人机事故的完整过程，AI将自动从中提取关键信息并智能填写报告表单。',
        'accident_narrative': '事故详细叙述*',
        'narrative_placeholder': '''请详细描述事故过程，包括：
• 时间、地点、天气条件
• 无人机型号、飞行阶段、任务类型
• 事故发生的具体过程和原因
• 操作员的行动和决策
• 事故结果和影响
• 采取的应急措施

示例：2024年3月15日下午2点30分，在北京顺义机场附近进行DJI Phantom 4训练飞行时，无人机在150英尺高度巡航阶段突然失去GPS信号，导致飞行器进入姿态模式。飞行员尝试手动控制但由于强风影响失控坠落...''',
        'basic_info': '📋 基本信息（必填）',
        'occurrence_date': '事故发生日期*',
        'time_of_day': '时间段*',
        'location_city': '发生城市*',
        'pilot_qualification': '操作员资质*',
        'incident_type': '事件类型*',
        'start_ai_analysis': '🚀 开始AI智能分析',
        'fill_all_fields': '❌ 请填写所有必填字段',
        
        # AI提取阶段
        'step2_ai_extraction': '🤖 第二步：AI智能字段提取',
        'ai_analyzing': '🧠 GPT-4o正在智能分析叙述并提取关键信息...',
        'ai_extraction_complete': '✅ AI字段提取完成！',
        'ai_analysis_failed': '❌ AI分析失败: {}',
        'retry': '🔄 重试',
        'extracted_fields': '已提取字段',
        'data_completeness': '数据完整度',
        'avg_confidence': '平均置信度',
        'missing_fields': '缺失字段',
        'extraction_details': '🔍 AI提取字段详情',
        'flight_info': '飞行信息',
        'weather_conditions': '天气条件',
        'uav_info': '无人机信息',
        'event_analysis': '事件分析',
        'other_info': '其他信息',
        'ai_synopsis': '📄 AI生成概要',
        'edit_results': '📝 编辑提取结果',
        'continue_review': '➡️ 继续完整性审核',
        'reextract': '🔄 重新提取',
        
        # 完整性审核阶段
        'step3_completeness_review': '🔍 第三步：AI完整性审核',
        'completeness_assessment': '📊 完整性评估结果',
        'excellent': '优秀',
        'good': '良好',
        'needs_improvement': '需要改进',
        'data_complete_excellent': '数据非常完整，可以进行高质量分析',
        'data_complete_good': '数据基本完整，建议补充部分信息',
        'data_incomplete': '数据不够完整，强烈建议补充更多信息',
        'no_missing_info': '🎉 没有关键信息缺失',
        'missing_critical_fields': '⚠️ 缺失 {} 个关键字段',
        'missing_key_info': '❌ 缺失的关键信息',
        'ai_suggested_questions': '❓ AI建议的补充问题',
        'ai_questions_desc': '以下是AI基于航空安全知识生成的专业问题，用于补充缺失信息：',
        'next_step': '🎯 下一步操作',
        'answer_questions': '❓ 回答AI问题补充信息',
        'submit_directly': '✅ 直接提交报告',
        'return_edit': '🔙 返回编辑',
        
        # 智能问答阶段
        'step4_smart_questions': '❓ 第四步：回答AI智能问题',
        'answer_questions_desc': '请回答以下AI生成的专业问题，以完善报告信息：',
        'no_questions_data': '❌ 没有智能问题数据',
        'question': '问题',
        'answer_question': '回答问题',
        'answer_placeholder': '请详细回答这个问题...',
        'submit_answers': '📝 提交答案',
        'answers_collected': '✅ 已收集 {} 个问题的回答',
        'ai_processing_answers': '🧠 AI正在处理您的回答并更新报告...',
        'info_updated': '🎉 信息更新完成！数据完整度有所提升。',
        'answer_processing_failed': '❌ 处理回答失败: {}',
        'answer_at_least_one': '⚠️ 请至少回答一个问题',
        'ready_final_review': '📋 准备进入最终审核阶段',
        'answers_complete': '✅ 您的回答已收集完成，现在可以进入最终审核阶段。',
        'enter_final_review': '➡️ 进入最终审核',
        'skip_questions': '⚠️ 跳过问题回答',
        'skip_warning': '您可以选择跳过问题回答直接进入最终审核，但这可能会降低报告的完整性。',
        'skip_and_review': '⏭️ 跳过并进入最终审核',
        'refresh_questions': '🔄 重新刷新问题',
        
        # 最终审核阶段
        'step5_final_review': '✅ 第五步：最终审核和提交',
        'final_completeness': '最终完整度',
        'supplementary_answers': '补充回答',
        'report_id': '报告ID',
        'final_report_preview': '📋 最终报告预览',
        'view_complete_report': '🔍 查看完整报告数据',
        'submit_asrs_report': '🚀 提交ASRS智能报告',
        'restart': '🔄 重新开始',
        'report_submitted_success': '✅ ASRS智能报告提交成功！',
        'select_followup_analysis': '🚀 选择后续分析',
        'report_submitted_desc': '✅ 报告已成功提交！现在您可以选择进行更深入的专业分析：',
        'goto_causal_analysis': '🔗 因果关系分析',
        'goto_professional_investigation': '🔬 专业事故调查',
        'goto_hfacs_analysis': '📋 HFACS分析',
        
        # 因果关系分析页面
        'causal_analysis_title': '🔗 智能因果关系分析',
        'ai_causal_analysis_desc': '''🧠 AI驱动的因果关系分析

基于事故叙述自动生成专业的因果关系图：
- 🎯 根本原因识别和分析
- 🔗 多层级因果关系映射
- ⏱️ 事故时间序列重建
- 🛡️ 安全屏障分析和控制点识别
- 📊 交互式可视化和风险路径分析''',
        'submit_report_first': '⚠️ 请先提交事故报告以生成因果关系图',
        'quick_narrative_input': '📝 快速叙述输入',
        'input_narrative_causal': '输入事故叙述进行因果关系分析',
        'narrative_causal_placeholder': '请描述事故的详细过程，包括时间序列、涉及因素、决策点等...',
        'generate_causal_diagram': '🚀 生成因果关系图',
        'analysis_target_report': '📋 分析目标报告',
        'report_details': '报告详情',
        'ai_causal_analysis': '🧠 AI因果分析',
        'causal_analyzing': '🔍 正在进行智能因果关系分析...',
        'causal_analysis_complete': '✅ 因果关系分析完成！',
        'causal_analysis_failed': '❌ 因果分析失败: {}',
        'causal_unavailable': '❌ 因果图分析功能不可用',
        'reanalyze': '🔄 重新分析',
        'switch_to_investigation': '📊 切换到专业调查',
        'causal_results': '🔗 因果关系分析结果',
        'central_event': '中心事件',
        'causal_nodes': '因果节点',
        'causal_relationships': '因果关系',
        'risk_paths': '风险路径',
        'causal_diagram_tab': '🎯 因果关系图',
        'node_analysis_tab': '📊 节点分析',
        'timeline_tab': '⏱️ 时间序列',
        'control_points_tab': '🛡️ 控制点',
        'analysis_report_tab': '📋 分析报告',
        'causal_node_analysis': '📊 因果节点详细分析',
        'no_node_data': '未生成因果节点数据',
        'event_timeline': '⏱️ 事件时间序列',
        'detailed_timeline': '详细时间线',
        'no_timeline_data': '未生成时间序列数据',
        'safety_control_analysis': '🛡️ 安全控制点分析',
        'control_point': '控制点',
        'effectiveness': '有效性',
        'associated_factors': '关联因素',
        'no_control_points': '未识别到安全控制点',
        'causal_analysis_report': '📋 因果分析报告',
        'generate_complete_report': '📄 生成完整分析报告',
        'download_causal_report': '📥 下载因果分析报告',
        'causal_report_generated': '✅ 因果分析报告已生成',
        'report_generation_failed': '❌ 报告生成失败: {}',
        
        # HFACS分析页面
        'hfacs_analysis_title': '📋 HFACS人因分析',
        'start_hfacs_analysis': '🚀 开始HFACS分析',
        'hfacs_analyzing': '📋 正在进行HFACS 8.0人因分析...',
        'hfacs_analysis_complete': '✅ HFACS分析完成！',
        'hfacs_analysis_failed': '❌ HFACS分析失败: {}',
        'hfacs_results': '📊 HFACS 8.0人因分析结果',
        'detailed_analysis': '详细分析',
        'improvement_suggestions': '改进建议',
        
        # LLM专家分析页面
        'llm_expert_analysis_title': '🧠 LLM专家分析',
        'start_llm_analysis': '🚀 开始LLM专家分析',
        'llm_analyzing': '🧠 GPT-4o专家正在深度分析中...',
        'llm_analysis_complete': '✅ LLM专家分析完成！',
        'llm_analysis_failed': '❌ 分析失败: {}',
        'risk_level': '风险等级',
        'analysis_confidence': '分析置信度',
        'recommended_measures': '建议措施',
        'root_cause_analysis': '🎯 根本原因',
        'expert_recommendations': '💡 专家建议',
        'similar_cases': '📚 相似案例',
        'root_cause_analysis_detail': '根本原因分析',
        'main_contributing_factors': '**主要贡献因素:**',
        'expert_recommended_measures': '专家建议措施',
        'preventive_measures': '预防措施',
        'similar_case_analysis': '相似案例分析',
        'similar_case': '相似案例',
        'no_similar_cases': '未找到相似案例',
        
        # 专业事故调查页面
        'professional_investigation_title': '🔬 专业事故调查',
        'start_professional_analysis': '🚀 开始专业调查分析',
        'professional_analyzing': '🔬 正在进行专业级事故调查分析...',
        'professional_analysis_complete': '✅ 专业调查分析完成！',
        'professional_analysis_failed': '❌ 专业分析失败: {}',
        'enhanced_investigation_unavailable': '🔧 增强调查功能需要相关模块支持',
        
        # 智能报告提交页面（兼容）
        'use_new_smart_report': '🚀 请使用新的\'🎯 ASRS智能报告\'功能，它提供了更智能化的报告体验！',
        'goto_asrs_smart_report': '🔗 前往ASRS智能报告',
        
        # 通用按钮和操作
        'confirm': '确认',
        'cancel': '取消',
        'save': '保存',
        'delete': '删除',
        'edit': '编辑',
        'submit': '提交',
        'reset': '重置',
        'back': '返回',
        'next': '下一步',
        'previous': '上一步',
        'close': '关闭',
        'loading': '加载中...',
        'processing': '处理中...',
        'complete': '完成',
        'failed': '失败',
        'success': '成功',
        'error': '错误',
        'warning': '警告',
        'info': '信息',
        
        # 时间选项
        'time_0001_0600': '0001-0600',
        'time_0601_1200': '0601-1200',
        'time_1201_1800': '1201-1800',
        'time_1801_2400': '1801-2400',
        
        # 操作员资质选项
        'part_107': 'Part 107 Remote Pilot Certificate',
        'part_61': 'Part 61 Pilot Certificate',
        'military_training': 'Military UAV Training',
        'manufacturer_training': 'Manufacturer Training',
        'other': 'Other',
        'none': 'None',
        
        # 事件类型选项
        'nmac': 'Near Mid-Air Collision (NMAC)',
        'airspace_violation': 'Airspace Violation',
        'loss_of_control': 'Loss of Control',
        'system_malfunction': 'System Malfunction',
        'communication_failure': 'Communication Failure',
        'weather_related': 'Weather Related',
        'runway_incursion': 'Runway Incursion',
        'ground_collision': 'Ground Collision',
        'emergency_landing': 'Emergency Landing',
    },
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
        'system_goal': '🎯 System Objectives',
        'system_goal_desc': '''Based on ASRS data, using LLM technology to provide:
- 🤖 Intelligent form completion
- 🧠 Expert-level incident analysis
- 📋 HFACS 8.0 human factors identification
- 📊 Professional analysis reports''',
        'core_functions': '✨ Core Functions',
        'core_functions_desc': '''🎯 **ASRS Smart Report**: True AI intelligent reporting system
🔗 **Causal Analysis**: Intelligent causal diagram generation
🔬 **Professional Investigation**: Multi-dimensional professional analysis
📋 **HFACS Analysis**: Human factors analysis''',
        'quick_start': '🚀 Quick Start',
        'quick_start_desc': '''1. Select "🎯 ASRS Smart Report"
2. Input detailed incident narrative
3. AI auto-extracts key information
4. Choose follow-up analysis type''',
        'system_status': '🔧 System Status',
        'enhanced_features': 'Enhanced Features',
        'causal_diagram': 'Causal Diagram Analysis',
        'historical_data': 'Historical Data',
        'api_status': 'API Status',
        'available': '✅ Available',
        'unavailable': '❌ Unavailable',
        'loaded': '✅ Loaded',
        'not_loaded': '⚠️ Not Loaded',
        'configured': '✅ Configured',
        'not_configured': '❌ Not Configured',
        
        # Data management page
        'data_management_title': '📊 Data Management',
        'load_asrs_data': '🔄 Load ASRS Historical Data',
        'loading_data': 'Processing ASRS data...',
        'data_load_success': '✅ ASRS historical data loaded successfully!',
        'data_load_failed': '❌ Data loading failed: {}',
        'file_not_found': '❌ Data file not found: {}',
        
        # ASRS smart report page
        'asrs_smart_report_title': '🎯 ASRS Smart Report System',
        'ai_smart_report_desc': '''🧠 True AI Intelligent Reporting System
        
🚀 **Intelligent Workflow**：
1. 📝 Input incident narrative → 2. 🤖 AI smart field extraction → 3. 📋 Intelligent completeness review → 4. ❓ Generate supplementary questions → 5. ✅ Complete report generation

- 🧠 GPT-4o intelligent field extraction and auto-form completion
- 🔍 AI completeness review and missing information identification
- ❓ Intelligently generate professional supplementary questions
- 🔗 Seamless integration with follow-up analysis functions
- 📊 Compliant with NASA ASRS professional standards''',
        
        # Smart report process
        'step1_input_narrative': '📝 Step 1: Input Detailed Incident Narrative',
        'narrative_input_desc': 'Please describe the complete UAV incident process in detail. AI will automatically extract key information and intelligently complete the report form.',
        'accident_narrative': 'Detailed Incident Narrative*',
        'narrative_placeholder': '''Please describe the incident process in detail, including:
• Time, location, weather conditions
• UAV model, flight phase, mission type
• Specific process and causes of the incident
• Operator actions and decisions
• Incident results and impacts
• Emergency measures taken

Example: At 2:30 PM on March 15, 2024, during DJI Phantom 4 training flight near Beijing Shunyi Airport, the UAV suddenly lost GPS signal at 150 feet altitude during cruise phase, causing the aircraft to enter attitude mode. The pilot attempted manual control but lost control due to strong wind and crashed...''',
        'basic_info': '📋 Basic Information (Required)',
        'occurrence_date': 'Incident Date*',
        'time_of_day': 'Time Period*',
        'location_city': 'Location City*',
        'pilot_qualification': 'Operator Qualification*',
        'incident_type': 'Incident Type*',
        'start_ai_analysis': '🚀 Start AI Intelligent Analysis',
        'fill_all_fields': '❌ Please fill in all required fields',
        
        # AI extraction stage
        'step2_ai_extraction': '🤖 Step 2: AI Intelligent Field Extraction',
        'ai_analyzing': '🧠 GPT-4o is intelligently analyzing narrative and extracting key information...',
        'ai_extraction_complete': '✅ AI field extraction complete!',
        'ai_analysis_failed': '❌ AI analysis failed: {}',
        'retry': '🔄 Retry',
        'extracted_fields': 'Extracted Fields',
        'data_completeness': 'Data Completeness',
        'avg_confidence': 'Average Confidence',
        'missing_fields': 'Missing Fields',
        'extraction_details': '🔍 AI Extraction Field Details',
        'flight_info': 'Flight Information',
        'weather_conditions': 'Weather Conditions',
        'uav_info': 'UAV Information',
        'event_analysis': 'Event Analysis',
        'other_info': 'Other Information',
        'ai_synopsis': '📄 AI Generated Synopsis',
        'edit_results': '📝 Edit Extraction Results',
        'continue_review': '➡️ Continue Completeness Review',
        'reextract': '🔄 Re-extract',
        
        # Completeness review stage
        'step3_completeness_review': '🔍 Step 3: AI Completeness Review',
        'completeness_assessment': '📊 Completeness Assessment Results',
        'excellent': 'Excellent',
        'good': 'Good',
        'needs_improvement': 'Needs Improvement',
        'data_complete_excellent': 'Data is very complete, high-quality analysis can be performed',
        'data_complete_good': 'Data is basically complete, suggest supplementing some information',
        'data_incomplete': 'Data is not complete enough, strongly recommend supplementing more information',
        'no_missing_info': '🎉 No critical information missing',
        'missing_critical_fields': '⚠️ Missing {} critical fields',
        'missing_key_info': '❌ Missing Critical Information',
        'ai_suggested_questions': '❓ AI Suggested Supplementary Questions',
        'ai_questions_desc': 'The following are professional questions generated by AI based on aviation safety knowledge to supplement missing information:',
        'next_step': '🎯 Next Step',
        'answer_questions': '❓ Answer AI Questions to Supplement Information',
        'submit_directly': '✅ Submit Report Directly',
        'return_edit': '🔙 Return to Edit',
        
        # Smart Q&A stage
        'step4_smart_questions': '❓ Step 4: Answer AI Smart Questions',
        'answer_questions_desc': 'Please answer the following AI-generated professional questions to improve report information:',
        'no_questions_data': '❌ No smart question data',
        'question': 'Question',
        'answer_question': 'Answer Question',
        'answer_placeholder': 'Please answer this question in detail...',
        'submit_answers': '📝 Submit Answers',
        'answers_collected': '✅ Collected {} question answers',
        'ai_processing_answers': '🧠 AI is processing your answers and updating the report...',
        'info_updated': '🎉 Information update complete! Data completeness has improved.',
        'answer_processing_failed': '❌ Answer processing failed: {}',
        'answer_at_least_one': '⚠️ Please answer at least one question',
        'ready_final_review': '📋 Ready for Final Review Stage',
        'answers_complete': '✅ Your answers have been collected. You can now proceed to the final review stage.',
        'enter_final_review': '➡️ Enter Final Review',
        'skip_questions': '⚠️ Skip Question Answering',
        'skip_warning': 'You can choose to skip question answering and go directly to final review, but this may reduce report completeness.',
        'skip_and_review': '⏭️ Skip and Enter Final Review',
        'refresh_questions': '🔄 Refresh Questions',
        
        # Final review stage
        'step5_final_review': '✅ Step 5: Final Review and Submission',
        'final_completeness': 'Final Completeness',
        'supplementary_answers': 'Supplementary Answers',
        'report_id': 'Report ID',
        'final_report_preview': '📋 Final Report Preview',
        'view_complete_report': '🔍 View Complete Report Data',
        'submit_asrs_report': '🚀 Submit ASRS Smart Report',
        'restart': '🔄 Restart',
        'report_submitted_success': '✅ ASRS smart report submitted successfully!',
        'select_followup_analysis': '🚀 Select Follow-up Analysis',
        'report_submitted_desc': '✅ Report submitted successfully! You can now choose to conduct more in-depth professional analysis:',
        'goto_causal_analysis': '🔗 Causal Analysis',
        'goto_professional_investigation': '🔬 Professional Investigation',
        'goto_hfacs_analysis': '📋 HFACS Analysis',
        
        # Causal analysis page
        'causal_analysis_title': '🔗 Intelligent Causal Analysis',
        'ai_causal_analysis_desc': '''🧠 AI-Driven Causal Analysis

Automatically generate professional causal diagrams based on incident narratives:
- 🎯 Root cause identification and analysis
- 🔗 Multi-level causal relationship mapping
- ⏱️ Incident timeline reconstruction
- 🛡️ Safety barrier analysis and control point identification
- 📊 Interactive visualization and risk path analysis''',
        'submit_report_first': '⚠️ Please submit an incident report first to generate causal diagram',
        'quick_narrative_input': '📝 Quick Narrative Input',
        'input_narrative_causal': 'Input incident narrative for causal analysis',
        'narrative_causal_placeholder': 'Please describe the detailed incident process, including timeline, involved factors, decision points, etc...',
        'generate_causal_diagram': '🚀 Generate Causal Diagram',
        'analysis_target_report': '📋 Analysis Target Report',
        'report_details': 'Report Details',
        'ai_causal_analysis': '🧠 AI Causal Analysis',
        'causal_analyzing': '🔍 Conducting intelligent causal analysis...',
        'causal_analysis_complete': '✅ Causal analysis complete!',
        'causal_analysis_failed': '❌ Causal analysis failed: {}',
        'causal_unavailable': '❌ Causal diagram analysis function unavailable',
        'reanalyze': '🔄 Re-analyze',
        'switch_to_investigation': '📊 Switch to Professional Investigation',
        'causal_results': '🔗 Causal Analysis Results',
        'central_event': 'Central Event',
        'causal_nodes': 'Causal Nodes',
        'causal_relationships': 'Causal Relationships',
        'risk_paths': 'Risk Paths',
        'causal_diagram_tab': '🎯 Causal Diagram',
        'node_analysis_tab': '📊 Node Analysis',
        'timeline_tab': '⏱️ Timeline',
        'control_points_tab': '🛡️ Control Points',
        'analysis_report_tab': '📋 Analysis Report',
        'causal_node_analysis': '📊 Detailed Causal Node Analysis',
        'no_node_data': 'No causal node data generated',
        'event_timeline': '⏱️ Event Timeline',
        'detailed_timeline': 'Detailed Timeline',
        'no_timeline_data': 'No timeline data generated',
        'safety_control_analysis': '🛡️ Safety Control Point Analysis',
        'control_point': 'Control Point',
        'effectiveness': 'Effectiveness',
        'associated_factors': 'Associated Factors',
        'no_control_points': 'No safety control points identified',
        'causal_analysis_report': '📋 Causal Analysis Report',
        'generate_complete_report': '📄 Generate Complete Analysis Report',
        'download_causal_report': '📥 Download Causal Analysis Report',
        'causal_report_generated': '✅ Causal analysis report generated',
        'report_generation_failed': '❌ Report generation failed: {}',
        
        # HFACS analysis page
        'hfacs_analysis_title': '📋 HFACS Human Factors Analysis',
        'start_hfacs_analysis': '🚀 Start HFACS Analysis',
        'hfacs_analyzing': '📋 Conducting HFACS 8.0 human factors analysis...',
        'hfacs_analysis_complete': '✅ HFACS analysis complete!',
        'hfacs_analysis_failed': '❌ HFACS analysis failed: {}',
        'hfacs_results': '📊 HFACS 8.0 Human Factors Analysis Results',
        'detailed_analysis': 'Detailed Analysis',
        'improvement_suggestions': 'Improvement Suggestions',
        
        # LLM expert analysis page
        'llm_expert_analysis_title': '🧠 LLM Expert Analysis',
        'start_llm_analysis': '🚀 Start LLM Expert Analysis',
        'llm_analyzing': '🧠 GPT-4o expert conducting in-depth analysis...',
        'llm_analysis_complete': '✅ LLM expert analysis complete!',
        'llm_analysis_failed': '❌ Analysis failed: {}',
        'risk_level': 'Risk Level',
        'analysis_confidence': 'Analysis Confidence',
        'recommended_measures': 'Recommended Measures',
        'root_cause_analysis': '🎯 Root Cause Analysis',
        'expert_recommendations': '💡 Expert Recommendations',
        'similar_cases': '📚 Similar Cases',
        'root_cause_analysis_detail': 'Root Cause Analysis',
        'main_contributing_factors': '**Main Contributing Factors:**',
        'expert_recommended_measures': 'Expert Recommended Measures',
        'preventive_measures': 'Preventive Measures',
        'similar_case_analysis': 'Similar Case Analysis',
        'similar_case': 'Similar Case',
        'no_similar_cases': 'No similar cases found',
        
        # Professional investigation page
        'professional_investigation_title': '🔬 Professional Investigation',
        'start_professional_analysis': '🚀 Start Professional Investigation Analysis',
        'professional_analyzing': '🔬 Conducting professional-level incident investigation analysis...',
        'professional_analysis_complete': '✅ Professional investigation analysis complete!',
        'professional_analysis_failed': '❌ Professional analysis failed: {}',
        'enhanced_investigation_unavailable': '🔧 Enhanced investigation functions require related module support',
        
        # Smart report submission page (compatibility)
        'use_new_smart_report': '🚀 Please use the new \'🎯 ASRS Smart Report\' function, which provides a more intelligent reporting experience!',
        'goto_asrs_smart_report': '🔗 Go to ASRS Smart Report',
        
        # Common buttons and operations
        'confirm': 'Confirm',
        'cancel': 'Cancel',
        'save': 'Save',
        'delete': 'Delete',
        'edit': 'Edit',
        'submit': 'Submit',
        'reset': 'Reset',
        'back': 'Back',
        'next': 'Next',
        'previous': 'Previous',
        'close': 'Close',
        'loading': 'Loading...',
        'processing': 'Processing...',
        'complete': 'Complete',
        'failed': 'Failed',
        'success': 'Success',
        'error': 'Error',
        'warning': 'Warning',
        'info': 'Info',
        
        # Time options
        'time_0001_0600': '0001-0600',
        'time_0601_1200': '0601-1200',
        'time_1201_1800': '1201-1800',
        'time_1801_2400': '1801-2400',
        
        # Operator qualification options
        'part_107': 'Part 107 Remote Pilot Certificate',
        'part_61': 'Part 61 Pilot Certificate',
        'military_training': 'Military UAV Training',
        'manufacturer_training': 'Manufacturer Training',
        'other': 'Other',
        'none': 'None',
        
        # Incident type options
        'nmac': 'Near Mid-Air Collision (NMAC)',
        'airspace_violation': 'Airspace Violation',
        'loss_of_control': 'Loss of Control',
        'system_malfunction': 'System Malfunction',
        'communication_failure': 'Communication Failure',
        'weather_related': 'Weather Related',
        'runway_incursion': 'Runway Incursion',
        'ground_collision': 'Ground Collision',
        'emergency_landing': 'Emergency Landing',
    }
}

def get_text(key: str, lang: str = 'zh') -> str:
    """
    获取指定语言的文本
    
    Args:
        key: 文本键名
        lang: 语言代码 ('zh' 或 'en')
        
    Returns:
        翻译后的文本，如果找不到则返回键名
    """
    return TRANSLATIONS.get(lang, {}).get(key, key)

def get_language_options() -> dict:
    """获取语言选项"""
    return {
        'zh': '中文',
        'en': 'English'
    }

def get_available_languages() -> list:
    """获取可用的语言列表"""
    return list(TRANSLATIONS.keys())