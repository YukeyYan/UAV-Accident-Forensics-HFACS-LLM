# 🧹 UAV项目整理计划

## 🎯 核心需求明确
- ASRS报告提交系统
- 智能填表功能 
- LLM代替人类专家分析
- HFACS 8.0自动识别
- 专业级结果输出

## 📁 文件分类

### ✅ 核心保留文件
1. `streamlit_app.py` - 主应用（需大幅简化）
2. `smart_form_assistant.py` - 智能填表（核心功能）
3. `ai_analyzer.py` - LLM专家分析（核心功能）
4. `hfacs_analyzer.py` - HFACS 8.0分析（核心功能）
5. `data_processor.py` - 数据处理
6. `ASRS_DBOnline 无人机事故报告).csv` - 数据源
7. `asrs_data.db` - 数据库
8. `requirements.txt` - 依赖包
9. `config.py` - 配置文件

### ❌ 删除冗余文件
1. `realtime_risk_engine.py` - 实时风险评估（过于复杂）
2. `natural_language_query.py` - 自然语言查询（非核心需求）
3. `llm_innovation_features.py` - 创新功能集成（冗余复杂）
4. `enhanced_visualizations.py` - 高级可视化（非必需）
5. `knowledge_graph.py` - 知识图谱（过于复杂）
6. `web_components/` - Node.js组件（完全不需要）
7. `test_*.py` - 测试文件（清理）
8. 大量总结文档 - 文档混乱

### 📋 简化主应用功能
**保留页面：**
- 系统概览
- 数据管理 
- 智能报告提交（智能填表）
- LLM专家分析
- HFACS 8.0分析

**删除页面：**
- 实时风险评估
- 自然语言查询
- 高级可视化
- 各种复杂功能

## 🎯 最终目标
简洁、专业、高效的ASRS智能分析系统，专注核心价值。