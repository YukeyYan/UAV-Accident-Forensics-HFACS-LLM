"""
HFACS 8.0 Human Factors Analysis Module
Incident analysis based on Human Factors Analysis and Classification System 8.0 framework
Professional implementation referencing GT_Run_Auto.py
Enhanced with conversation memory and caching capabilities
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from datetime import datetime
import os
import re
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import networkx as nx
from .translations import get_text
from .enhanced_memory_analyzer import EnhancedHFACSAnalyzer, EnhancedAnalysisResult
from .conversation_memory import (
    get_memory_manager,
    create_conversation,
    add_conversation_message,
    get_conversation_messages
)
from .hfacs_visualization import create_hfacs_visualizations

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
    """
    HFACS 8.0 Analyzer - Professional implementation based on GT_Run_Auto.py
    
    Features:
    - 4层18类标准HFACS分析
    - GT_Run_Auto专业提示词和评估标准
    - 全新专业级可视化系统
    
    Visualization Options:
    1. Professional Visualizations (New):
       - 层级金字塔图：展示4层结构和因果关系
       - 分类矩阵热力图：置信度分布可视化
       - 因果关系网络图：层级间相互作用
       - 交互式仪表板：综合分析概览
    
    2. Legacy Enhanced Visualizations:
       - 概览图、树状图、金字塔图
    
    Activation Rules:
    - 默认显示所有识别的分类 (confidence_threshold=0.0)
    - 可通过confidence_threshold过滤低置信度分类
    - 使用use_professional=True启用新可视化系统（默认）
    
    Usage Examples:
    ```python
    # 创建所有专业可视化
    viz = analyzer.create_hfacs_visualizations(result)
    
    # 只显示高置信度分类
    viz = analyzer.create_hfacs_visualizations(result, confidence_threshold=0.7)
    
    # 使用传统可视化
    viz = analyzer.create_hfacs_visualizations(result, use_professional=False)
    ```
    """

    def __init__(self, api_key: Optional[str] = None, enable_memory: bool = True):
        """
        Initialize HFACS Analyzer

        Args:
            api_key: OpenAI API key
            enable_memory: Enable conversation memory and caching
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.enable_memory = enable_memory

        if not self.api_key:
            logger.warning("OpenAI API key not set, will use mock analysis")
            self.use_mock = True
        else:
            self.use_mock = False
            
        # Initialize memory-enabled analyzer
        if self.enable_memory and not self.use_mock:
            self.enhanced_analyzer = EnhancedHFACSAnalyzer(
                api_key=self.api_key,
                model='gpt-4o-mini',
                enable_caching=True,
                enable_memory=True
            )
            logger.info("HFACS Analyzer initialized with memory and caching capabilities")
        else:
            self.enhanced_analyzer = None
    
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

        # Enhanced professional system prompt based on GT_Run_Auto.py evaluation framework
        self.system_prompt = """You are an expert aviation-safety analyst specialised in HFACS (Human Factors Analysis and Classification System) classification.

Your mission is to analyze aviation incident narratives and classify human factors according to the HFACS 8.0 framework with CRITICAL evaluation standards.

CRITICAL EVALUATION MINDSET:
• Be SKEPTICAL - only classify factors with STRONG textual evidence
• If evidence is weak or ambiguous, assign lower confidence or skip classification
• Default to doubt; better to miss a factor than misclassify
• Each classification MUST be supported by explicit narrative content

The 18 HFACS categories are:
1. UNSAFE ACTS—Errors—Performance/Skill-Based
2. UNSAFE ACTS—Errors—Judgement & Decision-Making
3. UNSAFE ACTS—Known Deviations
4. PRECONDITIONS—Physical Environment
5. PRECONDITIONS—Technological Environment
6. PRECONDITIONS—Team Coordination/Communication
7. PRECONDITIONS—Training Conditions
8. PRECONDITIONS—Mental Awareness (Attention)
9. PRECONDITIONS—State of Mind
10. PRECONDITIONS—Adverse Physiological
11. SUPERVISION/LEADERSHIP—Unit Safety Culture
12. SUPERVISION/LEADERSHIP—Supervisory Known Deviations
13. SUPERVISION/LEADERSHIP—Ineffective Supervision
14. SUPERVISION/LEADERSHIP—Ineffective Planning & Coordination
15. ORGANIZATIONAL INFLUENCES—Climate/Culture
16. ORGANIZATIONAL INFLUENCES—Policy/Procedures/Process
17. ORGANIZATIONAL INFLUENCES—Resource Support
18. ORGANIZATIONAL INFLUENCES—Training Program Issues

The 4 HFACS layers are:
1. UNSAFE ACTS
2. PRECONDITIONS
3. SUPERVISION/LEADERSHIP
4. ORGANIZATIONAL INFLUENCES

CLASSIFICATION CRITERIA:
• Category: Is the 18-category classification accurate based on strong textual evidence?
• Layer: Is the 4-layer classification accurate and consistent with the category?

CONFIDENCE SCORING:
• 0.9-1.0: Explicit evidence directly supports classification
• 0.7-0.8: Strong indirect evidence supports classification
• 0.5-0.6: Moderate evidence, some interpretation required
• 0.3-0.4: Weak evidence, significant uncertainty
• 0.1-0.2: Very weak evidence, highly speculative

REASONING GUIDELINES:
• Be concise (≤ 50 words per reasoning)
• Explicitly reference sentence content when possible
• Remain objective and consistent with HFACS definitions
• Provide specific evidence from the narrative text
• Default to conservative interpretation

QUALITY STANDARDS:
• Maintain objectivity and avoid speculation beyond the evidence
• Only classify factors with clear textual support
• Consider both active failures (unsafe acts) and latent conditions
• Prioritize accuracy over completeness
• Be thorough but conservative in your analysis

Analyze the incident narrative and identify ALL applicable HFACS categories and layers with high precision and strong evidence support."""
    
    def analyze_hfacs(self, incident_data: Dict, session_id: Optional[str] = None) -> HFACSAnalysisResult:
        """
        Perform HFACS analysis with optional memory support

        Args:
            incident_data: Incident data
            session_id: Optional conversation session ID for memory support

        Returns:
            HFACSAnalysisResult: HFACS analysis result
        """
        try:
            if self.use_mock:
                return self._mock_hfacs_analysis(incident_data)
            elif self.enhanced_analyzer:
                # Use memory-enabled analyzer
                enhanced_result = self.enhanced_analyzer.analyze_with_memory(
                    incident_data=incident_data,
                    session_id=session_id,
                    follow_up=False
                )
                return self._convert_enhanced_to_hfacs_result(enhanced_result, incident_data)
            else:
                return self._openai_hfacs_analysis(incident_data)
        except Exception as e:
            logger.error(f"HFACS analysis failed: {e}")
            return self._fallback_hfacs_analysis(incident_data)
    
    def ask_follow_up_question(self, session_id: str, question: str) -> Dict[str, Any]:
        """
        Ask follow-up question in existing HFACS conversation
        
        Args:
            session_id: Conversation session ID
            question: Follow-up question
            
        Returns:
            Dict containing the follow-up response and metadata
        """
        if not self.enhanced_analyzer:
            return {"error": "Memory not enabled", "response": None}
        
        try:
            enhanced_result = self.enhanced_analyzer.ask_follow_up(session_id, question)
            return {
                "response": enhanced_result.result,
                "cost": enhanced_result.cost,
                "token_usage": enhanced_result.token_usage,
                "confidence": enhanced_result.confidence,
                "session_id": enhanced_result.session_id
            }
        except Exception as e:
            logger.error(f"Follow-up question failed: {e}")
            return {"error": str(e), "response": None}
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get performance statistics for memory-enabled analyzer"""
        if not self.enhanced_analyzer:
            return {"error": "Memory not enabled"}
        
        return self.enhanced_analyzer.get_performance_stats()
    
    def evaluate_hfacs_classification(self, classifications: List[HFACSClassification], 
                                    evaluation_criteria: Dict = None) -> Dict[str, Any]:
        """
        Evaluate HFACS classification quality based on GT_Run_Auto evaluation standards
        
        Args:
            classifications: List of HFACS classifications to evaluate
            evaluation_criteria: Optional custom evaluation criteria
            
        Returns:
            Dict containing evaluation results and quality metrics
        """
        if not classifications:
            return {
                "total_classifications": 0,
                "quality_score": 0.0,
                "evaluation_summary": "No classifications to evaluate"
            }
        
        # Default evaluation criteria based on GT_Run_Auto standards
        default_criteria = {
            "high_confidence_threshold": 0.7,
            "medium_confidence_threshold": 0.4,
            "minimum_evidence_items": 1,
            "maximum_reasoning_length": 50
        }
        
        criteria = evaluation_criteria or default_criteria
        
        # Evaluate each classification
        evaluation_results = []
        total_quality_score = 0.0
        
        for cls in classifications:
            # Evaluate confidence appropriateness
            confidence_quality = self._evaluate_confidence_quality(cls)
            
            # Evaluate evidence strength
            evidence_quality = self._evaluate_evidence_quality(cls, criteria)
            
            # Evaluate reasoning quality
            reasoning_quality = self._evaluate_reasoning_quality(cls, criteria)
            
            # Evaluate category-layer consistency
            consistency_quality = self._evaluate_category_layer_consistency(cls)
            
            # Calculate overall quality for this classification
            classification_quality = (
                confidence_quality * 0.3 +
                evidence_quality * 0.3 +
                reasoning_quality * 0.2 +
                consistency_quality * 0.2
            )
            
            evaluation_results.append({
                "category": cls.category,
                "layer": cls.layer,
                "confidence": cls.confidence,
                "quality_score": classification_quality,
                "confidence_quality": confidence_quality,
                "evidence_quality": evidence_quality,
                "reasoning_quality": reasoning_quality,
                "consistency_quality": consistency_quality
            })
            
            total_quality_score += classification_quality
        
        # Calculate overall metrics
        avg_quality_score = total_quality_score / len(classifications)
        high_confidence_count = len([cls for cls in classifications if cls.confidence >= criteria["high_confidence_threshold"]])
        medium_confidence_count = len([cls for cls in classifications if criteria["medium_confidence_threshold"] <= cls.confidence < criteria["high_confidence_threshold"]])
        low_confidence_count = len([cls for cls in classifications if cls.confidence < criteria["medium_confidence_threshold"]])
        
        return {
            "total_classifications": len(classifications),
            "quality_score": avg_quality_score,
            "high_confidence_count": high_confidence_count,
            "medium_confidence_count": medium_confidence_count,
            "low_confidence_count": low_confidence_count,
            "layer_distribution": self._get_layer_distribution(classifications),
            "evaluation_results": evaluation_results,
            "evaluation_summary": self._generate_evaluation_summary(avg_quality_score, evaluation_results)
        }
    
    def _evaluate_confidence_quality(self, classification: HFACSClassification) -> float:
        """Evaluate confidence score appropriateness"""
        # Higher confidence should be supported by stronger evidence
        evidence_count = len(classification.evidence) if classification.evidence else 0
        reasoning_length = len(classification.reasoning)
        
        if classification.confidence >= 0.8:
            # High confidence requires strong evidence
            return 1.0 if evidence_count >= 2 and reasoning_length >= 20 else 0.6
        elif classification.confidence >= 0.5:
            # Medium confidence requires moderate evidence
            return 1.0 if evidence_count >= 1 and reasoning_length >= 15 else 0.8
        else:
            # Low confidence is generally acceptable for uncertain cases
            return 0.9
    
    def _evaluate_evidence_quality(self, classification: HFACSClassification, criteria: Dict) -> float:
        """Evaluate evidence strength and specificity"""
        if not classification.evidence:
            return 0.2
        
        evidence_count = len(classification.evidence)
        if evidence_count >= criteria["minimum_evidence_items"]:
            # Check for specific, non-generic evidence
            specific_evidence = [e for e in classification.evidence if len(e) > 10 and "mentioned" not in e.lower()]
            return min(1.0, len(specific_evidence) / evidence_count + 0.3)
        else:
            return 0.4
    
    def _evaluate_reasoning_quality(self, classification: HFACSClassification, criteria: Dict) -> float:
        """Evaluate reasoning quality and conciseness"""
        reasoning_length = len(classification.reasoning.split())
        
        if reasoning_length == 0:
            return 0.0
        elif reasoning_length <= criteria["maximum_reasoning_length"]:
            # Good length, check for narrative references
            has_specific_ref = any(word in classification.reasoning.lower() for word in ["narrative", "text", "states", "indicates", "shows"])
            return 1.0 if has_specific_ref else 0.8
        else:
            # Too verbose
            return 0.6
    
    def _evaluate_category_layer_consistency(self, classification: HFACSClassification) -> float:
        """Evaluate category-layer consistency"""
        expected_layer = CATEGORY_TO_LAYER.get(classification.category)
        if expected_layer == classification.layer:
            return 1.0
        else:
            logger.warning(f"Category-layer mismatch: {classification.category} should be in {expected_layer}, not {classification.layer}")
            return 0.0
    
    def _get_layer_distribution(self, classifications: List[HFACSClassification]) -> Dict[str, int]:
        """Get distribution of classifications across layers"""
        distribution = {layer: 0 for layer in HFACS_LAYERS}
        for cls in classifications:
            if cls.layer in distribution:
                distribution[cls.layer] += 1
        return distribution
    
    def _generate_evaluation_summary(self, avg_quality: float, evaluation_results: List[Dict]) -> str:
        """Generate evaluation summary based on quality metrics"""
        if avg_quality >= 0.8:
            quality_level = "High"
        elif avg_quality >= 0.6:
            quality_level = "Medium" 
        else:
            quality_level = "Low"
        
        high_quality_count = len([r for r in evaluation_results if r["quality_score"] >= 0.8])
        total_count = len(evaluation_results)
        
        return f"{quality_level} quality analysis. {high_quality_count}/{total_count} classifications meet high quality standards (≥0.8 quality score)."
    
    def _map_to_full_category_name(self, short_category: str, layer: str) -> str:
        """Map shortened category name to full HFACS category name"""
        # Handle different formats from LLM
        if not short_category:
            return ""
        
        # If it's already the full format, return as is
        if short_category in HFACS_CATEGORIES:
            return short_category
        
        # Try to find matching category by searching for the short name within full categories
        for full_category in HFACS_CATEGORIES:
            # Check if the short category is contained in the full category
            if short_category in full_category and full_category.startswith(layer):
                return full_category
        
        # If no exact match, try partial matching
        short_cleaned = short_category.replace("—", "").replace("Errors—", "").strip()
        for full_category in HFACS_CATEGORIES:
            if short_cleaned in full_category and full_category.startswith(layer):
                return full_category
        
        # If still no match, construct the full name
        if layer and short_category:
            # Handle common patterns
            if short_category.startswith("Errors—"):
                return f"{layer}—{short_category}"
            elif "—" not in short_category:
                return f"{layer}—{short_category}"
            else:
                return f"{layer}—{short_category}"
        
        # Fallback to original
        return short_category
    
    def _convert_enhanced_to_hfacs_result(self, enhanced_result: EnhancedAnalysisResult, 
                                        incident_data: Dict) -> HFACSAnalysisResult:
        """Convert EnhancedAnalysisResult to HFACSAnalysisResult format"""
        try:
            result_data = enhanced_result.result
            
            # Parse classifications
            classifications = []
            for cls in result_data.get("classifications", []):
                # Fix category name to match full HFACS format
                category = cls.get("category", "")
                layer = cls.get("layer", "")
                full_category = self._map_to_full_category_name(category, layer)
                
                classifications.append(HFACSClassification(
                    category=full_category,
                    layer=layer,
                    confidence=cls.get("confidence", 0.5),
                    reasoning=cls.get("reasoning", ""),
                    evidence=cls.get("evidence", "").split(". ") if cls.get("evidence") else []
                ))
            
            # Generate visualization data
            viz_data = self._generate_visualization_data(classifications)
            
            return HFACSAnalysisResult(
                classifications=classifications,
                primary_factors=[cls.category for cls in classifications if cls.confidence > 0.7],
                contributing_factors=[cls.category for cls in classifications if 0.4 <= cls.confidence <= 0.7],
                recommendations=[rec.get("recommendation", "") for rec in result_data.get("recommendations", [])],
                analysis_summary=result_data.get("summary", ""),
                confidence_score=enhanced_result.confidence,
                analysis_timestamp=enhanced_result.created_at.isoformat(),
                visualization_data=viz_data
            )
        except Exception as e:
            logger.error(f"Error converting enhanced result: {e}")
            return self._fallback_hfacs_analysis(incident_data)

    def _create_hfacs_function_schema(self):
        """Create enhanced HFACS analysis Function Schema based on GT_Run_Auto evaluation standards"""
        return {
            "name": "analyze_hfacs_factors",
            "description": "Analyze incident narrative using HFACS 8.0 framework with critical evaluation standards",
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
                                    "description": "HFACS category classification (one of 18 categories)"
                                },
                                "layer": {
                                    "type": "string",
                                    "enum": HFACS_LAYERS,
                                    "description": "HFACS layer classification (one of 4 layers)"
                                },
                                "confidence": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                    "description": "Confidence score: 0.9-1.0=explicit evidence, 0.7-0.8=strong indirect, 0.5-0.6=moderate, 0.3-0.4=weak, 0.1-0.2=very weak"
                                },
                                "reasoning": {
                                    "type": "string",
                                    "description": "Concise reasoning (≤50 words) with explicit reference to narrative content"
                                },
                                "evidence": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Specific evidence quotes from the narrative text"
                                }
                            },
                            "required": ["category", "layer", "confidence", "reasoning", "evidence"]
                        }
                    },
                    "primary_factors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Most critical human factors (high confidence classifications)"
                    },
                    "contributing_factors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Secondary contributing factors (moderate confidence classifications)"
                    },
                    "recommendations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "recommendation": {"type": "string"},
                                "target_layer": {"type": "string", "enum": HFACS_LAYERS},
                                "priority": {"type": "string", "enum": ["high", "medium", "low"]}
                            }
                        },
                        "description": "Specific recommendations targeting identified HFACS layers"
                    },
                    "analysis_summary": {
                        "type": "string",
                        "description": "Conservative analysis summary based only on strong evidence"
                    },
                    "confidence_score": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Overall confidence in the analysis based on evidence strength"
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

    def create_hfacs_visualizations(self, result: HFACSAnalysisResult, confidence_threshold: float = 0.0, 
                                   use_professional: bool = True) -> Dict:
        """
        Create HFACS visualization charts based on LLM analysis results
        
        Args:
            result: HFACS analysis result from LLM
            confidence_threshold: Minimum confidence for display (default: 0.0 shows all)
            use_professional: Compatibility parameter (ignored)
            
        Returns:
            Dictionary containing visualization figures
        """
        logger.info(f"Creating HFACS visualizations from LLM analysis results")
        
        # Filter classifications by confidence threshold if needed
        if confidence_threshold > 0.0 and hasattr(result, 'classifications') and result.classifications:
            filtered_classifications = [cls for cls in result.classifications if cls.confidence >= confidence_threshold]
            
            # Create filtered result object
            from dataclasses import replace
            filtered_result = replace(result, classifications=filtered_classifications)
            logger.info(f"Filtered {len(result.classifications)} classifications to {len(filtered_classifications)} above {confidence_threshold:.1%} confidence")
        else:
            filtered_result = result
        
        # Use the new visualization system
        try:
            visualizations = create_hfacs_visualizations(filtered_result)
            logger.info(f"Successfully created {len(visualizations)} HFACS visualizations")
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating HFACS visualizations: {e}")
            return self._create_fallback_visualizations(result)
    
    def _create_fallback_visualizations(self, result: HFACSAnalysisResult) -> Dict:
        """Create basic fallback visualizations"""
        try:
            return self._create_basic_visualizations(result)
        except Exception as e:
            logger.error(f"Fallback visualizations failed: {e}")
            return {}
    
    def _create_basic_visualizations(self, result: HFACSAnalysisResult) -> Dict:
        """Fallback basic visualizations if enhanced ones fail"""
        visualizations = {}
        
        # Basic layer distribution pie chart
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
            
        return visualizations
    
    def create_hfacs_pyramid_visualization(self, result: HFACSAnalysisResult, confidence_threshold: float = 0.0,
                                         use_professional: bool = True) -> go.Figure:
        """Create HFACS layer summary visualization"""
        
        logger.info("Creating HFACS layer summary visualization")
        
        # Filter by confidence threshold if needed
        if confidence_threshold > 0.0 and hasattr(result, 'classifications') and result.classifications:
            filtered_classifications = [cls for cls in result.classifications if cls.confidence >= confidence_threshold]
            from dataclasses import replace
            filtered_result = replace(result, classifications=filtered_classifications)
        else:
            filtered_result = result
        
        try:
            from .hfacs_visualization import HFACSVisualizer
            visualizer = HFACSVisualizer()
            return visualizer.create_layer_summary(filtered_result)
        except Exception as e:
            logger.error(f"Error creating pyramid visualization: {e}")
            return self._create_fallback_pyramid(result)
    
    def _create_fallback_pyramid(self, result: HFACSAnalysisResult) -> go.Figure:
        """Fallback basic pyramid if enhanced version fails"""
        fig = go.Figure()
        fig.add_annotation(
            x=0, y=0, 
            text="Pyramid visualization temporarily unavailable",
            showarrow=False,
            font=dict(size=16)
        )
        return fig


    def create_hfacs_tree_visualization(self, result: HFACSAnalysisResult, confidence_threshold: float = 0.0,
                                      use_professional: bool = True) -> go.Figure:
        """Create HFACS hierarchy tree visualization"""
        
        logger.info("Creating HFACS hierarchy tree visualization")
        
        # Filter by confidence threshold if needed
        if confidence_threshold > 0.0 and hasattr(result, 'classifications') and result.classifications:
            filtered_classifications = [cls for cls in result.classifications if cls.confidence >= confidence_threshold]
            from dataclasses import replace
            filtered_result = replace(result, classifications=filtered_classifications)
        else:
            filtered_result = result
        
        try:
            from .hfacs_visualization import HFACSVisualizer
            visualizer = HFACSVisualizer()
            return visualizer.create_hierarchy_tree(filtered_result)
        except Exception as e:
            logger.error(f"Error creating tree visualization: {e}")
            return self._create_fallback_tree(result)
    
    def _create_fallback_tree(self, result: HFACSAnalysisResult) -> go.Figure:
        """Fallback basic tree if enhanced version fails"""
        fig = go.Figure()
        fig.add_annotation(
            x=0, y=0,
            text="Tree visualization temporarily unavailable", 
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    def _create_fallback_pyramid(self, result: HFACSAnalysisResult) -> go.Figure:
        """Fallback basic pyramid if visualization fails"""
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text="HFACS layer summary temporarily unavailable",
            showarrow=False,
            font=dict(size=16),
            xref="paper", yref="paper"
        )
        fig.update_layout(title="HFACS Layer Summary")
        return fig
        
    def _create_fallback_tree(self, result: HFACSAnalysisResult) -> go.Figure:
        """Fallback basic tree if visualization fails"""
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text="HFACS hierarchy tree temporarily unavailable", 
            showarrow=False,
            font=dict(size=16),
            xref="paper", yref="paper"
        )
        fig.update_layout(title="HFACS Hierarchy Tree")
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
        if any(word in all_text for word in ['error', 'mistake', 'wrong', 'decision', 'decided', 'misjudged', 'failed to', 'judgment', 'judgement', 'lapse']):
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
        if any(word in all_text for word in ['violation', 'deviated', 'ignored', 'bypassed', 'shortcut', 'unauthorized', 'not authorized', 'should not have']):
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
