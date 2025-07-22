"""
HFACS 8.0 Human Factors Analysis Module
Incident analysis based on Human Factors Analysis and Classification System 8.0 framework
Professional implementation referencing GT_Run_Auto.py
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
from translations import get_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 18 HFACS 8.0 category definitions (from GT_Run_Auto.py)
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

# HFACS four layers
HFACS_LAYERS = [
    "UNSAFE ACTS",
    "PRECONDITIONS",
    "SUPERVISION/LEADERSHIP",
    "ORGANIZATIONAL INFLUENCES"
]

# Category to layer mapping
CATEGORY_TO_LAYER = {}
for category in HFACS_CATEGORIES:
    for layer in HFACS_LAYERS:
        if category.startswith(layer):
            CATEGORY_TO_LAYER[category] = layer
            break

@dataclass
class HFACSClassification:
    """HFACS Classification Result"""
    category: str
    layer: str
    confidence: float
    reasoning: str
    evidence: List[str]

@dataclass
class HFACSAnalysisResult:
    """HFACS Analysis Result"""
    classifications: List[HFACSClassification]
    primary_factors: List[str]
    contributing_factors: List[str]
    recommendations: List[str]
    analysis_summary: str
    confidence_score: float
    analysis_timestamp: str
    visualization_data: Dict

class HFACSAnalyzer:
    """HFACS 8.0 Analyzer - Professional implementation based on GT_Run_Auto.py"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize HFACS Analyzer

        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')

        if not self.api_key:
            logger.warning("OpenAI API key not set, will use mock analysis")
            self.use_mock = True
        else:
            self.use_mock = False
    
    def _is_dark_color(self, hex_color: str) -> bool:
        """
        Determine if color is dark
        Used for intelligent text color selection to ensure readability
        
        Args:
            hex_color: Hexadecimal color code, e.g., '#FF0000'
            
        Returns:
            bool: True for dark color, False for light color
        """
        try:
            # Remove # sign
            hex_color = hex_color.lstrip('#')
            
            # Convert to RGB
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Calculate brightness (using relative luminance formula)
            # Formula source: https://en.wikipedia.org/wiki/Relative_luminance
            r, g, b = [x/255.0 for x in rgb]
            luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
            
            # Brightness less than 0.5 is considered dark
            return luminance < 0.5
        except (ValueError, IndexError):
            # If color format is incorrect, default to dark
            return True

        # System prompt (professional prompt based on GT_Run_Auto.py, further enhanced)
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
        Perform HFACS analysis

        Args:
            incident_data: Incident data

        Returns:
            HFACSAnalysisResult: HFACS analysis result
        """
        try:
            if self.use_mock:
                return self._mock_hfacs_analysis(incident_data)
            else:
                return self._openai_hfacs_analysis(incident_data)
        except Exception as e:
            logger.error(f"HFACS analysis failed: {e}")
            return self._fallback_hfacs_analysis(incident_data)

    def _create_hfacs_function_schema(self):
        """Create HFACS analysis Function Schema"""
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
        """HFACS analysis using OpenAI"""

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

            logger.info(f"Sending HFACS analysis request to OpenAI...")
            response = requests.post(url, headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                message = result['choices'][0]['message']

                if 'function_call' in message:
                    function_result = json.loads(message['function_call']['arguments'])
                    parsed_result = self._parse_function_response(function_result, incident_data)
                    logger.info(f"HFACS analysis completed. Found {len(parsed_result.classifications)} classifications")
                    return parsed_result
                else:
                    # If no function call, try to parse normal response
                    analysis_text = message['content']
                    logger.warning("No function call in response, parsing text response")
                    return self._parse_hfacs_response(analysis_text, incident_data)
            else:
                logger.error(f"OpenAI HFACS analysis failed: {response.status_code} - {response.text}")
                return self._fallback_hfacs_analysis(incident_data)

        except Exception as e:
            logger.error(f"OpenAI HFACS analysis failed: {e}")
            return self._fallback_hfacs_analysis(incident_data)

    def _parse_function_response(self, result: Dict, incident_data: Dict) -> HFACSAnalysisResult:
        """Parse Function Call response"""

        classifications = []
        for item in result.get("classifications", []):
            # Validate category against known HFACS categories
            category = item.get("category", "")
            layer = item.get("layer", "")

            # Ensure category is in our known list
            if category in HFACS_CATEGORIES:
                # Ensure layer matches category
                expected_layer = CATEGORY_TO_LAYER.get(category, layer)
                if layer != expected_layer:
                    logger.warning(f"Layer mismatch for {category}: got {layer}, expected {expected_layer}")
                    layer = expected_layer

                classifications.append(HFACSClassification(
                    category=category,
                    layer=layer,
                    confidence=item.get("confidence", 0.0),
                    reasoning=item.get("reasoning", ""),
                    evidence=item.get("evidence", [])
                ))
            else:
                logger.warning(f"Unknown HFACS category: {category}")

        logger.info(f"Parsed {len(classifications)} valid HFACS classifications")
        for cls in classifications:
            logger.info(f"  - {cls.category} (confidence: {cls.confidence:.2f})")

        # Generate visualization data
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
        """Build HFACS analysis prompt"""

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
        """Generate visualization data"""

        # Statistics by layer
        layer_counts = {}
        layer_confidence = {}

        for classification in classifications:
            layer = classification.layer
            layer_counts[layer] = layer_counts.get(layer, 0) + 1
            if layer not in layer_confidence:
                layer_confidence[layer] = []
            layer_confidence[layer].append(classification.confidence)

        # Calculate average confidence
        layer_avg_confidence = {}
        for layer, confidences in layer_confidence.items():
            layer_avg_confidence[layer] = sum(confidences) / len(confidences)

        # Statistics by category
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
        """Create HFACS visualization charts"""

        visualizations = {}

        if not result.classifications:
            logger.warning("No classifications found for visualization")
            return visualizations

        logger.info(f"Creating visualizations for {len(result.classifications)} classifications")

        # 1. Layer distribution pie chart
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
            logger.info(f"Created layer distribution pie chart with {len(layer_counts)} layers")

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
    
    def create_hfacs_pyramid_visualization(self, result: HFACSAnalysisResult) -> go.Figure:
        """Create an improved HFACS pyramid visualization with clear layered structure"""
        
        # Define the four layers in hierarchical order (top to bottom)
        layers = {
            'ORGANIZATIONAL INFLUENCES': {
                'level': 0,
                'color': '#8B5CF6',
                'categories': [
                    'ORGANIZATIONAL INFLUENCES—Climate/Culture',
                    'ORGANIZATIONAL INFLUENCES—Policy/Procedures/Process', 
                    'ORGANIZATIONAL INFLUENCES—Resource Support',
                    'ORGANIZATIONAL INFLUENCES—Training Program Issues'
                ]
            },
            'SUPERVISION/LEADERSHIP': {
                'level': 1, 
                'color': '#3B82F6',
                'categories': [
                    'SUPERVISION/LEADERSHIP—Unit Safety Culture',
                    'SUPERVISION/LEADERSHIP—Supervisory Known Deviations',
                    'SUPERVISION/LEADERSHIP—Ineffective Supervision',
                    'SUPERVISION/LEADERSHIP—Ineffective Planning & Coordination'
                ]
            },
            'PRECONDITIONS': {
                'level': 2,
                'color': '#F59E0B', 
                'categories': [
                    'PRECONDITIONS—Physical Environment',
                    'PRECONDITIONS—Technological Environment',
                    'PRECONDITIONS—Team Coordination/Communication',
                    'PRECONDITIONS—Training Conditions',
                    'PRECONDITIONS—Mental Awareness (Attention)',
                    'PRECONDITIONS—State of Mind',
                    'PRECONDITIONS—Adverse Physiological'
                ]
            },
            'UNSAFE ACTS': {
                'level': 3,
                'color': '#EF4444',
                'categories': [
                    'UNSAFE ACTS—Errors—Performance/Skill-Based',
                    'UNSAFE ACTS—Errors—Judgement & Decision-Making', 
                    'UNSAFE ACTS—Known Deviations'
                ]
            }
        }
        
        # Get identified categories
        identified_categories = set()
        if result.classifications:
            identified_categories = {cls.category for cls in result.classifications if cls.confidence > 0.3}
        
        fig = go.Figure()
        
        # Create layered pyramid visualization
        for layer_name, layer_info in layers.items():
            level = layer_info['level']
            base_color = layer_info['color']
            
            # Draw layer background
            y_center = 3 - level * 0.7  # Spacing between layers
            layer_width = 8 - level * 1.5  # Pyramid shape - narrower at top
            
            # Add layer background rectangle
            fig.add_shape(
                type="rect",
                x0=-layer_width/2, y0=y_center-0.25,
                x1=layer_width/2, y1=y_center+0.25,
                fillcolor=f"rgba{tuple(list(int(base_color[i:i+2], 16) for i in (1, 3, 5)) + [0.2])}",
                line=dict(color=base_color, width=2),
                layer="below"
            )
            
            # Add layer title
            fig.add_annotation(
                x=-layer_width/2 - 1, y=y_center,
                text=f"<b>{layer_name}</b>",
                showarrow=False,
                font=dict(size=16, color=base_color, family="Arial Black"),
                xanchor="right",
                yanchor="middle"
            )
            
            # Position categories within the layer
            categories = layer_info['categories']
            for i, category in enumerate(categories):
                if category in HFACS_CATEGORIES:  # Only show valid HFACS categories
                    # Calculate position within the layer
                    cat_count = len(categories)
                    spacing = layer_width / (cat_count + 1)
                    x_pos = -layer_width/2 + (i + 1) * spacing
                    
                    # Determine if this category is identified
                    is_identified = category in identified_categories
                    
                    # Choose visual properties
                    if is_identified:
                        marker_color = base_color
                        marker_size = 20
                        text_color = '#FFFFFF'
                        border_color = '#FFFFFF'
                        border_width = 3
                        opacity = 1.0
                    else:
                        marker_color = '#E5E7EB'
                        marker_size = 16
                        text_color = '#6B7280'
                        border_color = '#D1D5DB'
                        border_width = 2
                        opacity = 0.7
                    
                    # Simplify category name for display
                    display_name = category.split('—')[-1] if '—' in category else category
                    if len(display_name) > 18:
                        display_name = display_name[:15] + '...'
                    
                    # Add category marker
                    fig.add_trace(go.Scatter(
                        x=[x_pos], y=[y_center],
                        mode='markers+text',
                        marker=dict(
                            size=marker_size,
                            color=marker_color,
                            symbol='circle',
                            line=dict(color=border_color, width=border_width),
                            opacity=opacity
                        ),
                        text=display_name,
                        textposition="bottom center",
                        textfont=dict(size=10, color=text_color, family="Arial Bold"),
                        name=layer_name,
                        showlegend=False,
                        hovertemplate=(
                            f"<b>{category}</b><br>" + 
                            (f"<b>Status:</b> Identified<br>" if is_identified else "<b>Status:</b> Not identified<br>") +
                            (f"<b>Confidence:</b> {next((cls.confidence for cls in result.classifications if cls.category == category), 0):.1%}<br>" if is_identified else "") +
                            (f"<b>Analysis:</b> {next((cls.reasoning[:100] + '...' if len(cls.reasoning) > 100 else cls.reasoning for cls in result.classifications if cls.category == category), '')}" if is_identified else "") +
                            "<extra></extra>"
                        )
                    ))
        
        # Add connecting lines to show hierarchy flow
        for i in range(3):  # Connect levels 0->1, 1->2, 2->3
            y_from = 3 - i * 0.7
            y_to = 3 - (i + 1) * 0.7
            
            # Add subtle connecting lines
            fig.add_shape(
                type="line",
                x0=-1, y0=y_from - 0.25,
                x1=-1, y1=y_to + 0.25,
                line=dict(color="#9CA3AF", width=2, dash="dot"),
                opacity=0.5
            )
            
            # Add arrow annotation
            fig.add_annotation(
                x=-1, y=(y_from + y_to) / 2,
                text="⬇",
                showarrow=False,
                font=dict(size=16, color="#6B7280"),
                xanchor="center"
            )
        
        # Add legend for identified vs not identified
        legend_items = [
            ('Identified Factors', layers['UNSAFE ACTS']['color']),
            ('Not Identified', '#E5E7EB')
        ]
        
        for i, (name, color) in enumerate(legend_items):
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(size=12, color=color, symbol='circle'),
                name=name,
                showlegend=True
            ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': '<b style="color: #1F2937; font-size: 32px;">🏗️ HFACS Hierarchical Analysis Framework</b><br>' +
                       '<span style="color: #6B7280; font-size: 18px;">Four-Layer Human Factors Pyramid • Organizational to Individual Flow</span>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 28, 'color': '#1F2937', 'family': 'Arial Black'}
            },
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.98,
                xanchor="left", 
                x=1.02,
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='rgba(107,114,128,0.3)',
                borderwidth=1,
                font=dict(size=12, color='#374151', family='Arial')
            ),
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                range=[-7, 6]
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                range=[-0.5, 4]
            ),
            plot_bgcolor='#FEFEFE',
            paper_bgcolor='#FFFFFF',
            width=1600,
            height=1000,
            margin=dict(t=140, b=60, l=200, r=200),
            font=dict(family='Arial', size=12, color='#374151')
        )
        
        # Add layer level annotations on the right
        layer_labels = [
            ("Level 1: Organizational", 3, '#8B5CF6'),
            ("Level 2: Supervisory", 2.3, '#3B82F6'),
            ("Level 3: Preconditions", 1.6, '#F59E0B'),
            ("Level 4: Unsafe Acts", 0.9, '#EF4444')
        ]
        
        for label, y_pos, color in layer_labels:
            fig.add_annotation(
                x=5.5, y=y_pos,
                text=f"<b>{label}</b>",
                showarrow=False,
                font=dict(size=14, color=color, family="Arial Bold"),
                xanchor="left",
                yanchor="middle",
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor=color,
                borderwidth=1
            )
        
        return fig

    def create_hfacs_tree_visualization(self, result: HFACSAnalysisResult) -> go.Figure:
        """Create professional HFACS Four-Layer 18-Category Tree Visualization with enhanced layout"""
        
        # Professional color scheme for enhanced readability
        layer_colors = {
            'HFACS Framework': '#1A365D',          # Deep navy - Root node
            'UNSAFE ACTS': '#E53E3E',              # Bright red - Unsafe acts
            'PRECONDITIONS': '#D69E2E',            # Golden orange - Preconditions  
            'SUPERVISION/LEADERSHIP': '#3182CE',   # Professional blue - Supervision
            'ORGANIZATIONAL INFLUENCES': '#9F7AEA' # Professional purple - Organization
        }
        
        # Enhanced node positioning for better readability and professional layout
        positions = {
            # Root node - centered at top
            'HFACS Framework': (0, 5),
            
            # Layer 1 - UNSAFE ACTS (spread wider for better readability)
            'UNSAFE ACTS': (-5, 4),
            'UNSAFE ACTS—Errors—Performance/Skill-Based': (-6.5, 3),
            'UNSAFE ACTS—Errors—Judgement & Decision-Making': (-5, 3),
            'UNSAFE ACTS—Known Deviations': (-3.5, 3),
            
            # Layer 2 - PRECONDITIONS (better vertical spacing)
            'PRECONDITIONS': (-1.5, 4),
            'PRECONDITIONS—Physical Environment': (-3.2, 2.8),
            'PRECONDITIONS—Technological Environment': (-2.2, 2.8),
            'PRECONDITIONS—Team Coordination/Communication': (-1.2, 2.8),
            'PRECONDITIONS—Training Conditions': (-0.2, 2.8),
            'PRECONDITIONS—Mental Awareness (Attention)': (-2.8, 1.8),
            'PRECONDITIONS—State of Mind': (-1.8, 1.8),
            'PRECONDITIONS—Adverse Physiological': (-0.8, 1.8),
            
            # Layer 3 - SUPERVISION/LEADERSHIP (improved spacing)
            'SUPERVISION/LEADERSHIP': (1.8, 4),
            'SUPERVISION/LEADERSHIP—Unit Safety Culture': (0.8, 2.8),
            'SUPERVISION/LEADERSHIP—Supervisory Known Deviations': (1.8, 2.8),
            'SUPERVISION/LEADERSHIP—Ineffective Supervision': (2.8, 2.8),
            'SUPERVISION/LEADERSHIP—Ineffective Planning & Coordination': (1.8, 1.8),
            
            # Layer 4 - ORGANIZATIONAL INFLUENCES (better distribution)
            'ORGANIZATIONAL INFLUENCES': (5, 4),
            'ORGANIZATIONAL INFLUENCES—Climate/Culture': (4, 2.8),
            'ORGANIZATIONAL INFLUENCES—Policy/Procedures/Process': (5, 2.8),
            'ORGANIZATIONAL INFLUENCES—Resource Support': (6, 2.8),
            'ORGANIZATIONAL INFLUENCES—Training Program Issues': (5, 1.8),
        }
        
        # 创建图形对象
        fig = go.Figure()
        
        # 分析结果中识别的分类
        identified_categories = set()
        if result.classifications:
            identified_categories = {cls.category for cls in result.classifications}
            logger.info(f"Identified categories for visualization: {identified_categories}")
        else:
            logger.warning("No classifications found in result for visualization")
        
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
            # 确定节点样式 - 专业级视觉设计 - 修复字体颜色可读性
            if node == 'HFACS Framework':
                # 根节点 - 最显眼的钻石形状
                color = layer_colors[node]
                size = 40
                symbol = 'diamond'
                text_color = '#FFFFFF'  # 根节点保持白色，因为背景是深色
                border_color = '#0F2027'
                border_width = 4
            elif node in ['UNSAFE ACTS', 'PRECONDITIONS', 'SUPERVISION/LEADERSHIP', 'ORGANIZATIONAL INFLUENCES']:
                # 层级节点 - 突出的圆形节点 - 改用深色字体确保可读性
                color = layer_colors[node]
                size = 32
                symbol = 'circle'
                text_color = '#FFFFFF' if self._is_dark_color(layer_colors[node]) else '#2D3748'
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
                    # 根据背景颜色智能选择文字颜色
                    text_color = '#FFFFFF' if self._is_dark_color(base_color) else '#2D3748'
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
            
            # Enhanced text processing for better readability
            display_text = node
            if '—' in node:
                # Split long category names into multiple lines for better readability
                parts = node.split('—')
                if len(parts) > 1:
                    category_part = parts[-1]
                    # Break long text into multiple lines if needed
                    if len(category_part) > 18:
                        words = category_part.split(' ')
                        if len(words) > 2:
                            mid = len(words) // 2
                            display_text = ' '.join(words[:mid]) + '<br>' + ' '.join(words[mid:])
                        else:
                            # If very long single words, truncate with ellipsis
                            display_text = category_part[:15] + '...' if len(category_part) > 18 else category_part
                    else:
                        display_text = category_part
            elif len(node) > 18 and node not in ['UNSAFE ACTS', 'PRECONDITIONS', 'SUPERVISION/LEADERSHIP', 'ORGANIZATIONAL INFLUENCES']:
                # Handle other long node names
                display_text = node[:15] + '...'
            
            # Determine appropriate font size for readability
            if node == 'HFACS Framework':
                font_size = 18
                font_family = "Arial Black"
            elif node in ['UNSAFE ACTS', 'PRECONDITIONS', 'SUPERVISION/LEADERSHIP', 'ORGANIZATIONAL INFLUENCES']:
                font_size = 14
                font_family = "Arial Bold"
            else:
                font_size = 11
                font_family = "Arial"
            
            # Add node with enhanced styling
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
                    size=font_size,
                    color=text_color,
                    family=font_family
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
        
        # Enhanced professional layout settings
        fig.update_layout(
            title={
                'text': '<b style="color: #2D3748; font-size: 30px;">🌳 HFACS Four-Layer 18-Category Tree Visualization</b><br>' +
                       '<span style="color: #718096; font-size: 20px;">Professional Human Factors Analysis Framework • UAV Incident Assessment</span>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 26, 'color': '#2D3748', 'family': 'Arial Black'}
            },
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.98,
                xanchor="left",
                x=1.02,
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='rgba(113,128,150,0.4)',
                borderwidth=2,
                font=dict(size=12, color='#2D3748', family='Arial Bold')
            ),
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                range=[-8, 7.5]  # Further expanded range for better spacing
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                range=[1, 5.5]  # Adjusted for better vertical spacing
            ),
            plot_bgcolor='rgba(249,250,251,1)',  # Professional light background
            paper_bgcolor='#FFFFFF',
            width=1800,  # Further increased width for better readability
            height=1200,  # Further increased height for better spacing
            margin=dict(t=160, b=100, l=150, r=150),  # Enhanced margins
            font=dict(family='Arial', size=14, color='#2D3748')  # Larger base font
        )
        
        # Add professional informational annotations
        if identified_categories:
            identified_count = len(identified_categories)
            total_categories = 18
            
            # Calculate analysis statistics
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
        """Mock HFACS analysis with enhanced keyword detection"""

        narrative = incident_data.get('narrative', '').lower()
        human_factors = incident_data.get('human_factors', '').lower()
        all_text = f"{narrative} {human_factors}".lower()

        # Enhanced classification based on keywords
        classifications = []

        # UNSAFE ACTS - Errors
        if any(word in all_text for word in ['error', 'mistake', 'wrong', 'decision', 'misjudged', 'failed to']):
            classifications.append(HFACSClassification(
                category="UNSAFE ACTS—Errors—Judgement & Decision-Making",
                layer="UNSAFE ACTS",
                confidence=0.8,
                reasoning="Evidence of decision-making errors in the incident narrative",
                evidence=["Decision-related keywords found in narrative"]
            ))

        if any(word in all_text for word in ['skill', 'technique', 'performance', 'inexperience', 'proficiency']):
            classifications.append(HFACSClassification(
                category="UNSAFE ACTS—Errors—Performance/Skill-Based",
                layer="UNSAFE ACTS",
                confidence=0.7,
                reasoning="Performance or skill-based errors identified",
                evidence=["Skill-related factors mentioned"]
            ))

        # UNSAFE ACTS - Violations
        if any(word in all_text for word in ['violation', 'deviated', 'ignored', 'bypassed', 'shortcut']):
            classifications.append(HFACSClassification(
                category="UNSAFE ACTS—Known Deviations",
                layer="UNSAFE ACTS",
                confidence=0.7,
                reasoning="Evidence of procedural violations or deviations",
                evidence=["Violation-related keywords found"]
            ))

        # PRECONDITIONS - Environment
        if any(word in all_text for word in ['weather', 'wind', 'visibility', 'environment', 'conditions']):
            classifications.append(HFACSClassification(
                category="PRECONDITIONS—Physical Environment",
                layer="PRECONDITIONS",
                confidence=0.6,
                reasoning="Adverse physical environmental conditions identified",
                evidence=["Environmental factors mentioned"]
            ))

        # PRECONDITIONS - Communication
        if any(word in all_text for word in ['communication', 'coordination', 'team', 'radio', 'contact']):
            classifications.append(HFACSClassification(
                category="PRECONDITIONS—Team Coordination/Communication",
                layer="PRECONDITIONS",
                confidence=0.7,
                reasoning="Communication or coordination issues identified",
                evidence=["Communication-related factors mentioned"]
            ))

        # PRECONDITIONS - Training
        if any(word in all_text for word in ['training', 'experience', 'familiar', 'knowledge', 'preparation']):
            classifications.append(HFACSClassification(
                category="PRECONDITIONS—Training Conditions",
                layer="PRECONDITIONS",
                confidence=0.6,
                reasoning="Training or preparation deficiencies indicated",
                evidence=["Training-related issues mentioned"]
            ))

        # SUPERVISION/LEADERSHIP
        if any(word in all_text for word in ['supervision', 'oversight', 'monitoring', 'guidance']):
            classifications.append(HFACSClassification(
                category="SUPERVISION/LEADERSHIP—Ineffective Supervision",
                layer="SUPERVISION/LEADERSHIP",
                confidence=0.6,
                reasoning="Supervision or oversight deficiencies indicated",
                evidence=["Supervision issues mentioned"]
            ))

        # ORGANIZATIONAL INFLUENCES
        if any(word in all_text for word in ['policy', 'procedure', 'process', 'standard', 'regulation']):
            classifications.append(HFACSClassification(
                category="ORGANIZATIONAL INFLUENCES—Policy/Procedures/Process",
                layer="ORGANIZATIONAL INFLUENCES",
                confidence=0.5,
                reasoning="Organizational policy or process issues suggested",
                evidence=["Policy or procedural factors identified"]
            ))

        logger.info(f"Mock HFACS analysis completed. Found {len(classifications)} classifications")
        for cls in classifications:
            logger.info(f"  - {cls.category} (confidence: {cls.confidence:.2f})")

        # Generate visualization data
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
        """Fallback HFACS analysis with basic classification"""

        # Provide basic fallback classifications for demonstration
        fallback_classifications = [
            HFACSClassification(
                category="UNSAFE ACTS—Errors—Judgement & Decision-Making",
                layer="UNSAFE ACTS",
                confidence=0.4,
                reasoning="Fallback analysis - manual review required",
                evidence=["System analysis unavailable"]
            ),
            HFACSClassification(
                category="PRECONDITIONS—Training Conditions",
                layer="PRECONDITIONS",
                confidence=0.3,
                reasoning="Fallback analysis - manual review required",
                evidence=["System analysis unavailable"]
            )
        ]

        # Generate visualization data for fallback
        visualization_data = self._generate_visualization_data(fallback_classifications)

        return HFACSAnalysisResult(
            classifications=fallback_classifications,
            primary_factors=["Further analysis required"],
            contributing_factors=["System analysis temporarily unavailable"],
            recommendations=["Recommend expert manual HFACS analysis"],
            analysis_summary="System temporarily unable to perform detailed HFACS analysis. Basic fallback classifications provided for demonstration. Professional manual analysis recommended.",
            confidence_score=0.3,
            analysis_timestamp=datetime.now().isoformat(),
            visualization_data=visualization_data
        )
    
    def generate_hfacs_report(self, result: HFACSAnalysisResult, lang: str = 'zh') -> str:
        """Generate HFACS analysis report"""

        report = f"""
