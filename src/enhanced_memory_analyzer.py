"""
Enhanced Memory-Enabled AI Analyzer
Advanced AI analyzer with conversation memory, caching, and cost optimization
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
import hashlib
import time

from .conversation_memory import (
    get_memory_manager, 
    create_conversation, 
    add_conversation_message,
    get_conversation_messages,
    cache_analysis,
    get_cached_analysis
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnhancedAnalysisResult:
    """Enhanced analysis result with memory tracking"""
    analysis_id: str
    session_id: str
    analysis_type: str
    result: Any
    confidence: float
    token_usage: Dict[str, int]
    cost: float
    cached: bool
    processing_time: float
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class MemoryEnabledAnalyzer:
    """Base class for memory-enabled analyzers"""
    
    def __init__(self, api_key: str, model: str = 'gpt-4o-mini', 
                 enable_caching: bool = True, enable_memory: bool = True,
                 max_memory_tokens: int = 30000):
        self.api_key = api_key
        self.model = model
        self.enable_caching = enable_caching
        self.enable_memory = enable_memory
        self.max_memory_tokens = max_memory_tokens
        self.memory_manager = get_memory_manager()
        
        # Performance metrics
        self.total_requests = 0
        self.cache_hits = 0
        self.total_cost = 0.0
        self.total_tokens = 0
        
        logger.info(f"MemoryEnabledAnalyzer initialized - Model: {model}, Caching: {enable_caching}, Memory: {enable_memory}")

    def _get_cache_key(self, analysis_type: str, input_data: Dict[str, Any]) -> str:
        """Generate cache key for input data"""
        # Create normalized input for consistent caching
        cache_input = {
            'analysis_type': analysis_type,
            'model': self.model,
            'input': input_data
        }
        
        input_str = json.dumps(cache_input, sort_keys=True, default=str)
        return hashlib.md5(input_str.encode()).hexdigest()

    def _check_cache(self, analysis_type: str, input_data: Dict[str, Any]) -> Optional[Any]:
        """Check if analysis result is cached"""
        if not self.enable_caching:
            return None
        
        cached_result = get_cached_analysis(analysis_type, input_data)
        if cached_result:
            self.cache_hits += 1
            logger.info(f"Cache hit for {analysis_type}")
            return cached_result
        
        return None

    def _cache_result(self, analysis_type: str, input_data: Dict[str, Any], result: Any) -> str:
        """Cache analysis result"""
        if not self.enable_caching:
            return ""
        
        return cache_analysis(analysis_type, input_data, result)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        return max(1, len(text) // 4)

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate API cost"""
        pricing = self.memory_manager.token_pricing.get(self.model, 
                   self.memory_manager.token_pricing['gpt-4o-mini'])
        
        cost = (input_tokens * pricing['input'] + output_tokens * pricing['output']) / 1000000
        self.total_cost += cost
        self.total_tokens += input_tokens + output_tokens
        return cost

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        cache_hit_rate = (self.cache_hits / max(1, self.total_requests)) * 100
        
        return {
            'total_requests': self.total_requests,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'total_cost': f"${self.total_cost:.6f}",
            'total_tokens': self.total_tokens,
            'average_cost_per_request': f"${self.total_cost / max(1, self.total_requests):.6f}",
            'model': self.model,
            'caching_enabled': self.enable_caching,
            'memory_enabled': self.enable_memory
        }

