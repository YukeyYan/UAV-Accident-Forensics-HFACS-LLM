"""
专业事故调查分析引擎
LLM驱动的深度无人机事故调查分析系统
"""

import requests
import json
import logging
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import os
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InvestigationFinding:
    """调查发现"""
    category: str
    finding: str
    evidence: List[str]
    severity: str  # HIGH, MEDIUM, LOW
    confidence: float
    recommendations: List[str]

@dataclass
class SwissCheeseLayer:
    """瑞士奶酪模型层级"""
    layer_name: str
    layer_type: str  # organizational, supervision, preconditions, acts
    defects: List[str]
    barriers: List[str]
    effectiveness: float
    failure_mode: str

@dataclass 
class InvestigationResult:
    """调查分析结果"""
    executive_summary: str
    findings: List[InvestigationFinding]
    swiss_cheese_analysis: List[SwissCheeseLayer]
    timeline_reconstruction: List[Dict]
    contributing_factors: Dict[str, List[str]]
    safety_barriers: Dict[str, Dict]
    risk_assessment: Dict
    recommendations: List[Dict]
    lessons_learned: List[str]
    confidence_score: float
    analysis_timestamp: str

class ProfessionalInvestigationEngine:
    """专业事故调查分析引擎"""
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化调查引擎"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            logger.warning("未设置OpenAI API密钥，将使用模拟分析")
            self.use_mock = True
        else:
            self.use_mock = False
            
        # 专业调查系统提示词
        self.system_prompt = """You are a senior aviation safety investigator with 20+ years of experience in UAV incident investigation.

Your mission is to conduct a comprehensive professional investigation of UAV incidents using industry best practices.

INVESTIGATION FRAMEWORK:
You will analyze the incident from multiple professional perspectives:

1. EXECUTIVE SUMMARY
- Concise overview of the incident
- Primary causal factors
- Safety significance
- Investigation methodology

2. DETAILED FINDINGS
Categorize findings into:
- IMMEDIATE CAUSES: Direct factors that led to the incident
- CONTRIBUTING FACTORS: Conditions that enabled the incident
- SYSTEMIC ISSUES: Organizational/procedural weaknesses
- HUMAN FACTORS: Operator performance and decision-making
- TECHNICAL FACTORS: Equipment/system performance
- ENVIRONMENTAL FACTORS: Weather, terrain, operational context

3. SWISS CHEESE MODEL ANALYSIS
Analyze defense layers and their failures:
- ORGANIZATIONAL LEVEL: Management decisions, resource allocation, safety culture
- SUPERVISION LEVEL: Training, oversight, procedures, planning
- PRECONDITIONS LEVEL: Environmental factors, operator state, team dynamics
- UNSAFE ACTS LEVEL: Errors, violations, decision failures

For each layer, identify:
- Specific defects/holes in the defense
- Remaining barriers that functioned
- Effectiveness rating (0.0-1.0)
- Failure mode description

4. TIMELINE RECONSTRUCTION
Create detailed chronological sequence:
- Pre-incident conditions and decisions
- Critical events during the occurrence
- Post-incident response and recovery
- Decision points and missed opportunities

5. CONTRIBUTING FACTORS MATRIX
Organize factors by:
- Human Factors (training, experience, workload, etc.)
- Technical Factors (equipment, design, maintenance, etc.)  
- Environmental Factors (weather, airspace, terrain, etc.)
- Organizational Factors (procedures, culture, resources, etc.)

6. SAFETY BARRIER ANALYSIS
Evaluate defense mechanisms:
- PREVENTIVE BARRIERS: Designed to prevent incidents
- PROTECTIVE BARRIERS: Designed to mitigate consequences
- Barrier effectiveness and failure modes
- Recommendations for improvement

7. RISK ASSESSMENT
- Probability of recurrence
- Severity of potential consequences
- Risk matrix classification
- Risk mitigation priorities

8. RECOMMENDATIONS
Structured by:
- IMMEDIATE ACTIONS: Urgent safety measures
- SHORT-TERM ACTIONS: 1-6 months implementation
- LONG-TERM ACTIONS: Strategic improvements
- SYSTEMIC CHANGES: Organizational/regulatory improvements

9. LESSONS LEARNED
- Key insights for the aviation community
- Broader applicability beyond this incident
- Best practices and cautionary guidance

ANALYSIS STANDARDS:
- Use aviation industry terminology and standards
- Reference applicable regulations and guidance (Part 107, AC, etc.)
- Apply systematic investigation methodologies
- Maintain objectivity and evidence-based conclusions
- Consider human factors and organizational influences
- Address both technical and non-technical aspects

EVIDENCE-BASED APPROACH:
- Base conclusions on available evidence
- Clearly distinguish between facts and inferences
- Acknowledge limitations and uncertainties
- Provide confidence levels for key findings
- Support recommendations with clear rationale

OUTPUT REQUIREMENTS:
- Professional investigation report format
- Clear, actionable recommendations  
- Detailed supporting evidence
- Risk-based prioritization
- Industry-standard terminology"""

    def investigate_incident(self, incident_data: Dict) -> InvestigationResult:
        """进行专业事故调查分析"""
        try:
            if self.use_mock:
                return self._mock_investigation(incident_data)
            else:
                return self._llm_investigation(incident_data)
        except Exception as e:
            logger.error(f"专业调查分析失败: {e}")
            return self._fallback_investigation(incident_data)

    def _llm_investigation(self, incident_data: Dict) -> InvestigationResult:
        """使用LLM进行专业调查分析"""
        
        # 构建详细的分析提示
        analysis_prompt = self._build_investigation_prompt(incident_data)
        
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 使用function calling获取结构化结果
            data = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                "functions": [self._create_investigation_function_schema()],
                "function_call": {"name": "conduct_professional_investigation"},
                "temperature": 0.1,
                "max_tokens": 4000
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                message = result['choices'][0]['message']
                
                if 'function_call' in message:
                    function_result = json.loads(message['function_call']['arguments'])
                    return self._parse_investigation_result(function_result, incident_data)
                else:
                    # 备用解析
                    return self._parse_text_investigation(message['content'], incident_data)
            else:
                logger.error(f"OpenAI API调用失败: {response.status_code}")
                return self._fallback_investigation(incident_data)
                
        except Exception as e:
            logger.error(f"LLM调查分析失败: {e}")
            return self._fallback_investigation(incident_data)

    def _build_investigation_prompt(self, incident_data: Dict) -> str:
        """构建专业调查分析提示"""
        
        narrative = incident_data.get('narrative', incident_data.get('detailed_narrative', ''))
        
        prompt = f"""Conduct a comprehensive professional investigation of this UAV incident:

**INCIDENT DETAILS:**
- Report ID: {incident_data.get('id', 'N/A')}
- Date: {incident_data.get('occurrence_date', 'N/A')}  
- Time: {incident_data.get('time_of_day', 'N/A')}
- Location: {incident_data.get('location_city', 'N/A')}
- Weather: {incident_data.get('weather_conditions', 'N/A')}
- Flight Phase: {incident_data.get('flight_phase', 'N/A')}
- Aircraft Type: {incident_data.get('aircraft_make', 'N/A')} {incident_data.get('aircraft_model', 'N/A')}
- Operator Qualification: {incident_data.get('pilot_qualification', 'N/A')}
- Incident Type: {incident_data.get('incident_type', 'N/A')}

**DETAILED NARRATIVE:**
{narrative}

**ADDITIONAL CONTEXT:**
- Primary Problem: {incident_data.get('primary_problem', 'N/A')}
- Contributing Factors: {incident_data.get('contributing_factors', 'N/A')}
- Human Factors: {incident_data.get('human_factors', 'N/A')}
- Equipment Factors: {incident_data.get('equipment_factors', 'N/A')}
- Environmental Factors: {incident_data.get('environmental_factors', 'N/A')}

**INVESTIGATION REQUIREMENTS:**
Please conduct a thorough professional investigation following aviation industry standards. Provide:

1. Executive summary with key findings
2. Detailed investigation findings by category
3. Swiss cheese model analysis with specific layer defects
4. Timeline reconstruction of critical events
5. Contributing factors matrix
6. Safety barrier analysis
7. Risk assessment and classification
8. Structured recommendations by timeframe
9. Lessons learned for the aviation community

Use evidence-based analysis and maintain professional investigation standards throughout."""

        return prompt

    def _create_investigation_function_schema(self):
        """创建专业调查Function Schema"""
        return {
            "name": "conduct_professional_investigation",
            "description": "Conduct comprehensive professional UAV incident investigation",
            "parameters": {
                "type": "object",
                "properties": {
                    "executive_summary": {
                        "type": "string",
                        "description": "Concise executive summary of the investigation"
                    },
                    "findings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "category": {"type": "string", "description": "Finding category"},
                                "finding": {"type": "string", "description": "Detailed finding"},
                                "evidence": {"type": "array", "items": {"type": "string"}, "description": "Supporting evidence"},
                                "severity": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                                "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                "recommendations": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    },
                    "swiss_cheese_analysis": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "layer_name": {"type": "string"},
                                "layer_type": {"type": "string", "enum": ["organizational", "supervision", "preconditions", "acts"]},
                                "defects": {"type": "array", "items": {"type": "string"}},
                                "barriers": {"type": "array", "items": {"type": "string"}},
                                "effectiveness": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                "failure_mode": {"type": "string"}
                            }
                        }
                    },
                    "timeline_reconstruction": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "time": {"type": "string"},
                                "event": {"type": "string"},
                                "significance": {"type": "string", "enum": ["critical", "major", "minor"]},
                                "decision_point": {"type": "boolean"}
                            }
                        }
                    },
                    "contributing_factors": {
                        "type": "object",
                        "properties": {
                            "human_factors": {"type": "array", "items": {"type": "string"}},
                            "technical_factors": {"type": "array", "items": {"type": "string"}},
                            "environmental_factors": {"type": "array", "items": {"type": "string"}},
                            "organizational_factors": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "safety_barriers": {
                        "type": "object",
                        "properties": {
                            "preventive": {
                                "type": "object",
                                "properties": {
                                    "existing": {"type": "array", "items": {"type": "string"}},
                                    "failed": {"type": "array", "items": {"type": "string"}},
                                    "missing": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "protective": {
                                "type": "object", 
                                "properties": {
                                    "existing": {"type": "array", "items": {"type": "string"}},
                                    "failed": {"type": "array", "items": {"type": "string"}},
                                    "missing": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        }
                    },
                    "risk_assessment": {
                        "type": "object",
                        "properties": {
                            "probability": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                            "severity": {"type": "string", "enum": ["CATASTROPHIC", "MAJOR", "MODERATE", "MINOR"]},
                            "risk_level": {"type": "string", "enum": ["UNACCEPTABLE", "TOLERABLE", "ACCEPTABLE"]},
                            "recurrence_likelihood": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                        }
                    },
                    "recommendations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "timeframe": {"type": "string", "enum": ["IMMEDIATE", "SHORT_TERM", "LONG_TERM", "SYSTEMIC"]},
                                "category": {"type": "string"},
                                "recommendation": {"type": "string"},
                                "rationale": {"type": "string"},
                                "priority": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]}
                            }
                        }
                    },
                    "lessons_learned": {"type": "array", "items": {"type": "string"}},
                    "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                },
                "required": ["executive_summary", "findings", "swiss_cheese_analysis", "timeline_reconstruction", "contributing_factors", "safety_barriers", "risk_assessment", "recommendations", "lessons_learned", "confidence_score"]
            }
        }

    def _parse_investigation_result(self, result: Dict, incident_data: Dict) -> InvestigationResult:
        """解析专业调查结果"""
        
        # 解析findings
        findings = []
        for f in result.get("findings", []):
            findings.append(InvestigationFinding(
                category=f.get("category", ""),
                finding=f.get("finding", ""),
                evidence=f.get("evidence", []),
                severity=f.get("severity", "MEDIUM"),
                confidence=f.get("confidence", 0.5),
                recommendations=f.get("recommendations", [])
            ))
        
        # 解析Swiss Cheese分析
        swiss_cheese_analysis = []
        for layer in result.get("swiss_cheese_analysis", []):
            swiss_cheese_analysis.append(SwissCheeseLayer(
                layer_name=layer.get("layer_name", ""),
                layer_type=layer.get("layer_type", ""),
                defects=layer.get("defects", []),
                barriers=layer.get("barriers", []),
                effectiveness=layer.get("effectiveness", 0.5),
                failure_mode=layer.get("failure_mode", "")
            ))
        
        return InvestigationResult(
            executive_summary=result.get("executive_summary", ""),
            findings=findings,
            swiss_cheese_analysis=swiss_cheese_analysis,
            timeline_reconstruction=result.get("timeline_reconstruction", []),
            contributing_factors=result.get("contributing_factors", {}),
            safety_barriers=result.get("safety_barriers", {}),
            risk_assessment=result.get("risk_assessment", {}),
            recommendations=result.get("recommendations", []),
            lessons_learned=result.get("lessons_learned", []),
            confidence_score=result.get("confidence_score", 0.5),
            analysis_timestamp=datetime.now().isoformat()
        )

    def _mock_investigation(self, incident_data: Dict) -> InvestigationResult:
        """模拟专业调查分析 - 基于实际数据的丰富分析"""
        
        narrative = incident_data.get('narrative', incident_data.get('detailed_narrative', ''))
        incident_type = incident_data.get('incident_type', 'Unknown')
        
        # 基于叙述内容生成真实分析
        findings = []
        
        # 分析关键词来生成相关findings
        if 'gps' in narrative.lower() or 'signal' in narrative.lower():
            findings.append(InvestigationFinding(
                category="Technical Factors",
                finding="GPS signal loss resulted in navigation degradation",
                evidence=["Narrative mentions GPS signal issues", "Flight mode change to attitude mode"],
                severity="HIGH",
                confidence=0.9,
                recommendations=["Implement backup navigation systems", "Enhanced pilot training on GPS-denied operations"]
            ))
        
        if 'wind' in narrative.lower() or 'weather' in narrative.lower():
            findings.append(InvestigationFinding(
                category="Environmental Factors", 
                finding="Adverse weather conditions contributed to loss of control",
                evidence=["Strong wind conditions reported", "Manual control difficulties noted"],
                severity="HIGH",
                confidence=0.8,
                recommendations=["Establish stricter weather minimums", "Improve weather assessment procedures"]
            ))
        
        if 'training' in narrative.lower() or 'pilot' in narrative.lower():
            findings.append(InvestigationFinding(
                category="Human Factors",
                finding="Pilot response to emergency situation suboptimal",
                evidence=["Manual control attempt unsuccessful", "Emergency procedures not fully effective"],
                severity="MEDIUM", 
                confidence=0.7,
                recommendations=["Enhanced emergency procedures training", "Regular proficiency checks"]
            ))
        
        # Swiss Cheese分析 - 基于实际情况
        swiss_cheese_analysis = [
            SwissCheeseLayer(
                layer_name="Organizational Influences",
                layer_type="organizational",
                defects=["Insufficient weather policy", "Inadequate risk assessment procedures"],
                barriers=["Written procedures exist", "Training program in place"],
                effectiveness=0.6,
                failure_mode="Policy gaps allowed operations in marginal conditions"
            ),
            SwissCheeseLayer(
                layer_name="Unsafe Supervision",
                layer_type="supervision",
                defects=["Limited pre-flight planning", "Insufficient weather briefing"],
                barriers=["Supervisor approval required", "Checklist procedures"],
                effectiveness=0.4,
                failure_mode="Supervision did not adequately assess conditions"
            ),
            SwissCheeseLayer(
                layer_name="Preconditions",
                layer_type="preconditions",
                defects=["GPS vulnerability", "Environmental conditions", "Pilot workload"],
                barriers=["Backup systems available", "Emergency procedures known"],
                effectiveness=0.3,
                failure_mode="Multiple precondition failures aligned"
            ),
            SwissCheeseLayer(
                layer_name="Unsafe Acts",
                layer_type="acts",
                defects=["Continued flight in degraded conditions", "Inadequate emergency response"],
                barriers=["Pilot training", "Standard procedures"],
                effectiveness=0.2,
                failure_mode="Pilot actions insufficient to prevent incident"
            )
        ]
        
        # 时间线重构
        timeline_reconstruction = [
            {"time": "Pre-flight", "event": "Flight planning and preparation", "significance": "minor", "decision_point": True},
            {"time": "Takeoff", "event": "Normal takeoff and initial climb", "significance": "minor", "decision_point": False},
            {"time": "Cruise", "event": "GPS signal loss detected", "significance": "critical", "decision_point": True},
            {"time": "Emergency", "event": "Aircraft entered attitude mode", "significance": "critical", "decision_point": False},
            {"time": "Response", "event": "Pilot attempted manual control", "significance": "critical", "decision_point": True},
            {"time": "Impact", "event": "Loss of control and crash", "significance": "critical", "decision_point": False}
        ]
        
        # 贡献因素矩阵
        contributing_factors = {
            "human_factors": ["Emergency response training", "Situational awareness", "Decision making under stress"],
            "technical_factors": ["GPS system reliability", "Backup navigation systems", "Flight control systems"],
            "environmental_factors": ["Wind conditions", "GPS signal interference", "Terrain features"],
            "organizational_factors": ["Weather policies", "Risk assessment procedures", "Training programs"]
        }
        
        # 安全屏障分析
        safety_barriers = {
            "preventive": {
                "existing": ["Pre-flight planning", "Weather assessment", "Pilot training"],
                "failed": ["GPS backup systems", "Weather decision making"],
                "missing": ["Real-time weather monitoring", "Enhanced GPS backup"]
            },
            "protective": {
                "existing": ["Emergency procedures", "Pilot training", "Aircraft design"],
                "failed": ["Manual control capability", "Emergency landing procedures"],
                "missing": ["Automatic recovery systems", "Enhanced emergency protocols"]
            }
        }
        
        # 风险评估
        risk_assessment = {
            "probability": "MEDIUM",
            "severity": "MAJOR", 
            "risk_level": "TOLERABLE",
            "recurrence_likelihood": 0.3
        }
        
        # 结构化建议
        recommendations = [
            {
                "timeframe": "IMMEDIATE",
                "category": "Operations",
                "recommendation": "Review and strengthen weather minimums for GPS-dependent operations",
                "rationale": "Prevent similar incidents in adverse conditions",
                "priority": "HIGH"
            },
            {
                "timeframe": "SHORT_TERM", 
                "category": "Training",
                "recommendation": "Enhance pilot training on GPS-denied operations and manual control",
                "rationale": "Improve pilot response to system failures",
                "priority": "HIGH"
            },
            {
                "timeframe": "LONG_TERM",
                "category": "Technology",
                "recommendation": "Implement redundant navigation systems and improved backup procedures",
                "rationale": "Reduce dependency on single navigation source",
                "priority": "MEDIUM"
            }
        ]
        
        # 经验教训
        lessons_learned = [
            "GPS signal loss can occur without warning in certain environmental conditions",
            "Manual control skills require regular practice and proficiency maintenance",
            "Multiple system failures can overwhelm pilot response capabilities",
            "Environmental conditions must be thoroughly assessed before GPS-dependent operations",
            "Backup navigation systems are essential for safe operations"
        ]
        
        return InvestigationResult(
            executive_summary=f"Investigation of {incident_type} incident involving GPS signal loss and subsequent loss of control. Multiple contributing factors identified across organizational, supervision, precondition, and unsafe act levels. Key findings indicate inadequate backup navigation systems and emergency response procedures.",
            findings=findings,
            swiss_cheese_analysis=swiss_cheese_analysis,
            timeline_reconstruction=timeline_reconstruction,
            contributing_factors=contributing_factors,
            safety_barriers=safety_barriers,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            lessons_learned=lessons_learned,
            confidence_score=0.8,
            analysis_timestamp=datetime.now().isoformat()
        )

    def _fallback_investigation(self, incident_data: Dict) -> InvestigationResult:
        """备用调查分析"""
        return InvestigationResult(
            executive_summary="基础调查分析已完成。建议进行更详细的专业调查。",
            findings=[InvestigationFinding(
                category="General",
                finding="需要更详细的事故调查分析",
                evidence=["系统分析能力有限"],
                severity="MEDIUM",
                confidence=0.3,
                recommendations=["使用专业调查工具", "收集更多证据"]
            )],
            swiss_cheese_analysis=[],
            timeline_reconstruction=[],
            contributing_factors={},
            safety_barriers={},
            risk_assessment={"probability": "UNKNOWN", "severity": "UNKNOWN", "risk_level": "UNKNOWN", "recurrence_likelihood": 0.0},
            recommendations=[],
            lessons_learned=["需要更完整的调查分析工具"],
            confidence_score=0.3,
            analysis_timestamp=datetime.now().isoformat()
        )

    def create_swiss_cheese_visualization(self, analysis: List[SwissCheeseLayer]) -> go.Figure:
        """创建瑞士奶酪模型可视化"""
        
        fig = go.Figure()
        
        # 层级颜色
        layer_colors = {
            "organizational": "#E74C3C",
            "supervision": "#F39C12",
            "preconditions": "#3498DB", 
            "acts": "#9B59B6"
        }
        
        y_positions = list(range(len(analysis)))
        
        # 绘制每一层
        for i, layer in enumerate(analysis):
            color = layer_colors.get(layer.layer_type, "#95A5A6")
            
            # 主层级矩形
            fig.add_shape(
                type="rect",
                x0=0, x1=10,
                y0=i-0.4, y1=i+0.4,
                fillcolor=color,
                opacity=0.3,
                line=dict(color=color, width=2)
            )
            
            # 根据有效性显示"洞"
            holes = int((1 - layer.effectiveness) * 5)  # 最多5个洞
            for j in range(holes):
                hole_x = 1.5 + j * 1.5
                fig.add_shape(
                    type="circle",
                    x0=hole_x-0.3, x1=hole_x+0.3,
                    y0=i-0.2, y1=i+0.2,
                    fillcolor="white",
                    line=dict(color="red", width=2)
                )
            
            # 添加层级标签 - 增强字体和可读性
            fig.add_annotation(
                x=-0.5, y=i,
                text=f"<b style='color: #2D3748; font-size: 14px;'>{layer.layer_name}</b><br>" +
                     f"<span style='color: #4A5568; font-size: 12px;'>({layer.effectiveness:.1%} effective)</span>",
                showarrow=False,
                xanchor="right",
                font=dict(size=13, color='#2D3748', family='Arial'),
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='rgba(113,128,150,0.2)',
                borderwidth=1
            )
        
        # 添加标题和样式 - 增强美观度
        fig.update_layout(
            title={
                'text': '<b style="color: #2D3748; font-size: 20px;">Swiss Cheese Model - Defense Layer Analysis</b>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#2D3748', 'family': 'Arial Black'}
            },
            xaxis=dict(range=[-3, 12], showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(range=[-1, len(analysis)], showticklabels=False, showgrid=False, zeroline=False),
            plot_bgcolor='rgba(247,250,252,1)',
            paper_bgcolor='white',
            height=450,
            margin=dict(t=80, b=40, l=120, r=40)
        )
        
        return fig

    def create_timeline_visualization(self, timeline: List[Dict]) -> go.Figure:
        """创建时间线可视化"""
        
        fig = go.Figure()
        
        # 重要性颜色映射
        significance_colors = {
            "critical": "#E74C3C",
            "major": "#F39C12", 
            "minor": "#3498DB"
        }
        
        x_vals = list(range(len(timeline)))
        y_vals = [1] * len(timeline)
        
        for i, event in enumerate(timeline):
            color = significance_colors.get(event.get("significance", "minor"), "#95A5A6")
            size = 20 if event.get("significance") == "critical" else 15 if event.get("significance") == "major" else 10
            
            # 决策点用不同形状
            symbol = "diamond" if event.get("decision_point", False) else "circle"
            
            fig.add_trace(go.Scatter(
                x=[i], y=[1],
                mode='markers',
                marker=dict(
                    size=size,
                    color=color,
                    symbol=symbol,
                    line=dict(color='white', width=2)
                ),
                text=[event.get("event", "")],
                textposition="top center",
                hovertemplate=f"<b>{event.get('time', '')}</b><br>{event.get('event', '')}<br>Significance: {event.get('significance', '')}<extra></extra>",
                showlegend=False
            ))
        
        # 连接线
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_vals,
            mode='lines',
            line=dict(color='gray', width=2),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.update_layout(
            title="Incident Timeline Reconstruction",
            xaxis_title="Timeline Progression",
            yaxis=dict(showticklabels=False, range=[0.5, 1.5]),
            height=300
        )
        
        return fig

    def create_risk_matrix(self, risk_assessment: Dict) -> go.Figure:
        """创建风险矩阵"""
        
        # 概率映射
        prob_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        
        # 严重性映射  
        sev_map = {"MINOR": 1, "MODERATE": 2, "MAJOR": 3, "CATASTROPHIC": 4}
        
        probability = prob_map.get(risk_assessment.get("probability", "MEDIUM"), 2)
        severity = sev_map.get(risk_assessment.get("severity", "MODERATE"), 2)
        
        # 风险矩阵颜色
        risk_colors = {
            1: "#2ECC71",  # 低风险 - 绿色
            2: "#F39C12",  # 中风险 - 橙色
            3: "#E74C3C"   # 高风险 - 红色
        }
        
        # 创建风险矩阵背景
        fig = go.Figure()
        
        # 绘制风险区域
        for p in range(1, 4):
            for s in range(1, 5):
                risk_level = min(3, max(1, (p + s) // 2))
                color = risk_colors[risk_level]
                
                fig.add_shape(
                    type="rect",
                    x0=p-0.5, x1=p+0.5,
                    y0=s-0.5, y1=s+0.5,
                    fillcolor=color,
                    opacity=0.3,
                    line=dict(color=color, width=1)
                )
        
        # 标记当前事件
        fig.add_trace(go.Scatter(
            x=[probability], y=[severity],
            mode='markers',
            marker=dict(
                size=25,
                color='black',
                symbol='x',
                line=dict(color='white', width=3)
            ),
            text=[f"This Incident<br>{risk_assessment.get('risk_level', 'UNKNOWN')}"],
            textposition="top center",
            showlegend=False
        ))
        
        fig.update_layout(
            title="Risk Assessment Matrix",
            xaxis=dict(
                title="Probability",
                tickvals=[1, 2, 3],
                ticktext=["Low", "Medium", "High"],
                range=[0.5, 3.5]
            ),
            yaxis=dict(
                title="Severity", 
                tickvals=[1, 2, 3, 4],
                ticktext=["Minor", "Moderate", "Major", "Catastrophic"],
                range=[0.5, 4.5]
            ),
            height=400
        )
        
        return fig

def main():
    """测试函数"""
    # 测试数据
    test_incident = {
        'id': 'TEST_001',
        'narrative': 'The DJI Phantom 4 experienced GPS signal loss during cruise flight at 150 feet. Strong winds caused the pilot to lose control when attempting manual flight. The aircraft crashed in an open field.',
        'incident_type': 'Loss of Control',
        'flight_phase': 'Cruise',
        'weather_conditions': 'VMC with strong winds'
    }
    
    # 创建调查引擎
    engine = ProfessionalInvestigationEngine()
    result = engine.investigate_incident(test_incident)
    
    print("专业调查分析结果:")
    print(f"执行摘要: {result.executive_summary}")
    print(f"发现数量: {len(result.findings)}")
    print(f"置信度: {result.confidence_score}")

if __name__ == "__main__":
    main()