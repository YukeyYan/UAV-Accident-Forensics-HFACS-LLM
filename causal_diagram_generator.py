"""
Causal Diagram Automatic Generator
Automatically generate causal relationship diagrams based on incident narratives for accident investigation and root cause analysis
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import os
import re
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import numpy as np
from translations import get_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CausalNode:
    """Causal Relationship Node"""
    id: str
    name: str
    type: str  # 'root_cause', 'contributing_factor', 'immediate_cause', 'consequence'
    description: str
    likelihood: float  # 0.0-1.0
    impact: float  # 0.0-1.0
    evidence_strength: float  # 0.0-1.0
    category: str  # 'human', 'technical', 'environmental', 'organizational'

@dataclass
class CausalRelationship:
    """Causal Relationship Connection"""
    from_node: str
    to_node: str
    relationship_type: str  # 'direct_cause', 'contributing_cause', 'enabling_condition'
    strength: float  # 0.0-1.0
    confidence: float  # 0.0-1.0
    description: str

@dataclass
class CausalDiagram:
    """Causal Relationship Diagram"""
    nodes: List[CausalNode]
    relationships: List[CausalRelationship]
    central_event: str
    timeline: List[Dict[str, Any]]
    risk_paths: List[List[str]]  # Risk propagation paths
    control_points: List[Dict[str, Any]]  # Control points
    metadata: Dict[str, Any]

class CausalDiagramGenerator:
    """Causal Diagram Generator"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize Causal Diagram Generator
        
        Args:
            api_key: OpenAI API key
            model: Model to use (gpt-4o or gpt-4o-mini)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY') or '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'
        self.model = model
        self.use_mock = not bool(self.api_key)
        
        # Define node category colors
        self.node_colors = {
            'root_cause': '#e74c3c',        # Red - Root cause
            'contributing_factor': '#f39c12', # Orange - Contributing factor  
            'immediate_cause': '#e67e22',    # Dark orange - Immediate cause
            'consequence': '#9b59b6',        # Purple - Consequence
            'control_point': '#27ae60'       # Green - Control point
        }
        
        # 定义类别颜色
        self.category_colors = {
            'human': '#3498db',          # 蓝色 - 人为因素
            'technical': '#e74c3c',      # 红色 - 技术因素
            'environmental': '#27ae60',  # 绿色 - 环境因素
            'organizational': '#f39c12', # 橙色 - 组织因素
            'procedural': '#9b59b6'      # 紫色 - 程序因素
        }
        
        self.system_prompt = """You are a world-class incident investigation expert and causal analysis specialist with expertise in:

🎯 CORE COMPETENCIES:
• Root Cause Analysis (RCA) methodologies
• Causal mapping and systems thinking
• Aviation accident investigation (NTSB, ICAO standards)
• Human factors analysis (HFACS, SHELL model)
• Swiss Cheese model and barrier analysis
• Bow-tie risk analysis
• Failure Mode and Effects Analysis (FMEA)
• Event and fault tree analysis

📊 CAUSAL ANALYSIS FRAMEWORK:
Your mission is to analyze incident narratives and construct comprehensive causal diagrams that reveal the complex web of factors leading to the event.

🔍 NODE CLASSIFICATION:
1. **Root Causes** - Fundamental system deficiencies that, if corrected, would prevent recurrence
2. **Contributing Factors** - Conditions that increased likelihood but didn't directly cause the event
3. **Immediate Causes** - Direct precipitating factors that triggered the event
4. **Consequences** - Direct and indirect outcomes of the event

📋 FACTOR CATEGORIES:
• **Human Factors**: Decision errors, skill deficiencies, violations, communication failures
• **Technical Factors**: Equipment failures, design deficiencies, maintenance issues
• **Environmental Factors**: Weather, lighting, terrain, external hazards  
• **Organizational Factors**: Policies, procedures, culture, resource allocation
• **Procedural Factors**: Inadequate procedures, procedure violations, gaps

⚖️ ASSESSMENT DIMENSIONS:
• **Likelihood** (0.0-1.0): Probability this factor contributed to the event
• **Impact** (0.0-1.0): Magnitude of influence on event occurrence/severity
• **Evidence Strength** (0.0-1.0): Quality and reliability of supporting evidence
• **Relationship Strength** (0.0-1.0): Certainty of causal connection

🎯 ANALYSIS PRINCIPLES:
• Apply systems thinking to identify complex interactions
• Consider multiple causal pathways and feedback loops
• Distinguish between necessary and sufficient causes
• Identify both active failures and latent conditions
• Focus on systemic factors rather than individual blame
• Consider prevention and mitigation opportunities

🔗 RELATIONSHIP TYPES:
• **Direct Cause**: Factor X directly produced outcome Y
• **Contributing Cause**: Factor X increased likelihood of outcome Y
• **Enabling Condition**: Factor X made outcome Y possible

Your analysis should provide actionable insights for prevention and risk mitigation while maintaining scientific rigor and objectivity."""
    
    def generate_causal_diagram(self, narrative: str, incident_data: Dict = None) -> CausalDiagram:
        """
        基于叙述生成因果图
        
        Args:
            narrative: 事故叙述
            incident_data: 额外的事故数据
            
        Returns:
            CausalDiagram: 生成的因果图
        """
        try:
            if self.use_mock:
                return self._generate_mock_diagram(narrative, incident_data)
            else:
                return self._generate_ai_diagram(narrative, incident_data)
        except Exception as e:
            logger.error(f"因果图生成失败: {e}")
            return self._generate_fallback_diagram(narrative, incident_data)
    
    def _generate_ai_diagram(self, narrative: str, incident_data: Dict = None) -> CausalDiagram:
        """使用AI生成因果图"""
        
        # 构建分析提示
        prompt = self._build_causal_analysis_prompt(narrative, incident_data)
        
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "functions": [self._create_causal_function_schema()],
                "function_call": {"name": "analyze_causal_relationships"},
                "temperature": 0.1,
                "max_tokens": 3000
            }

            response = requests.post(url, headers=headers, json=data, timeout=60)

            if response.status_code == 200:
                result = response.json()
                message = result['choices'][0]['message']

                if 'function_call' in message:
                    function_result = json.loads(message['function_call']['arguments'])
                    return self._parse_causal_result(function_result, narrative)
                else:
                    return self._generate_fallback_diagram(narrative, incident_data)
            else:
                logger.error(f"AI分析失败: {response.status_code}")
                return self._generate_fallback_diagram(narrative, incident_data)

        except Exception as e:
            logger.error(f"AI因果分析失败: {e}")
            return self._generate_fallback_diagram(narrative, incident_data)
    
    def _build_causal_analysis_prompt(self, narrative: str, incident_data: Dict = None) -> str:
        """构建因果分析提示"""
        
        additional_info = ""
        if incident_data:
            additional_info = f"\n**Additional Context:**\n"
            for key, value in incident_data.items():
                if value:
                    additional_info += f"- {key}: {value}\n"
        
        prompt = f"""Conduct a comprehensive causal analysis of the following UAV/UAS incident narrative:

**INCIDENT NARRATIVE:**
{narrative}
{additional_info}

**ANALYSIS REQUIREMENTS:**

🎯 **PRIMARY OBJECTIVES:**
1. Identify all causal factors contributing to the incident
2. Establish causal relationships and dependencies
3. Classify factors by type and category
4. Assess likelihood, impact, and evidence strength
5. Map risk propagation pathways
6. Identify control points for prevention

📊 **REQUIRED ANALYSIS:**

**1. ROOT CAUSE IDENTIFICATION**
- What fundamental system deficiencies enabled this incident?
- What organizational or design factors created the conditions for failure?
- Which factors, if addressed, would prevent similar occurrences?

**2. CONTRIBUTING FACTOR ANALYSIS**
- What conditions increased the likelihood of the incident?
- How did multiple factors interact to create the incident scenario?
- What latent conditions existed in the system?

**3. IMMEDIATE CAUSE MAPPING**
- What direct triggers precipitated the event?
- What was the sequence of immediate failures or errors?
- How did the incident unfold chronologically?

**4. CONSEQUENCE ASSESSMENT**
- What were the direct outcomes of the incident?
- What secondary effects or cascading failures occurred?
- How did consequences propagate through the system?

**5. CONTROL POINT IDENTIFICATION**
- Where could the incident progression have been interrupted?
- What barriers failed or were absent?
- What intervention points exist for prevention?

🔍 **FACTOR CATEGORIZATION:**
Classify each factor into:
- **Human**: Pilot error, training deficiency, decision-making, communication
- **Technical**: Equipment failure, design flaw, maintenance, software
- **Environmental**: Weather, terrain, obstacles, external conditions  
- **Organizational**: Policy, procedure, culture, resources, oversight
- **Procedural**: Process gaps, non-compliance, inadequate procedures

⚖️ **QUANTITATIVE ASSESSMENT:**
For each factor, provide:
- **Likelihood** (0.0-1.0): How probable was this factor's contribution?
- **Impact** (0.0-1.0): How significantly did this factor influence the outcome?
- **Evidence Strength** (0.0-1.0): How well-supported is this factor by evidence?

🔗 **RELATIONSHIP MAPPING:**
Define causal relationships:
- **Direct Cause**: X directly caused Y
- **Contributing Cause**: X increased likelihood of Y  
- **Enabling Condition**: X made Y possible

**TIMELINE INTEGRATION:**
Establish temporal sequence showing how factors developed and interacted over time.

**PREVENTION FOCUS:**
Identify specific, actionable intervention points that could break the causal chain and prevent recurrence."""
        
        return prompt
    
    def _create_causal_function_schema(self):
        """创建因果分析的Function Schema"""
        return {
            "name": "analyze_causal_relationships",
            "description": "Analyze incident narrative and generate comprehensive causal diagram data",
            "parameters": {
                "type": "object",
                "properties": {
                    "central_event": {
                        "type": "string",
                        "description": "Primary incident or failure event"
                    },
                    "causal_nodes": {
                        "type": "array",
                        "description": "All causal factors identified in the analysis",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique identifier"},
                                "name": {"type": "string", "description": "Factor name"},
                                "type": {
                                    "type": "string", 
                                    "enum": ["root_cause", "contributing_factor", "immediate_cause", "consequence"],
                                    "description": "Factor classification"
                                },
                                "description": {"type": "string", "description": "Detailed description"},
                                "likelihood": {
                                    "type": "number", 
                                    "minimum": 0.0, 
                                    "maximum": 1.0,
                                    "description": "Probability of contribution (0.0-1.0)"
                                },
                                "impact": {
                                    "type": "number", 
                                    "minimum": 0.0, 
                                    "maximum": 1.0,
                                    "description": "Magnitude of influence (0.0-1.0)"
                                },
                                "evidence_strength": {
                                    "type": "number", 
                                    "minimum": 0.0, 
                                    "maximum": 1.0,
                                    "description": "Quality of supporting evidence (0.0-1.0)"
                                },
                                "category": {
                                    "type": "string",
                                    "enum": ["human", "technical", "environmental", "organizational", "procedural"],
                                    "description": "Factor category"
                                }
                            },
                            "required": ["id", "name", "type", "description", "likelihood", "impact", "evidence_strength", "category"]
                        }
                    },
                    "causal_relationships": {
                        "type": "array",
                        "description": "Relationships between causal factors",
                        "items": {
                            "type": "object",
                            "properties": {
                                "from_node": {"type": "string", "description": "Source factor ID"},
                                "to_node": {"type": "string", "description": "Target factor ID"},
                                "relationship_type": {
                                    "type": "string",
                                    "enum": ["direct_cause", "contributing_cause", "enabling_condition"],
                                    "description": "Type of causal relationship"
                                },
                                "strength": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                    "description": "Strength of causal connection"
                                },
                                "confidence": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                    "description": "Confidence in relationship"
                                },
                                "description": {"type": "string", "description": "Relationship description"}
                            },
                            "required": ["from_node", "to_node", "relationship_type", "strength", "confidence", "description"]
                        }
                    },
                    "timeline": {
                        "type": "array",
                        "description": "Chronological sequence of events",
                        "items": {
                            "type": "object",
                            "properties": {
                                "time": {"type": "string", "description": "Time reference"},
                                "event": {"type": "string", "description": "Event description"},
                                "factors": {"type": "array", "items": {"type": "string"}, "description": "Associated factor IDs"},
                                "criticality": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
                            }
                        }
                    },
                    "risk_paths": {
                        "type": "array",
                        "description": "Risk propagation pathways",
                        "items": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Sequence of factor IDs showing risk propagation"
                        }
                    },
                    "control_points": {
                        "type": "array",
                        "description": "Potential intervention points",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Control point name"},
                                "description": {"type": "string", "description": "Intervention description"},
                                "effectiveness": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                "associated_factors": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    }
                },
                "required": ["central_event", "causal_nodes", "causal_relationships", "timeline", "risk_paths", "control_points"]
            }
        }
    
    def _parse_causal_result(self, result: Dict, narrative: str) -> CausalDiagram:
        """解析AI分析结果"""
        
        # 解析节点
        nodes = []
        for node_data in result.get("causal_nodes", []):
            node = CausalNode(
                id=node_data["id"],
                name=node_data["name"],
                type=node_data["type"],
                description=node_data["description"],
                likelihood=node_data["likelihood"],
                impact=node_data["impact"],
                evidence_strength=node_data["evidence_strength"],
                category=node_data["category"]
            )
            nodes.append(node)
        
        # 解析关系
        relationships = []
        for rel_data in result.get("causal_relationships", []):
            relationship = CausalRelationship(
                from_node=rel_data["from_node"],
                to_node=rel_data["to_node"],
                relationship_type=rel_data["relationship_type"],
                strength=rel_data["strength"],
                confidence=rel_data["confidence"],
                description=rel_data["description"]
            )
            relationships.append(relationship)
        
        return CausalDiagram(
            nodes=nodes,
            relationships=relationships,
            central_event=result.get("central_event", "Incident Event"),
            timeline=result.get("timeline", []),
            risk_paths=result.get("risk_paths", []),
            control_points=result.get("control_points", []),
            metadata={
                "generation_time": datetime.now().isoformat(),
                "narrative_length": len(narrative),
                "analysis_method": "AI-based",
                "confidence": "high"
            }
        )
    
    def _generate_mock_diagram(self, narrative: str, incident_data: Dict = None) -> CausalDiagram:
        """生成模拟因果图"""
        
        narrative_lower = narrative.lower()
        
        # 基于叙述内容生成节点
        nodes = []
        relationships = []
        
        # Root causes
        if 'communication' in narrative_lower or 'link' in narrative_lower:
            nodes.append(CausalNode(
                id="rc_comm_system",
                name="Communication System Design Deficiency",
                type="root_cause",
                description="Communication system lacks sufficient redundancy and fault recovery mechanisms",
                likelihood=0.8,
                impact=0.9,
                evidence_strength=0.7,
                category="technical"
            ))
            
            nodes.append(CausalNode(
                id="ic_comm_loss",
                name="Communication Link Interruption", 
                type="immediate_cause",
                description="Communication connection between UAV and ground station suddenly interrupted",
                likelihood=0.9,
                impact=0.8,
                evidence_strength=0.9,
                category="technical"
            ))
            
            relationships.append(CausalRelationship(
                from_node="rc_comm_system",
                to_node="ic_comm_loss",
                relationship_type="direct_cause",
                strength=0.8,
                confidence=0.7,
                description="Design deficiency leads to communication interruption"
            ))
        
        # Human factors
        if 'pilot' in narrative_lower or 'operator' in narrative_lower:
            nodes.append(CausalNode(
                id="cf_pilot_training",
                name="Insufficient Pilot Emergency Training",
                type="contributing_factor", 
                description="Lack of sufficient emergency procedure training for communication failures",
                likelihood=0.6,
                impact=0.7,
                evidence_strength=0.5,
                category="human"
            ))
        
        # 环境因素
        if 'weather' in narrative_lower or 'wind' in narrative_lower:
            nodes.append(CausalNode(
                id="cf_weather",
                name="Adverse Weather Conditions",
                type="contributing_factor",
                description="Adverse weather conditions affected flight operations and communication quality",
                likelihood=0.5,
                impact=0.6,
                evidence_strength=0.8,
                category="environmental"
            ))
        
        # 后果
        nodes.append(CausalNode(
            id="cons_control_loss",
            name="Loss of Aircraft Control",
            type="consequence",
            description="Operator unable to continue controlling UAV flight path and operations",
            likelihood=0.9,
            impact=1.0,
            evidence_strength=0.9,
            category="technical"
        ))
        
        # 如果节点太少，添加默认节点
        if len(nodes) < 3:
            nodes.extend([
                CausalNode(
                    id="rc_system_design",
                    name="Inadequate System Design",
                    type="root_cause",
                    description="UAV system did not adequately consider failure modes during design phase",
                    likelihood=0.7,
                    impact=0.8,
                    evidence_strength=0.6,
                    category="organizational"
                ),
                CausalNode(
                    id="cf_maintenance",
                    name="Maintenance Procedure Deficiency",
                    type="contributing_factor",
                    description="Equipment maintenance inspection procedures are inadequate",
                    likelihood=0.5,
                    impact=0.6,
                    evidence_strength=0.4,
                    category="procedural"
                )
            ])
        
        # 生成基本关系
        if len(relationships) == 0:
            for i in range(len(nodes) - 1):
                relationships.append(CausalRelationship(
                    from_node=nodes[i].id,
                    to_node=nodes[i + 1].id,
                    relationship_type="contributing_cause" if i % 2 == 0 else "direct_cause",
                    strength=0.7 - i * 0.1,
                    confidence=0.6 - i * 0.05,
                    description=f"{nodes[i].name} leads to {nodes[i + 1].name}"
                ))
        
        # 时间线
        timeline = [
            {"time": "T-30 min", "event": "Normal flight preparation", "factors": [], "criticality": "low"},
            {"time": "T-10 min", "event": "Flight mission commenced", "factors": [], "criticality": "low"}, 
            {"time": "T-2 min", "event": "Abnormal signs appeared", "factors": [nodes[0].id if nodes else ""], "criticality": "medium"},
            {"time": "T=0", "event": "Incident occurred", "factors": [node.id for node in nodes[-2:] if nodes], "criticality": "critical"},
            {"time": "T+5 min", "event": "Emergency response initiated", "factors": [], "criticality": "high"}
        ]
        
        # 风险路径
        risk_paths = []
        if len(nodes) >= 3:
            risk_paths.append([nodes[0].id, nodes[1].id, nodes[-1].id])
        
        # 控制点
        control_points = [
            {
                "name": "预防性维护检查",
                "description": "加强设备预防性维护和故障预测",
                "effectiveness": 0.8,
                "associated_factors": [nodes[0].id if nodes else ""]
            },
            {
                "name": "应急程序培训",
                "description": "强化操作员应急情况处置培训",
                "effectiveness": 0.7,
                "associated_factors": [node.id for node in nodes if node.category == "human"]
            }
        ]
        
        return CausalDiagram(
            nodes=nodes,
            relationships=relationships,
            central_event="UAV通信故障事故",
            timeline=timeline,
            risk_paths=risk_paths,
            control_points=control_points,
            metadata={
                "generation_time": datetime.now().isoformat(),
                "narrative_length": len(narrative),
                "analysis_method": "Rule-based mock",
                "confidence": "medium"
            }
        )
    
    def _generate_fallback_diagram(self, narrative: str, incident_data: Dict = None) -> CausalDiagram:
        """生成备用因果图"""
        
        # 简单的备用图
        nodes = [
            CausalNode(
                id="unknown_root",
                name="Undetermined Root Cause",
                type="root_cause", 
                description="Further investigation required to determine root cause",
                likelihood=0.5,
                impact=0.5,
                evidence_strength=0.3,
                category="technical"
            ),
            CausalNode(
                id="incident_event",
                name="Incident Event",
                type="immediate_cause",
                description="Incident event based on narrative description",
                likelihood=1.0,
                impact=1.0,
                evidence_strength=1.0,
                category="technical"
            )
        ]
        
        relationships = [
            CausalRelationship(
                from_node="unknown_root",
                to_node="incident_event",
                relationship_type="direct_cause",
                strength=0.5,
                confidence=0.3,
                description="Causal relationship requiring further analysis"
            )
        ]
        
        return CausalDiagram(
            nodes=nodes,
            relationships=relationships,
            central_event="需要进一步分析的事故",
            timeline=[],
            risk_paths=[],
            control_points=[],
            metadata={
                "generation_time": datetime.now().isoformat(),
                "narrative_length": len(narrative),
                "analysis_method": "Fallback",
                "confidence": "low"
            }
        )
    
    def create_causal_visualization(self, diagram: CausalDiagram, lang: str = 'zh') -> go.Figure:
        """创建因果图可视化"""
        
        if not diagram.nodes:
            # 空图的情况
            fig = go.Figure()
            fig.add_annotation(
                x=0.5, y=0.5,
                text="🔧 因果图生成中...<br><br>需要更详细的事故叙述来构建因果关系",
                showarrow=False,
                font=dict(size=14, color='#7f8c8d'),
                xref="paper", yref="paper",
                align="center"
            )
            fig.update_layout(
                title="🔗 事故因果关系图",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                height=400
            )
            return fig
        
        # 使用NetworkX构建图
        G = nx.DiGraph()
        
        # 添加节点
        for node in diagram.nodes:
            G.add_node(node.id, 
                      name=node.name, 
                      type=node.type, 
                      category=node.category,
                      impact=node.impact,
                      likelihood=node.likelihood)
        
        # 添加边
        for rel in diagram.relationships:
            G.add_edge(rel.from_node, rel.to_node, 
                      type=rel.relationship_type, 
                      strength=rel.strength)
        
        # 使用专业的层次化布局，符合事故调查分析逻辑
        pos = self._create_hierarchical_layout(diagram, G)
        
        # 创建可视化
        fig = go.Figure()
        
        # 绘制边
        for rel in diagram.relationships:
            if rel.from_node in pos and rel.to_node in pos:
                x0, y0 = pos[rel.from_node]
                x1, y1 = pos[rel.to_node]
                
                # 边的颜色基于类型
                line_color = {
                    'direct_cause': '#e74c3c',
                    'contributing_cause': '#f39c12', 
                    'enabling_condition': '#3498db'
                }.get(rel.relationship_type, '#95a5a6')
                
                # 边的宽度基于强度
                line_width = 1 + rel.strength * 3
                
                fig.add_trace(go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(color=line_color, width=line_width),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                # 添加箭头，并在中点添加关系类型标签
                mid_x, mid_y = (x0 + x1) / 2, (y0 + y1) / 2
                
                fig.add_annotation(
                    x=x1, y=y1,
                    ax=x0, ay=y0,
                    xref='x', yref='y',
                    axref='x', ayref='y',
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1.5,
                    arrowwidth=2,
                    arrowcolor=line_color
                )
                
                # 添加关系类型标签
                rel_type_label = get_text(rel.relationship_type, lang) if rel.relationship_type in ['direct_cause', 'contributing_cause', 'enabling_condition'] else rel.relationship_type
                
                fig.add_annotation(
                    x=mid_x, y=mid_y,
                    text=f"<b>{rel_type_label}</b><br>({rel.strength:.1f})",
                    showarrow=False,
                    font=dict(size=12, color=line_color, family="Arial Black"),
                    bgcolor="white",
                    bordercolor=line_color,
                    borderwidth=1,
                    xref='x', yref='y'
                )
        
        # Draw nodes
        for node in diagram.nodes:
            if node.id in pos:
                x, y = pos[node.id]
                
                # 节点颜色基于类型
                node_color = self.node_colors.get(node.type, '#95a5a6')
                
                # 节点大小基于影响度
                node_size = 20 + node.impact * 40
                
                # 节点形状基于类别
                symbol = {
                    'human': 'circle',
                    'technical': 'square', 
                    'environmental': 'triangle-up',
                    'organizational': 'diamond',
                    'procedural': 'hexagon'
                }.get(node.category, 'circle')
                
                fig.add_trace(go.Scatter(
                    x=[x], y=[y],
                    mode='markers+text',
                    marker=dict(
                        size=node_size,
                        color=node_color,
                        symbol=symbol,
                        line=dict(width=2, color='white'),
                        opacity=0.8
                    ),
                    text=node.name,
                    textposition="bottom center",
                    textfont=dict(size=14, color='#2c3e50', family="Arial Black"),
                    name=node.type,
                    showlegend=False,
                    hovertemplate=(
                        f"<b>{node.name}</b><br>"
                        f"{get_text('type', lang)}: {get_text(node.type, lang)}<br>"
                        f"{get_text('category', lang)}: {get_text(node.category, lang)}<br>"
                        f"{get_text('likelihood', lang)}: {node.likelihood:.1%}<br>"
                        f"{get_text('impact', lang)}: {node.impact:.1%}<br>"
                        f"{get_text('evidence_strength', lang)}: {node.evidence_strength:.1%}<br>"
                        f"{node.description}"
                        "<extra></extra>"
                    )
                ))
        
        # 添加图例
        legend_traces = []
        for node_type, color in self.node_colors.items():
            legend_traces.append(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(size=12, color=color),
                name=node_type.replace('_', ' ').title(),
                showlegend=True
            ))
        
        for trace in legend_traces:
            fig.add_trace(trace)
        
        # 添加层级标签
        layer_labels = [
            (get_text("organizational_influences", lang), 4),
            (get_text("root_cause", lang), 3), 
            (get_text("contributing_factors", lang), 2),
            (get_text("direct_causes", lang), 1),
            (get_text("incident_consequences", lang), 0)
        ]
        
        for label, y_pos in layer_labels:
            fig.add_annotation(
                x=-5, y=y_pos,
                text=f"<b>{label}</b>",
                showarrow=False,
                font=dict(size=16, color='#2c3e50', family="Arial Black"),
                xref='x', yref='y',
                xanchor='right'
            )
        
        fig.update_layout(
            title={
                'text': f"🔗 Professional Incident Causal Analysis Diagram<br><sub>{diagram.central_event}</sub>",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#2c3e50'}
            },
            xaxis=dict(
                showgrid=False, 
                zeroline=False, 
                showticklabels=False,
                range=[-6, 6]  # 为层级标签留出空间
            ),
            yaxis=dict(
                showgrid=False, 
                zeroline=False, 
                showticklabels=False,
                range=[-0.5, 4.5]
            ),
            height=700,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left", 
                x=1.01,
                title="Node Type"
            ),
            plot_bgcolor='white',
            paper_bgcolor='#f8f9fa'
        )
        
        return fig
    
    def _create_hierarchical_layout(self, diagram: CausalDiagram, G) -> dict:
        """Create hierarchical layout that follows incident investigation logic"""
        
        # 按类型分层，从上到下：组织因素 -> 根本原因 -> 贡献因素 -> 直接原因 -> 后果
        layer_hierarchy = {
            'organizational': 0,     # 最顶层：组织因素
            'root_cause': 1,        # 根本原因层
            'contributing_factor': 2, # 贡献因素层  
            'immediate_cause': 3,    # 直接原因层
            'consequence': 4         # 后果层（最底层）
        }
        
        # 按类别分层，从左到右：人为 -> 技术 -> 环境 -> 程序 -> 组织
        category_order = {
            'human': 0,
            'technical': 1, 
            'environmental': 2,
            'procedural': 3,
            'organizational': 4
        }
        
        pos = {}
        layer_counts = {i: 0 for i in range(5)}  # 每层的节点计数
        
        # 首次遍历：计算每层节点数
        for node in diagram.nodes:
            layer = layer_hierarchy.get(node.type, 2)  # 默认为贡献因素层
            layer_counts[layer] += 1
        
        layer_positions = {i: 0 for i in range(5)}  # 每层当前位置计数
        
        # 第二次遍历：计算实际位置
        for node in diagram.nodes:
            layer = layer_hierarchy.get(node.type, 2)
            category_x_offset = category_order.get(node.category, 2) * 0.5
            
            # Y坐标：根据层次确定（顶部为组织因素，底部为后果）
            y = 4 - layer  # 反转Y轴，使组织因素在顶部
            
            # X坐标：在该层内均匀分布，并根据类别稍作偏移
            layer_width = max(layer_counts[layer], 1)
            if layer_width == 1:
                x = category_x_offset
            else:
                x_base = (layer_positions[layer] / (layer_width - 1)) * 8 - 4  # 分布在-4到4之间
                x = x_base + category_x_offset * 0.3  # 加上类别偏移
            
            pos[node.id] = (x, y)
            layer_positions[layer] += 1
        
        # 如果节点太少，使用备用布局
        if len(diagram.nodes) < 3:
            try:
                pos = nx.spring_layout(G, k=2, iterations=50)
            except:
                pos = nx.circular_layout(G)
        
        return pos

def main():
    """测试函数"""
    generator = CausalDiagramGenerator()
    
    test_narrative = """
    在一次训练飞行中，无人机在1500英尺高度巡航时突然失去了与地面控制站的通信连接。
    飞行员尝试重新建立联系但未成功，无人机自动启动了返航模式。
    天气条件良好，能见度清晰。后来发现是通信设备的天线连接松动导致了通信中断。
    这暴露了维护检查程序的不足，以及应急程序培训的缺陷。
    """
    
    diagram = generator.generate_causal_diagram(test_narrative)
    
    print("=== 因果图分析结果 ===")
    print(f"中心事件: {diagram.central_event}")
    print(f"节点数量: {len(diagram.nodes)}")
    print(f"关系数量: {len(diagram.relationships)}")
    print(f"风险路径: {len(diagram.risk_paths)}")
    print(f"控制点: {len(diagram.control_points)}")
    
    # 打印节点信息
    print("\n节点详情:")
    for node in diagram.nodes:
        print(f"- {node.name} ({node.type}, {node.category}): {node.description}")

if __name__ == "__main__":
    main()