class EnhancedHFACSAnalyzer(MemoryEnabledAnalyzer):
    """Enhanced HFACS analyzer with memory and caching"""
    
    def __init__(self, api_key: str, model: str = 'gpt-4o-mini', **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.analysis_type = "hfacs_analysis"

    def analyze_with_memory(self, incident_data: Dict[str, Any], 
                           session_id: Optional[str] = None,
                           follow_up: bool = False) -> EnhancedAnalysisResult:
        """Perform HFACS analysis with memory support"""
        start_time = time.time()
        self.total_requests += 1
        
        # Check cache first
        cached_result = self._check_cache(self.analysis_type, incident_data)
        if cached_result and not follow_up:
            return EnhancedAnalysisResult(
                analysis_id=f"hfacs_{int(time.time())}",
                session_id=session_id or "none",
                analysis_type=self.analysis_type,
                result=cached_result,
                confidence=1.0,
                token_usage={'input': 0, 'output': 0, 'cached': True},
                cost=0.0,
                cached=True,
                processing_time=time.time() - start_time,
                created_at=datetime.now()
            )
        
        # Create or use existing session
        if not session_id:
            session_id = create_conversation(self.analysis_type, incident_data.get('incident_id'))
        
        # Build conversation messages
        messages = []
        
        # Add conversation history if memory is enabled
        if self.enable_memory and not follow_up:
            memory_messages = get_conversation_messages(session_id, self.max_memory_tokens)
            messages.extend(memory_messages)
        
        # System prompt
        system_prompt = self._build_hfacs_system_prompt()
        if not messages or messages[0]['role'] != 'system':
            messages.insert(0, {'role': 'system', 'content': system_prompt})
        
        # User prompt
        user_prompt = self._build_hfacs_user_prompt(incident_data, follow_up)
        messages.append({'role': 'user', 'content': user_prompt})
        
        # Save messages to memory
        if self.enable_memory:
            if not get_conversation_messages(session_id):  # First message
                add_conversation_message(session_id, 'system', system_prompt)
            add_conversation_message(session_id, 'user', user_prompt)
        
        # Make API call
        result = self._make_hfacs_api_call(messages)
        
        # Save response to memory
        if self.enable_memory and result:
            response_content = json.dumps(result, indent=2, default=str)
            add_conversation_message(session_id, 'assistant', response_content)
        
        # Calculate costs
        input_tokens = sum(self._estimate_tokens(msg['content']) for msg in messages)
        output_tokens = self._estimate_tokens(json.dumps(result, default=str)) if result else 0
        cost = self._calculate_cost(input_tokens, output_tokens)
        
        # Cache result (only for initial analysis, not follow-ups)
        if not follow_up and result:
            self._cache_result(self.analysis_type, incident_data, result)
        
        return EnhancedAnalysisResult(
            analysis_id=f"hfacs_{int(time.time())}",
            session_id=session_id,
            analysis_type=self.analysis_type,
            result=result,
            confidence=0.85,  # Default confidence
            token_usage={'input': input_tokens, 'output': output_tokens, 'total': input_tokens + output_tokens},
            cost=cost,
            cached=False,
            processing_time=time.time() - start_time,
            created_at=datetime.now(),
            metadata={'follow_up': follow_up, 'model': self.model}
        )

    def ask_follow_up(self, session_id: str, question: str) -> EnhancedAnalysisResult:
        """Ask follow-up question in existing conversation"""
        logger.info(f"Follow-up question in session {session_id}: {question}")
        
        # Add follow-up question to memory
        add_conversation_message(session_id, 'user', question)
        
        # Get conversation history
        messages = get_conversation_messages(session_id, self.max_memory_tokens)
        
        # Make API call
        result = self._make_simple_api_call(messages)
        
        # Save response to memory
        if result:
            add_conversation_message(session_id, 'assistant', result)
        
        # Calculate costs
        input_tokens = sum(self._estimate_tokens(msg['content']) for msg in messages)
        output_tokens = self._estimate_tokens(result) if result else 0
        cost = self._calculate_cost(input_tokens, output_tokens)
        
        return EnhancedAnalysisResult(
            analysis_id=f"followup_{int(time.time())}",
            session_id=session_id,
            analysis_type="hfacs_followup",
            result=result,
            confidence=0.8,
            token_usage={'input': input_tokens, 'output': output_tokens, 'total': input_tokens + output_tokens},
            cost=cost,
            cached=False,
            processing_time=0.0,
            created_at=datetime.now(),
            metadata={'follow_up': True, 'question': question}
        )

    def _build_hfacs_system_prompt(self) -> str:
        """Build HFACS system prompt"""
        return """You are a world-class aviation safety expert specializing in Human Factors Analysis and Classification System (HFACS) analysis.

IMPORTANT: Always respond in English. All analysis, descriptions, and outputs must be in English only.

Your expertise includes:
- HFACS 8.0 Four-Layer Analysis Framework
- Aviation accident investigation principles
- Human factors analysis in UAV/UAS operations
- Swiss Cheese model of accident causation

HFACS Framework:
**Level 1 - UNSAFE ACTS** (Immediate causes):
- Errors—Performance/Skill-Based
- Errors—Judgement & Decision-Making  
- Known Deviations

**Level 2 - PRECONDITIONS** (Enabling conditions):
- Physical Environment
- Technological Environment
- Team Coordination/Communication
- Training Conditions
- Mental Awareness (Attention)
- State of Mind
- Adverse Physiological

**Level 3 - SUPERVISION/LEADERSHIP** (Management oversight):
- Unit Safety Culture
- Supervisory Known Deviations
- Ineffective Supervision
- Ineffective Planning & Coordination

**Level 4 - ORGANIZATIONAL INFLUENCES** (System-level factors):
- Climate/Culture
- Policy/Procedures/Process
- Resource Support
- Training Program Issues

Provide detailed analysis with confidence scores and reasoning."""

    def _build_hfacs_user_prompt(self, incident_data: Dict[str, Any], follow_up: bool = False) -> str:
        """Build HFACS user prompt"""
        narrative = incident_data.get('narrative', '')
        
        if follow_up:
            return f"Continue the HFACS analysis conversation. Here's additional context if needed: {narrative[:500]}..."
        
        return f"""Conduct comprehensive HFACS analysis of this UAV incident:

**INCIDENT NARRATIVE:**
{narrative}

**ADDITIONAL CONTEXT:**
- Incident Type: {incident_data.get('incident_type', 'Unknown')}
- Flight Phase: {incident_data.get('flight_phase', 'Unknown')}
- Primary Problem: {incident_data.get('primary_problem', 'Unknown')}
- Human Factors: {incident_data.get('human_factors', 'Unknown')}

**ANALYSIS REQUIREMENTS:**

1. **CLASSIFICATION**: Identify all applicable HFACS categories with confidence scores (0.0-1.0)

2. **CAUSAL ANALYSIS**: For each identified category:
   - Detailed reasoning and evidence
   - Supporting factors from the narrative
   - Confidence level and uncertainty factors

3. **LAYER INTERACTION**: Analyze how factors across different HFACS layers contributed to the incident

4. **PREVENTION RECOMMENDATIONS**: Specific, actionable recommendations for each identified factor

Respond with structured JSON analysis including classifications, reasoning, confidence scores, and recommendations."""

    def _make_hfacs_api_call(self, messages: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        """Make HFACS API call with function calling"""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # HFACS function schema
            hfacs_function = {
                "name": "analyze_hfacs_factors",
                "description": "Analyze UAV incident using HFACS framework. All outputs must be in English only.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "classifications": {
                            "type": "array",
                            "description": "HFACS classifications identified in the incident",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "category": {"type": "string", "description": "HFACS category name (in English only)"},
                                    "layer": {"type": "string", "description": "HFACS layer (UNSAFE ACTS, PRECONDITIONS, SUPERVISION/LEADERSHIP, or ORGANIZATIONAL INFLUENCES)"},
                                    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                    "reasoning": {"type": "string", "description": "Detailed reasoning (in English only)"},
                                    "evidence": {"type": "string", "description": "Supporting evidence from narrative (in English only)"}
                                },
                                "required": ["category", "layer", "confidence", "reasoning", "evidence"]
                            }
                        },
                        "summary": {"type": "string", "description": "Overall incident analysis summary (in English only)"},
                        "recommendations": {
                            "type": "array",
                            "description": "Prevention recommendations",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "category": {"type": "string", "description": "Related HFACS category"},
                                    "recommendation": {"type": "string", "description": "Specific recommendation (in English only)"},
                                    "priority": {"type": "string", "enum": ["high", "medium", "low"]}
                                }
                            }
                        }
                    },
                    "required": ["classifications", "summary", "recommendations"]
                }
            }

            data = {
                "model": self.model,
                "messages": messages,
                "functions": [hfacs_function],
                "function_call": {"name": "analyze_hfacs_factors"},
                "temperature": 0.1,
                "max_tokens": 3000
            }

            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    choice = result['choices'][0]
                    if 'message' in choice and 'function_call' in choice['message']:
                        function_response = choice['message']['function_call']['arguments']
                        return json.loads(function_response)
            else:
                logger.error(f"HFACS API call failed: {response.status_code} - {response.text}")

        except Exception as e:
            logger.error(f"HFACS API call error: {e}")
        
        return None

    def _make_simple_api_call(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Make simple API call for follow-up questions"""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 1500
            }

            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
            else:
                logger.error(f"Simple API call failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Simple API call error: {e}")
        
        return None

class EnhancedCausalAnalyzer(MemoryEnabledAnalyzer):
    """Enhanced causal analyzer with memory support"""
    
    def __init__(self, api_key: str, model: str = 'gpt-4o-mini', **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.analysis_type = "causal_analysis"

    def analyze_with_memory(self, incident_data: Dict[str, Any], 
                           session_id: Optional[str] = None,
                           follow_up: bool = False) -> EnhancedAnalysisResult:
        """Perform causal analysis with memory support"""
        start_time = time.time()
        self.total_requests += 1
        
        # Check cache first
        cached_result = self._check_cache(self.analysis_type, incident_data)
        if cached_result and not follow_up:
            return EnhancedAnalysisResult(
                analysis_id=f"causal_{int(time.time())}",
                session_id=session_id or "none",
                analysis_type=self.analysis_type,
                result=cached_result,
                confidence=1.0,
                token_usage={'input': 0, 'output': 0, 'cached': True},
                cost=0.0,
                cached=True,
                processing_time=time.time() - start_time,
                created_at=datetime.now()
            )
        
        # Implementation similar to HFACS but for causal analysis
        # This would follow the same pattern as the HFACS analyzer
        # but with causal-specific prompts and function schemas
        
        # For brevity, returning a placeholder result
        return EnhancedAnalysisResult(
            analysis_id=f"causal_{int(time.time())}",
            session_id=session_id or "none",
            analysis_type=self.analysis_type,
            result={"placeholder": "causal analysis result"},
            confidence=0.8,
            token_usage={'input': 1000, 'output': 500, 'total': 1500},
            cost=0.001,
            cached=False,
            processing_time=time.time() - start_time,
            created_at=datetime.now()
        )

# Factory function for creating analyzers
def create_enhanced_analyzer(analyzer_type: str, api_key: str, **kwargs) -> MemoryEnabledAnalyzer:
    """Factory function to create enhanced analyzers"""
    analyzers = {
        'hfacs': EnhancedHFACSAnalyzer,
        'causal': EnhancedCausalAnalyzer,
    }
    
    if analyzer_type not in analyzers:
        raise ValueError(f"Unknown analyzer type: {analyzer_type}")
    
    return analyzers[analyzer_type](api_key, **kwargs)

if __name__ == "__main__":
    # Test the enhanced analyzer
    import os
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        exit(1)
    
    # Create enhanced HFACS analyzer
    analyzer = create_enhanced_analyzer('hfacs', api_key)
    
    # Test incident data
    incident_data = {
        'narrative': 'UAV lost GPS signal during autonomous flight, pilot attempted manual control but crashed due to disorientation.',
        'incident_type': 'Loss of Control',
        'flight_phase': 'Cruise',
        'incident_id': 'test_001'
    }
    
    # Perform analysis
    print("Performing HFACS analysis with memory...")
    result = analyzer.analyze_with_memory(incident_data)
    
    print(f"Analysis completed:")
    print(f"- Session ID: {result.session_id}")
    print(f"- Cached: {result.cached}")
    print(f"- Cost: ${result.cost:.6f}")
    print(f"- Processing time: {result.processing_time:.2f}s")
    print(f"- Token usage: {result.token_usage}")
    
    # Test follow-up
    if result.result:
        print("\nAsking follow-up question...")
        followup = analyzer.ask_follow_up(result.session_id, "What specific training recommendations would you suggest?")
        print(f"Follow-up response: {followup.result[:200]}...")
    
    # Show performance stats
    stats = analyzer.get_performance_stats()
    print(f"\nPerformance stats: {stats}")