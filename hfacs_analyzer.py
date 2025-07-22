"""
HFACS 8.0 人因分析模块
基于Human Factors Analysis and Classification System 8.0框架进行事故分析
参考GT_Run_Auto.py的专业实现
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import os
import re
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import networkx as nx

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 18个HFACS 8.0分类定义（来自GT_Run_Auto.py）
HFACS_CATEGORIES = [
    "UNSAFE ACTS—Errors—Performance/Skill-Based",
    "UNSAFE ACTS—Errors—Judgement & Decision-Making",
    "UNSAFE ACTS—Known Deviations",
    "PRECONDITIONS—Physical Environment",
    "PRECONDITIONS—Technological Environment",
    "PRECONDITIONS—Team Coordination/Communication",
    "PRECONDITIONS—Training Conditions",
    "PRECONDITIONS—Mental Awareness (Attention)",
    "PRECONDITIONS—State of Mind",
    "PRECONDITIONS—Adverse Physiological",
    "SUPERVISION/LEADERSHIP—Unit Safety Culture",
    "SUPERVISION/LEADERSHIP—Supervisory Known Deviations",
    "SUPERVISION/LEADERSHIP—Ineffective Supervision",
    "SUPERVISION/LEADERSHIP—Ineffective Planning & Coordination",
    "ORGANIZATIONAL INFLUENCES—Climate/Culture",
    "ORGANIZATIONAL INFLUENCES—Policy/Procedures/Process",
    "ORGANIZATIONAL INFLUENCES—Resource Support",
    "ORGANIZATIONAL INFLUENCES—Training Program Issues"
]

# HFACS四个层级
HFACS_LAYERS = [
    "UNSAFE ACTS",
    "PRECONDITIONS",
    "SUPERVISION/LEADERSHIP",
    "ORGANIZATIONAL INFLUENCES"
]

# 类别到层级的映射
CATEGORY_TO_LAYER = {}
for category in HFACS_CATEGORIES:
    for layer in HFACS_LAYERS:
        if category.startswith(layer):
            CATEGORY_TO_LAYER[category] = layer
            break

@dataclass
class HFACSClassification:
    """HFACS分类结果"""
    category: str
    layer: str
    confidence: float
    reasoning: str
    evidence: List[str]

@dataclass
class HFACSAnalysisResult:
    """HFACS分析结果"""
    classifications: List[HFACSClassification]
    primary_factors: List[str]
    contributing_factors: List[str]
    recommendations: List[str]
    analysis_summary: str
    confidence_score: float
    analysis_timestamp: str
    visualization_data: Dict

class HFACSAnalyzer:
    """HFACS 8.0 分析器 - 基于GT_Run_Auto.py的专业实现"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化HFACS分析器

        Args:
            api_key: OpenAI API密钥
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY') or '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'

        if not self.api_key:
            logger.warning("未设置OpenAI API密钥，将使用模拟分析")
            self.use_mock = True
        else:
            self.use_mock = False

        # 系统提示词（基于GT_Run_Auto.py的专业提示词，进一步完善）
        self.system_prompt = """You are an expert aviation-safety analyst specialised in HFACS (Human Factors Analysis and Classification System) classification.

Your mission is to analyze aviation incident narratives and classify human factors according to the HFACS 8.0 framework.

CLASSIFICATION CRITERIA:
Analyze the incident narrative and identify ALL applicable HFACS categories and layers with high precision.

The 18 HFACS categories are organized into 4 layers:

LAYER 1: UNSAFE ACTS
1. UNSAFE ACTS—Errors—Performance/Skill-Based: Actions or inactions by operators that deviate from expected practice due to inadequate skill or knowledge
2. UNSAFE ACTS—Errors—Judgement & Decision-Making: Poor decisions made by operators, including risk assessment failures
3. UNSAFE ACTS—Known Deviations: Willful violations of rules, regulations, or procedures

LAYER 2: PRECONDITIONS 
4. PRECONDITIONS—Physical Environment: Adverse conditions in the physical operating environment
5. PRECONDITIONS—Technological Environment: Problems with equipment design, displays, interfaces, automation
6. PRECONDITIONS—Team Coordination/Communication: Breakdown in team coordination or communication
7. PRECONDITIONS—Training Conditions: Inadequate individual training or preparation
8. PRECONDITIONS—Mental Awareness (Attention): Reduced situational awareness, attention problems, task fixation
9. PRECONDITIONS—State of Mind: Adverse mental state affecting performance (stress, complacency, overconfidence)
10. PRECONDITIONS—Adverse Physiological: Physical impairment affecting performance (fatigue, illness, medication effects)

LAYER 3: SUPERVISION/LEADERSHIP
11. SUPERVISION/LEADERSHIP—Unit Safety Culture: Local unit culture that tolerates or encourages unsafe practices
12. SUPERVISION/LEADERSHIP—Supervisory Known Deviations: Supervisors knowingly allowing violations of safety rules
13. SUPERVISION/LEADERSHIP—Ineffective Supervision: Inadequate oversight, monitoring, or guidance by supervisors
14. SUPERVISION/LEADERSHIP—Ineffective Planning & Coordination: Poor planning, scheduling, or resource coordination by leadership

LAYER 4: ORGANIZATIONAL INFLUENCES
15. ORGANIZATIONAL INFLUENCES—Climate/Culture: High-level organizational priorities that compromise safety
16. ORGANIZATIONAL INFLUENCES—Policy/Procedures/Process: Inadequate, conflicting, or unclear organizational policies and procedures
17. ORGANIZATIONAL INFLUENCES—Resource Support: Insufficient resources (funding, equipment, personnel, time)
18. ORGANIZATIONAL INFLUENCES—Training Program Issues: Systemic problems with training programs and curricula

ANALYSIS REQUIREMENTS:
• Provide detailed reasoning for each classification with specific evidence from the narrative
• Assign confidence scores (0.0-1.0) for each classification based on evidence strength
• Consider the hierarchical nature of HFACS - higher layers often influence lower layers
• Identify primary factors (most direct causes) vs contributing factors (background conditions)
• Provide actionable recommendations targeting each identified layer
• Be conservative - only classify factors with clear textual evidence

QUALITY STANDARDS:
• Maintain objectivity and avoid speculation beyond the evidence
• Ensure classifications are mutually exclusive within layers but can span multiple layers
• Consider both active failures (unsafe acts) and latent conditions (preconditions, supervision, organization)
• Prioritize accuracy over completeness - better to miss a factor than misclassify

Be thorough, objective, and consistent with HFACS 8.0 definitions."""
    
    def analyze_hfacs(self, incident_data: Dict) -> HFACSAnalysisResult:
        """
        进行HFACS分析

        Args:
            incident_data: 事故数据

        Returns:
            HFACSAnalysisResult: HFACS分析结果
        """
        try:
            if self.use_mock:
                return self._mock_hfacs_analysis(incident_data)
            else:
                return self._openai_hfacs_analysis(incident_data)
        except Exception as e:
            logger.error(f"HFACS分析失败: {e}")
            return self._fallback_hfacs_analysis(incident_data)

    def _create_hfacs_function_schema(self):
        """创建HFACS分析的Function Schema"""
        return {
            "name": "analyze_hfacs_factors",
            "description": "Analyze incident narrative using HFACS 8.0 framework",
            "parameters": {
                "type": "object",
                "properties": {
                    "classifications": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "category": {
                                    "type": "string",
                                    "enum": HFACS_CATEGORIES,
                                    "description": "HFACS category classification"
                                },
                                "layer": {
                                    "type": "string",
                                    "enum": HFACS_LAYERS,
                                    "description": "HFACS layer classification"
                                },
                                "confidence": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                    "description": "Confidence score for this classification"
                                },
                                "reasoning": {
                                    "type": "string",
                                    "description": "Detailed reasoning for this classification"
                                },
                                "evidence": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Specific evidence from the narrative"
                                }
                            },
                            "required": ["category", "layer", "confidence", "reasoning", "evidence"]
                        }
                    },
                    "primary_factors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Primary human factors identified"
                    },
                    "contributing_factors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Contributing factors identified"
                    },
                    "recommendations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific recommendations for prevention"
                    },
                    "analysis_summary": {
                        "type": "string",
                        "description": "Overall analysis summary"
                    },
                    "confidence_score": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Overall confidence in the analysis"
                    }
                },
                "required": ["classifications", "primary_factors", "contributing_factors", "recommendations", "analysis_summary", "confidence_score"]
            }
        }
    
    def _openai_hfacs_analysis(self, incident_data: Dict) -> HFACSAnalysisResult:
        """使用OpenAI进行HFACS分析"""

        analysis_prompt = self._build_hfacs_prompt(incident_data)

        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                "functions": [self._create_hfacs_function_schema()],
                "function_call": {"name": "analyze_hfacs_factors"},
                "temperature": 0.1,
                "max_tokens": 3000
            }

            response = requests.post(url, headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                message = result['choices'][0]['message']

                if 'function_call' in message:
                    function_result = json.loads(message['function_call']['arguments'])
                    return self._parse_function_response(function_result, incident_data)
                else:
                    # 如果没有function call，尝试解析普通响应
                    analysis_text = message['content']
                    return self._parse_hfacs_response(analysis_text, incident_data)
            else:
                logger.error(f"OpenAI HFACS分析失败: {response.status_code}")
                return self._fallback_hfacs_analysis(incident_data)

        except Exception as e:
            logger.error(f"OpenAI HFACS分析失败: {e}")
            return self._fallback_hfacs_analysis(incident_data)

    def _parse_function_response(self, result: Dict, incident_data: Dict) -> HFACSAnalysisResult:
        """解析Function Call响应"""

        classifications = []
        for item in result.get("classifications", []):
            classifications.append(HFACSClassification(
                category=item.get("category", ""),
                layer=item.get("layer", ""),
                confidence=item.get("confidence", 0.0),
                reasoning=item.get("reasoning", ""),
                evidence=item.get("evidence", [])
            ))

        # 生成可视化数据
        visualization_data = self._generate_visualization_data(classifications)

        return HFACSAnalysisResult(
            classifications=classifications,
            primary_factors=result.get("primary_factors", []),
            contributing_factors=result.get("contributing_factors", []),
            recommendations=result.get("recommendations", []),
            analysis_summary=result.get("analysis_summary", ""),
            confidence_score=result.get("confidence_score", 0.0),
            analysis_timestamp=datetime.now().isoformat(),
            visualization_data=visualization_data
        )
    
    def _build_hfacs_prompt(self, incident_data: Dict) -> str:
        """构建HFACS分析提示词"""

        prompt = f"""Analyze the following UAV incident using the HFACS 8.0 framework:

**Incident Information:**
- Date: {incident_data.get('date', 'N/A')}
- Flight Phase: {incident_data.get('flight_phase', 'N/A')}
- Mission Type: {incident_data.get('mission_type', 'N/A')}
- Weather: {incident_data.get('weather', 'N/A')}
- Location: {incident_data.get('location', 'N/A')}
- Altitude: {incident_data.get('altitude', 'N/A')} feet

**Incident Narrative:**
{incident_data.get('narrative', 'N/A')}

**Primary Problem:**
{incident_data.get('primary_problem', 'N/A')}

**Contributing Factors:**
{incident_data.get('contributing_factors', 'N/A')}

**Human Factors:**
{incident_data.get('human_factors', 'N/A')}

Please analyze this incident and identify ALL applicable HFACS categories and layers. For each classification:
1. Select the most appropriate category from the 18 HFACS categories
2. Identify the corresponding layer (1 of 4 layers)
3. Provide detailed reasoning with specific evidence from the narrative
4. Assign a confidence score (0.0-1.0)
5. List specific evidence that supports the classification

Also provide:
- Primary human factors (most critical)
- Contributing factors (secondary)
- Specific recommendations for prevention
- Overall analysis summary
- Overall confidence score

Be thorough and objective in your analysis."""

        return prompt

    def _generate_visualization_data(self, classifications: List[HFACSClassification]) -> Dict:
        """生成可视化数据"""

        # 按层级统计
        layer_counts = {}
        layer_confidence = {}

        for classification in classifications:
            layer = classification.layer
            layer_counts[layer] = layer_counts.get(layer, 0) + 1
            if layer not in layer_confidence:
                layer_confidence[layer] = []
            layer_confidence[layer].append(classification.confidence)

        # 计算平均置信度
        layer_avg_confidence = {}
        for layer, confidences in layer_confidence.items():
            layer_avg_confidence[layer] = sum(confidences) / len(confidences)

        # 按类别统计
        category_data = []
        for classification in classifications:
            category_data.append({
                'category': classification.category,
                'layer': classification.layer,
                'confidence': classification.confidence,
                'reasoning': classification.reasoning[:100] + "..." if len(classification.reasoning) > 100 else classification.reasoning
            })

        return {
            'layer_counts': layer_counts,
            'layer_avg_confidence': layer_avg_confidence,
            'category_data': category_data,
            'total_classifications': len(classifications)
        }

    def create_hfacs_visualizations(self, result: HFACSAnalysisResult) -> Dict:
        """创建HFACS可视化图表"""

        visualizations = {}

        if not result.classifications:
            return visualizations

        # 1. 层级分布饼图
        layer_counts = result.visualization_data.get('layer_counts', {})
        if layer_counts:
            fig_pie = px.pie(
                values=list(layer_counts.values()),
                names=list(layer_counts.keys()),
                title="HFACS Layer Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            visualizations['layer_pie'] = fig_pie

        # 2. 层级置信度条形图
        layer_confidence = result.visualization_data.get('layer_avg_confidence', {})
        if layer_confidence:
            fig_bar = px.bar(
                x=list(layer_confidence.keys()),
                y=list(layer_confidence.values()),
                title="Average Confidence by HFACS Layer",
                labels={'x': 'HFACS Layer', 'y': 'Average Confidence'},
                color=list(layer_confidence.values()),
                color_continuous_scale='RdYlGn'
            )
            fig_bar.update_layout(showlegend=False)
            visualizations['confidence_bar'] = fig_bar

        # 3. 详细分类热力图
        category_data = result.visualization_data.get('category_data', [])
        if category_data:
            df = pd.DataFrame(category_data)

            # 创建层级-类别矩阵
            heatmap_data = []
            for layer in HFACS_LAYERS:
                layer_categories = df[df['layer'] == layer]
                for category in HFACS_CATEGORIES:
                    if category.startswith(layer):
                        matching = layer_categories[layer_categories['category'] == category]
                        confidence = matching['confidence'].mean() if not matching.empty else 0
                        heatmap_data.append({
                            'Layer': layer,
                            'Category': category.replace(layer + "—", ""),
                            'Confidence': confidence
                        })

            if heatmap_data:
                heatmap_df = pd.DataFrame(heatmap_data)
                pivot_df = heatmap_df.pivot(index='Layer', columns='Category', values='Confidence')

                fig_heatmap = px.imshow(
                    pivot_df.values,
                    x=pivot_df.columns,
                    y=pivot_df.index,
                    title="HFACS Classification Confidence Heatmap",
                    color_continuous_scale='RdYlGn',
                    aspect='auto'
                )
                fig_heatmap.update_xaxes(tickangle=45)
                visualizations['heatmap'] = fig_heatmap

        # 4. 分类详情表格
        if category_data:
            df = pd.DataFrame(category_data)
            df = df.sort_values('confidence', ascending=False)
            visualizations['details_table'] = df

        # 5. 置信度分布直方图
        confidences = [c.confidence for c in result.classifications]
        if confidences:
            fig_hist = px.histogram(
                x=confidences,
                nbins=10,
                title="Confidence Score Distribution",
                labels={'x': 'Confidence Score', 'y': 'Count'},
                color_discrete_sequence=['#1f77b4']
            )
            visualizations['confidence_hist'] = fig_hist

        return visualizations
    
    def create_hfacs_tree_visualization(self, result: HFACSAnalysisResult) -> go.Figure:
        """创建HFACS四层18类树状图可视化"""
        
        # 定义层级颜色 - 专业级配色方案
        layer_colors = {
            'HFACS Framework': '#1A365D',          # 深海军蓝 - 根节点
            'UNSAFE ACTS': '#C53030',              # 深红色 - 不安全行为
            'PRECONDITIONS': '#D69E2E',            # 金橙色 - 前提条件  
            'SUPERVISION/LEADERSHIP': '#2B6CB0',   # 深蓝色 - 监督领导
            'ORGANIZATIONAL INFLUENCES': '#805AD5' # 深紫色 - 组织影响
        }
        
        # 定义节点位置（手动布局以确保美观）
        positions = {
            # 根节点
            'HFACS Framework': (0, 4),
            
            # 第一层 - UNSAFE ACTS
            'UNSAFE ACTS': (-3, 3),
            'UNSAFE ACTS—Errors—Performance/Skill-Based': (-4.5, 2.5),
            'UNSAFE ACTS—Errors—Judgement & Decision-Making': (-3, 2.5),
            'UNSAFE ACTS—Known Deviations': (-1.5, 2.5),
            
            # 第二层 - PRECONDITIONS  
            'PRECONDITIONS': (-1, 3),
            'PRECONDITIONS—Physical Environment': (-2.5, 2),
            'PRECONDITIONS—Technological Environment': (-1.5, 2),
            'PRECONDITIONS—Team Coordination/Communication': (-0.5, 2),
            'PRECONDITIONS—Training Conditions': (-2.5, 1.5),
            'PRECONDITIONS—Mental Awareness (Attention)': (-1.5, 1.5),
            'PRECONDITIONS—State of Mind': (-0.5, 1.5),
            'PRECONDITIONS—Adverse Physiological': (-2, 1),
            
            # 第三层 - SUPERVISION/LEADERSHIP
            'SUPERVISION/LEADERSHIP': (1, 3),
            'SUPERVISION/LEADERSHIP—Unit Safety Culture': (0.5, 2),
            'SUPERVISION/LEADERSHIP—Supervisory Known Deviations': (1.5, 2),
            'SUPERVISION/LEADERSHIP—Ineffective Supervision': (0.5, 1.5),
            'SUPERVISION/LEADERSHIP—Ineffective Planning & Coordination': (1.5, 1.5),
            
            # 第四层 - ORGANIZATIONAL INFLUENCES
            'ORGANIZATIONAL INFLUENCES': (3, 3),
            'ORGANIZATIONAL INFLUENCES—Climate/Culture': (2.5, 2),
            'ORGANIZATIONAL INFLUENCES—Policy/Procedures/Process': (3.5, 2),
            'ORGANIZATIONAL INFLUENCES—Resource Support': (2.5, 1.5),
            'ORGANIZATIONAL INFLUENCES—Training Program Issues': (3.5, 1.5),
        }
        
        # 创建图形对象
        fig = go.Figure()
        
        # 分析结果中识别的分类
        identified_categories = set()
        if result.classifications:
            identified_categories = {cls.category for cls in result.classifications}
        
        # 添加连接线（边）
        edges = [
            # 根到层级
            ('HFACS Framework', 'UNSAFE ACTS'),
            ('HFACS Framework', 'PRECONDITIONS'),
            ('HFACS Framework', 'SUPERVISION/LEADERSHIP'),
            ('HFACS Framework', 'ORGANIZATIONAL INFLUENCES'),
            
            # 层级到分类
            ('UNSAFE ACTS', 'UNSAFE ACTS—Errors—Performance/Skill-Based'),
            ('UNSAFE ACTS', 'UNSAFE ACTS—Errors—Judgement & Decision-Making'),
            ('UNSAFE ACTS', 'UNSAFE ACTS—Known Deviations'),
            
            ('PRECONDITIONS', 'PRECONDITIONS—Physical Environment'),
            ('PRECONDITIONS', 'PRECONDITIONS—Technological Environment'),
            ('PRECONDITIONS', 'PRECONDITIONS—Team Coordination/Communication'),
            ('PRECONDITIONS', 'PRECONDITIONS—Training Conditions'),
            ('PRECONDITIONS', 'PRECONDITIONS—Mental Awareness (Attention)'),
            ('PRECONDITIONS', 'PRECONDITIONS—State of Mind'),
            ('PRECONDITIONS', 'PRECONDITIONS—Adverse Physiological'),
            
            ('SUPERVISION/LEADERSHIP', 'SUPERVISION/LEADERSHIP—Unit Safety Culture'),
            ('SUPERVISION/LEADERSHIP', 'SUPERVISION/LEADERSHIP—Supervisory Known Deviations'),
            ('SUPERVISION/LEADERSHIP', 'SUPERVISION/LEADERSHIP—Ineffective Supervision'),
            ('SUPERVISION/LEADERSHIP', 'SUPERVISION/LEADERSHIP—Ineffective Planning & Coordination'),
            
            ('ORGANIZATIONAL INFLUENCES', 'ORGANIZATIONAL INFLUENCES—Climate/Culture'),
            ('ORGANIZATIONAL INFLUENCES', 'ORGANIZATIONAL INFLUENCES—Policy/Procedures/Process'),
            ('ORGANIZATIONAL INFLUENCES', 'ORGANIZATIONAL INFLUENCES—Resource Support'),
            ('ORGANIZATIONAL INFLUENCES', 'ORGANIZATIONAL INFLUENCES—Training Program Issues'),
        ]
        
        # 绘制连接线
        for edge in edges:
            start_pos = positions[edge[0]]
            end_pos = positions[edge[1]]
            
            # 确定线条颜色和宽度 - 专业级连接线设计
            line_color = '#A0AEC0'  # 专业的中灰色
            line_width = 3
            opacity = 0.7
            
            # 如果终点节点被识别，高亮连接线
            if edge[1] in identified_categories:
                line_color = '#C53030'  # 深红色高亮
                line_width = 6
                opacity = 1.0
            
            fig.add_trace(go.Scatter(
                x=[start_pos[0], end_pos[0]],
                y=[start_pos[1], end_pos[1]],
                mode='lines',
                line=dict(color=line_color, width=line_width),
                opacity=opacity,
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # 添加节点
        for node, pos in positions.items():
            # 确定节点样式 - 专业级视觉设计
            if node == 'HFACS Framework':
                # 根节点 - 最显眼的钻石形状
                color = layer_colors[node]
                size = 40
                symbol = 'diamond'
                text_color = 'white'
                border_color = '#0F2027'
                border_width = 4
            elif node in ['UNSAFE ACTS', 'PRECONDITIONS', 'SUPERVISION/LEADERSHIP', 'ORGANIZATIONAL INFLUENCES']:
                # 层级节点 - 突出的圆形节点
                color = layer_colors[node]
                size = 32
                symbol = 'circle'
                text_color = 'white'
                border_color = '#FFFFFF'
                border_width = 4
            else:
                # 分类节点
                layer = CATEGORY_TO_LAYER.get(node, 'UNKNOWN')
                base_color = layer_colors.get(layer, '#718096')
                
                # 如果该分类被识别，使用高亮颜色和更大尺寸
                if node in identified_categories:
                    color = base_color
                    size = 26
                    symbol = 'circle'
                    text_color = 'white'
                    border_color = '#FFFFFF'
                    border_width = 3
                else:
                    # 未识别的节点 - 改为更好的对比度
                    color = '#E2E8F0'  # 浅灰背景
                    size = 20
                    symbol = 'circle'  
                    text_color = '#2D3748'  # 深色文字，确保可读性
                    border_color = '#CBD5E0'
                    border_width = 2
            
            # 创建显示文本（缩短长名称）
            display_text = node
            if '—' in node:
                display_text = node.split('—')[-1]
            
            # 添加节点
            fig.add_trace(go.Scatter(
                x=[pos[0]],
                y=[pos[1]],
                mode='markers+text',
                marker=dict(
                    size=size,
                    color=color,
                    symbol=symbol,
                    line=dict(color=border_color, width=border_width)
                ),
                text=display_text,
                textposition='middle center',
                textfont=dict(
                    size=12 if node not in ['HFACS Framework'] + list(HFACS_LAYERS) else 16,
                    color=text_color,
                    family="Arial Black" if node in ['HFACS Framework'] + list(HFACS_LAYERS) else "Arial Bold"
                ),
                hovertemplate=f"<b style='color: {color}'>{node}</b><br>" + 
                             (f"<b>Confidence:</b> {next((cls.confidence for cls in result.classifications if cls.category == node), 0):.1%}<br>" if node in identified_categories else "") +
                             (f"<b>Analysis:</b> {next((cls.reasoning[:100] + '...' if len(cls.reasoning) > 100 else cls.reasoning for cls in result.classifications if cls.category == node), '')}<br>" if node in identified_categories else "") +
                             "<extra></extra>",
                showlegend=False,
                name=display_text
            ))
        
        # 添加图例
        legend_traces = []
        for layer, color in layer_colors.items():
            if layer != 'HFACS Framework':
                legend_traces.append(go.Scatter(
                    x=[None], y=[None],
                    mode='markers',
                    marker=dict(size=15, color=color),
                    name=layer,
                    showlegend=True
                ))
        
        for trace in legend_traces:
            fig.add_trace(trace)
        
        # 设置布局 - 增强美观度和专业性
        fig.update_layout(
            title={
                'text': '<b style="color: #2D3748; font-size: 24px;">HFACS 8.0 Framework - UAV Incident Analysis</b><br>' +
                       '<span style="color: #718096; font-size: 16px;">Four Layers • Eighteen Categories • Tree Visualization</span>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 22, 'color': '#2D3748', 'family': 'Arial Black'}
            },
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.05,
                xanchor="center",
                x=0.5,
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='rgba(113,128,150,0.3)',
                borderwidth=2,
                font=dict(size=12, color='#2D3748')
            ),
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                range=[-5.5, 4.5]
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                range=[0.3, 4.7]
            ),
            plot_bgcolor='rgba(249,250,251,1)',  # 专业的浅色背景
            paper_bgcolor='#FFFFFF',
            width=1400,
            height=950,
            margin=dict(t=130, b=70, l=80, r=80),
            font=dict(family='Arial', size=12, color='#2D3748')
        )
        
        # 添加说明文字 - 增强信息展示
        if identified_categories:
            identified_count = len(identified_categories)
            total_categories = 18
            
            # 计算分析统计信息
            high_confidence = sum(1 for cls in result.classifications if cls.confidence > 0.8)
            medium_confidence = sum(1 for cls in result.classifications if 0.5 <= cls.confidence <= 0.8)
            low_confidence = sum(1 for cls in result.classifications if cls.confidence < 0.5)
            
            fig.add_annotation(
                text=f"<b style='color: #2D3748; font-size: 14px;'>📊 Analysis Summary</b><br>" +
                     f"<b>Identified Factors:</b> {identified_count}/{total_categories} HFACS categories<br>" +
                     f"<b>Confidence Distribution:</b> High ({high_confidence}) | Medium ({medium_confidence}) | Low ({low_confidence})<br>" +
                     "<br><b style='color: #C53030;'>🔴 Highlighted Nodes:</b> Factors identified in this incident<br>" +
                     "<b style='color: #718096;'>⚪ Gray Nodes:</b> Factors not identified",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=11, color='#2D3748', family='Arial'),
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='rgba(113,128,150,0.3)',
                borderwidth=2,
            )
        else:
            fig.add_annotation(
                text="<b style='color: #2D3748; font-size: 14px;'>🔍 HFACS Framework Overview</b><br>" +
                     "This visualization shows the complete HFACS 8.0 framework structure.<br>" +
                     "Perform incident analysis to see identified factors highlighted.",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=11, color='#2D3748', family='Arial'),
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='rgba(113,128,150,0.3)',
                borderwidth=2,
            )
        
        return fig
    
    def _parse_hfacs_response(self, analysis_text: str, incident_data: Dict) -> HFACSAnalysisResult:
        """解析HFACS分析响应"""
        
        categories = []
        primary_factors = []
        recommendations = []
        analysis_summary = ""
        confidence_score = 0.8
        
        lines = analysis_text.split('\n')
        current_level = None
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 识别HFACS层级
            if "Level 1" in line:
                current_level = "Level 1"
            elif "Level 2" in line:
                current_level = "Level 2"
            elif "Level 3" in line:
                current_level = "Level 3"
            elif "Level 4" in line:
                current_level = "Level 4"
            elif "主要人因因素排序" in line:
                current_section = "primary_factors"
            elif "改进建议" in line:
                current_section = "recommendations"
            elif "分析总结" in line:
                current_section = "summary"
            elif "置信度" in line:
                try:
                    confidence_score = float(line.split("：")[1].strip())
                except:
                    confidence_score = 0.8
            elif line.startswith(('1.', '2.', '3.', '4.', '5.')):
                item = line[2:].strip()
                if current_section == "primary_factors":
                    primary_factors.append(item)
                elif current_section == "recommendations":
                    recommendations.append(item)
            elif current_section == "summary" and line:
                analysis_summary += line + " "
            
            # 解析具体的HFACS分类
            if current_level and any(keyword in line for keyword in ["错误类型", "违规类型", "环境因素", "操作者状态", "监督问题", "组织因素"]):
                # 提取分类信息
                if ":" in line:
                    category_type, description = line.split(":", 1)
                    categories.append(HFACSCategory(
                        level=current_level,
                        category=category_type.strip(),
                        subcategory="",
                        description=description.strip(),
                        evidence=[],
                        confidence=0.8
                    ))
        
        return HFACSAnalysisResult(
            categories=categories,
            primary_factors=primary_factors,
            contributing_factors=[],
            recommendations=recommendations,
            analysis_summary=analysis_summary.strip(),
            confidence_score=confidence_score,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _mock_hfacs_analysis(self, incident_data: Dict) -> HFACSAnalysisResult:
        """模拟HFACS分析"""

        narrative = incident_data.get('narrative', '').lower()
        human_factors = incident_data.get('human_factors', '').lower()

        # 基于关键词的简单分类
        classifications = []

        # UNSAFE ACTS
        if any(word in narrative for word in ['error', 'mistake', 'wrong', 'decision']):
            classifications.append(HFACSClassification(
                category="UNSAFE ACTS—Errors—Judgement & Decision-Making",
                layer="UNSAFE ACTS",
                confidence=0.7,
                reasoning="Evidence of decision-making errors in the narrative",
                evidence=["Decision-related keywords found in narrative"]
            ))

        # PRECONDITIONS
        if any(word in narrative for word in ['communication', 'coordination', 'team']):
            classifications.append(HFACSClassification(
                category="PRECONDITIONS—Team Coordination/Communication",
                layer="PRECONDITIONS",
                confidence=0.6,
                reasoning="Communication or coordination issues identified",
                evidence=["Communication-related factors mentioned"]
            ))

        # SUPERVISION/LEADERSHIP
        if any(word in narrative for word in ['training', 'supervision', 'procedure']):
            classifications.append(HFACSClassification(
                category="SUPERVISION/LEADERSHIP—Ineffective Supervision",
                layer="SUPERVISION/LEADERSHIP",
                confidence=0.6,
                reasoning="Training or supervision deficiencies indicated",
                evidence=["Training or supervision issues mentioned"]
            ))

        # ORGANIZATIONAL INFLUENCES
        if any(word in narrative for word in ['policy', 'resource', 'management', 'procedure']):
            classifications.append(HFACSClassification(
                category="ORGANIZATIONAL INFLUENCES—Policy/Procedures/Process",
                layer="ORGANIZATIONAL INFLUENCES",
                confidence=0.5,
                reasoning="Organizational policy or process issues suggested",
                evidence=["Policy or procedural factors identified"]
            ))

        # 生成可视化数据
        visualization_data = self._generate_visualization_data(classifications)

        return HFACSAnalysisResult(
            classifications=classifications,
            primary_factors=[
                "Decision-making errors",
                "Communication breakdown",
                "Inadequate supervision"
            ],
            contributing_factors=[
                "Environmental pressure",
                "Time pressure",
                "Resource limitations"
            ],
            recommendations=[
                "Enhance decision-making training and procedures",
                "Improve supervision mechanisms and quality control",
                "Develop comprehensive organizational safety management system",
                "Establish better communication and coordination protocols"
            ],
            analysis_summary="Based on HFACS 8.0 framework analysis, this incident involves multiple layers of human factors requiring comprehensive improvement measures at individual, supervisory, and organizational levels.",
            confidence_score=0.6,
            analysis_timestamp=datetime.now().isoformat(),
            visualization_data=visualization_data
        )
    
    def _fallback_hfacs_analysis(self, incident_data: Dict) -> HFACSAnalysisResult:
        """备用HFACS分析"""
        return HFACSAnalysisResult(
            classifications=[],
            primary_factors=["Further analysis required"],
            contributing_factors=["System analysis temporarily unavailable"],
            recommendations=["Recommend expert manual HFACS analysis"],
            analysis_summary="System temporarily unable to perform detailed HFACS analysis. Professional manual analysis recommended.",
            confidence_score=0.3,
            analysis_timestamp=datetime.now().isoformat(),
            visualization_data={}
        )
    
    def generate_hfacs_report(self, result: HFACSAnalysisResult) -> str:
        """生成HFACS分析报告"""

        report = f"""
# HFACS 8.0 人因分析报告

**分析时间:** {result.analysis_timestamp}
**置信度:** {result.confidence_score:.2f}

## 分析总结
{result.analysis_summary}

## HFACS分类结果

"""

        # 按层级组织分类结果
        if result.classifications:
            levels = {}
            for classification in result.classifications:
                if classification.layer not in levels:
                    levels[classification.layer] = []
                levels[classification.layer].append(classification)

            for level, classifications in levels.items():
                report += f"### {level}\n\n"
                for classification in classifications:
                    report += f"**{classification.category}**\n"
                    report += f"- 分析: {classification.reasoning}\n"
                    report += f"- 置信度: {classification.confidence:.2f}\n"
                    if classification.evidence:
                        report += f"- 证据: {', '.join(classification.evidence)}\n"
                    report += "\n"

        # 主要因素
        if result.primary_factors:
            report += "## 主要人因因素\n\n"
            for i, factor in enumerate(result.primary_factors, 1):
                report += f"{i}. {factor}\n"
            report += "\n"

        # 贡献因素
        if result.contributing_factors:
            report += "## 贡献因素\n\n"
            for i, factor in enumerate(result.contributing_factors, 1):
                report += f"{i}. {factor}\n"
            report += "\n"

        # 改进建议
        if result.recommendations:
            report += "## 改进建议\n\n"
            for i, rec in enumerate(result.recommendations, 1):
                report += f"{i}. {rec}\n"
            report += "\n"

        return report
    
    def get_hfacs_statistics(self, results: List[HFACSAnalysisResult]) -> Dict:
        """获取HFACS统计信息"""
        
        if not results:
            return {}
        
        stats = {
            'total_analyses': len(results),
            'level_distribution': {},
            'category_distribution': {},
            'average_confidence': 0.0
        }
        
        # 统计各层级分布
        level_counts = {}
        category_counts = {}
        total_confidence = 0.0
        
        for result in results:
            total_confidence += result.confidence_score
            
            for category in result.categories:
                level_counts[category.level] = level_counts.get(category.level, 0) + 1
                category_counts[category.category] = category_counts.get(category.category, 0) + 1
        
        stats['level_distribution'] = level_counts
        stats['category_distribution'] = category_counts
        stats['average_confidence'] = total_confidence / len(results) if results else 0.0
        
        return stats

def main():
    """测试函数"""
    # 测试数据
    test_incident = {
        'date': '2024-01-15',
        'flight_phase': 'Cruise',
        'mission_type': 'Training',
        'weather': 'VMC',
        'narrative': 'The pilot made a decision error during the flight which led to a communication breakdown. There was inadequate supervision and the training procedures were not followed properly.',
        'human_factors': 'Decision making, Communication, Training',
        'primary_problem': 'Human Error',
        'contributing_factors': 'Inadequate training, poor communication protocols'
    }
    
    # 创建分析器并测试
    analyzer = HFACSAnalyzer()
    result = analyzer.analyze_hfacs(test_incident)
    
    print("HFACS分析结果:")
    print(f"主要因素: {result.primary_factors}")
    print(f"建议措施: {result.recommendations}")
    print(f"置信度: {result.confidence_score}")
    
    # 生成报告
    report = analyzer.generate_hfacs_report(result)
    print("\n" + "="*50)
    print(report)

if __name__ == "__main__":
    main()