# {get_text('hfacs_report_title', lang)}

**{get_text('analysis_time', lang)}:** {result.analysis_timestamp}
**{get_text('confidence', lang)}:** {result.confidence_score:.2f}

## {get_text('analysis_summary', lang)}
{result.analysis_summary}

## {get_text('hfacs_classification_results', lang)}

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
                    report += f"- {get_text('analysis', lang)}: {classification.reasoning}\n"
                    report += f"- {get_text('confidence', lang)}: {classification.confidence:.2f}\n"
                    if classification.evidence:
                        report += f"- {get_text('evidence', lang)}: {', '.join(classification.evidence)}\n"
                    report += "\n"

        # 主要因素
        if result.primary_factors:
            report += f"## {get_text('primary_human_factors', lang)}\n\n"
            for i, factor in enumerate(result.primary_factors, 1):
                report += f"{i}. {factor}\n"
            report += "\n"

        # 贡献因素
        if result.contributing_factors:
            report += f"## {get_text('contributing_factors', lang)}\n\n"
            for i, factor in enumerate(result.contributing_factors, 1):
                report += f"{i}. {factor}\n"
            report += "\n"

        # 改进建议
        if result.recommendations:
            report += f"## {get_text('improvement_recommendations', lang)}\n\n"
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
    """Enhanced test function for HFACS analyzer"""
    print("Testing HFACS Analyzer...")

    # 测试数据
    test_incident = {
        'date': '2024-01-15',
        'flight_phase': 'Cruise',
        'mission_type': 'Training',
        'weather': 'VMC',
        'narrative': 'The pilot made a decision error during the flight which led to a communication breakdown. There was inadequate supervision and the training procedures were not followed properly. The pilot was fatigued and had insufficient training on the aircraft systems.',
        'human_factors': 'Decision making, Communication, Training, Fatigue',
        'primary_problem': 'Human Error',
        'contributing_factors': 'Inadequate training, poor communication protocols, fatigue'
    }

    print(f"Analyzing incident: {test_incident['narrative'][:100]}...")

    # 创建分析器并测试
    analyzer = HFACSAnalyzer()
    result = analyzer.analyze_hfacs(test_incident)

    print("HFACS分析结果:")
    print(f"识别的分类数量: {len(result.classifications) if result.classifications else 0}")

    if result.classifications:
        print("识别的分类:")
        for cls in result.classifications:
            print(f"  - {cls.category} (层级: {cls.layer}, 置信度: {cls.confidence:.2f})")

    print(f"主要因素: {result.primary_factors}")
    print(f"建议措施: {result.recommendations}")
    print(f"置信度: {result.confidence_score}")

    # 测试可视化
    try:
        tree_fig = analyzer.create_hfacs_tree_visualization(result)
        print("✅ 树状图可视化创建成功")
    except Exception as e:
        print(f"❌ 树状图可视化失败: {e}")

    try:
        viz_charts = analyzer.create_hfacs_visualizations(result)
        print(f"✅ 创建了 {len(viz_charts)} 个可视化图表")
    except Exception as e:
        print(f"❌ 可视化图表创建失败: {e}")

    # 生成报告
    try:
        report = analyzer.generate_hfacs_report(result)
        print("\n" + "="*50)
        print("生成的报告:")
        print(report[:500] + "..." if len(report) > 500 else report)
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")

if __name__ == "__main__":
    main()
