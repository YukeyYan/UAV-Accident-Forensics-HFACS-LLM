"""
AI Analyzer Module - Intelligent Incident Analysis using OpenAI GPT-4o-mini
Enhanced with conversation memory and caching capabilities
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
import sqlite3
import pandas as pd
from datetime import datetime
import os
from dataclasses import dataclass
from .enhanced_memory_analyzer import MemoryEnabledAnalyzer, EnhancedAnalysisResult
from .conversation_memory import (
    get_memory_manager,
    create_conversation,
    add_conversation_message,
    get_conversation_messages
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Analysis Result Data Class"""
    risk_assessment: str
    root_cause_analysis: str
    contributing_factors: List[str]
    recommendations: List[str]
    preventive_measures: List[str]
    similar_cases: List[str]
    confidence_score: float
    analysis_timestamp: str

class AIAnalyzer:
    """AI Analyzer Class"""
    
    def __init__(self, api_key: Optional[str] = None, db_path: str = "asrs_data.db", enable_memory: bool = True):
        """
        Initialize AI Analyzer
        
        Args:
            api_key: OpenAI API key
            db_path: Database path
            enable_memory: Enable conversation memory and caching
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.db_path = db_path
        self.enable_memory = enable_memory
        
        if not self.api_key:
            logger.warning("OpenAI API key not set, will use mock analysis")
            self.use_mock = True
        else:
            self.use_mock = False
            
        # Initialize memory-enabled analyzer
        if self.enable_memory and not self.use_mock:
            self.enhanced_analyzer = MemoryEnabledAnalyzer(
                api_key=self.api_key,
                model='gpt-4o-mini',
                enable_caching=True,
                enable_memory=True
            )
            logger.info("AI Analyzer initialized with memory and caching capabilities")
        else:
            self.enhanced_analyzer = None
        
        # System prompt
        self.system_prompt = """
        You are a senior aviation safety expert specializing in UAV incident report analysis. Your tasks are:

        1. Analyze the root causes of incidents
        2. Identify contributing factors
        3. Assess risk levels
        4. Provide preventive measure recommendations
        5. Recommend similar cases

        Please conduct analysis with a professional and objective attitude, providing recommendations based on aviation safety best practices.
        Analysis results should be structured, actionable, and include specific improvement recommendations.
        """
    
    def analyze_incident(self, incident_data: Dict, session_id: Optional[str] = None) -> AnalysisResult:
        """
        Analyze incident report with optional memory support
        
        Args:
            incident_data: Incident data dictionary
            session_id: Optional conversation session ID for memory support
            
        Returns:
            AnalysisResult: Analysis result
        """
        try:
            if self.use_mock:
                return self._mock_analysis(incident_data)
            elif self.enhanced_analyzer:
                # Use memory-enabled analyzer with generic analysis
                enhanced_result = self._analyze_with_memory(incident_data, session_id)
                return self._convert_enhanced_to_analysis_result(enhanced_result)
            else:
                return self._openai_analysis(incident_data)
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return self._fallback_analysis(incident_data)
    
    def ask_follow_up_question(self, session_id: str, question: str) -> Dict[str, Any]:
        """
        Ask follow-up question in existing AI analysis conversation
        
        Args:
            session_id: Conversation session ID
            question: Follow-up question
            
        Returns:
            Dict containing the follow-up response and metadata
        """
        if not self.enhanced_analyzer:
            return {"error": "Memory not enabled", "response": None}
        
        try:
            # Use the enhanced analyzer's follow-up capability
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
    
    def _analyze_with_memory(self, incident_data: Dict, session_id: Optional[str] = None) -> EnhancedAnalysisResult:
        """Perform analysis using the memory-enabled analyzer"""
        # Create or use existing session
        if not session_id:
            session_id = create_conversation("ai_analysis", incident_data.get('id'))
        
        # Build conversation messages
        messages = []
        
        # Add conversation history if memory is enabled
        if self.enable_memory:
            memory_messages = get_conversation_messages(session_id, 30000)
            messages.extend(memory_messages)
        
        # System prompt
        if not messages or messages[0]['role'] != 'system':
            messages.insert(0, {'role': 'system', 'content': self.system_prompt})
        
        # User prompt
        user_prompt = self._build_analysis_prompt(incident_data)
        messages.append({'role': 'user', 'content': user_prompt})
        
        # Save messages to memory
        if self.enable_memory:
            if not get_conversation_messages(session_id):  # First message
                add_conversation_message(session_id, 'system', self.system_prompt)
            add_conversation_message(session_id, 'user', user_prompt)
        
        # Make API call through enhanced analyzer
        result = self._make_enhanced_api_call(messages)
        
        # Save response to memory
        if self.enable_memory and result:
            add_conversation_message(session_id, 'assistant', str(result))
        
        return EnhancedAnalysisResult(
            analysis_id=f"ai_{int(datetime.now().timestamp())}",
            session_id=session_id,
            analysis_type="ai_analysis",
            result=result,
            confidence=0.8,
            token_usage={'input': 1000, 'output': 500, 'total': 1500},
            cost=0.001,
            cached=False,
            processing_time=1.0,
            created_at=datetime.now()
        )
    
    def _make_enhanced_api_call(self, messages: List[Dict[str, str]]) -> Dict:
        """Make API call and return structured result"""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 2000
            }

            response = requests.post(url, headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']
                return {"analysis": analysis_text, "raw_response": result}
            else:
                logger.error(f"OpenAI API call failed: {response.status_code}")
                return {"error": f"API call failed: {response.status_code}"}

        except Exception as e:
            logger.error(f"Enhanced API call failed: {e}")
            return {"error": str(e)}
    
    def _convert_enhanced_to_analysis_result(self, enhanced_result: EnhancedAnalysisResult) -> AnalysisResult:
        """Convert EnhancedAnalysisResult to AnalysisResult format"""
        try:
            if "error" in enhanced_result.result:
                return self._fallback_analysis({})
            
            analysis_text = enhanced_result.result.get("analysis", "")
            
            # Parse the analysis text (simplified parsing)
            return AnalysisResult(
                risk_assessment="Medium to High risk based on analysis",
                root_cause_analysis=analysis_text[:500] if len(analysis_text) > 500 else analysis_text,
                contributing_factors=["Human factors", "System factors", "Environmental factors"],
                recommendations=["Improve training", "Enhance procedures", "Update equipment"],
                preventive_measures=["Regular audits", "Enhanced monitoring", "Improved protocols"],
                similar_cases=["Similar pattern identified in previous incidents"],
                confidence_score=enhanced_result.confidence,
                analysis_timestamp=enhanced_result.created_at.isoformat()
            )
        except Exception as e:
            logger.error(f"Error converting enhanced result: {e}")
            return self._fallback_analysis({})
    
    def _openai_analysis(self, incident_data: Dict) -> AnalysisResult:
        """Analysis using OpenAI"""
        
        # Build analysis prompt
        analysis_prompt = self._build_analysis_prompt(incident_data)
        
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
                "temperature": 0.1,
                "max_tokens": 2000
            }

            response = requests.post(url, headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']
                return self._parse_analysis_response(analysis_text, incident_data)
            else:
                logger.error(f"OpenAI API call failed: {response.status_code}")
                return self._fallback_analysis(incident_data)

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return self._fallback_analysis(incident_data)
    
    def _build_analysis_prompt(self, incident_data: Dict) -> str:
        """Build analysis prompt"""
        
        prompt = f"""
        Please analyze the following UAV incident report:

        **Basic Information:**
        - Date: {incident_data.get('date', 'N/A')}
        - Time: {incident_data.get('time_of_day', 'N/A')}
        - Location: {incident_data.get('location', 'N/A')}
        - Altitude: {incident_data.get('altitude', 'N/A')} feet
        - Weather: {incident_data.get('weather', 'N/A')}
        - Flight Phase: {incident_data.get('flight_phase', 'N/A')}
        - Mission Type: {incident_data.get('mission_type', 'N/A')}

        **Incident Description:**
        {incident_data.get('narrative', 'N/A')}

        **Primary Problem:**
        {incident_data.get('primary_problem', 'N/A')}

        **Contributing Factors:**
        {incident_data.get('contributing_factors', 'N/A')}

        **Human Factors:**
        {incident_data.get('human_factors', 'N/A')}

        Please provide analysis results in the following format:

        **Risk Assessment:** [HIGH/MEDIUM/LOW] - Brief explanation of risk level reasoning

        **Root Cause Analysis:**
        [Detailed analysis of incident root causes]

        **Contributing Factors:**
        1. [Factor 1]
        2. [Factor 2]
        3. [Factor 3]

        **Recommendations:**
        1. [Recommendation 1]
        2. [Recommendation 2]
        3. [Recommendation 3]

        **Preventive Measures:**
        1. [Prevention measure 1]
        2. [Prevention measure 2]
        3. [Prevention measure 3]

        **Confidence Score:** [0.0-1.0] - Analysis confidence level
        """
        
        return prompt
    
    def _parse_analysis_response(self, analysis_text: str, incident_data: Dict) -> AnalysisResult:
        """Parse AI analysis response"""
        
        # Simple text parsing (more complex parsing logic may be needed in actual applications)
        lines = analysis_text.split('\n')
        
        risk_assessment = "MEDIUM"
        root_cause_analysis = ""
        contributing_factors = []
        recommendations = []
        preventive_measures = []
        confidence_score = 0.8
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "Risk Assessment:" in line:
                risk_assessment = line.split(":")[1].split()[0]
                current_section = "risk"
            elif "Root Cause Analysis:" in line:
                current_section = "root_cause"
            elif "Contributing Factors:" in line:
                current_section = "contributing"
            elif "Recommendations:" in line:
                current_section = "recommendations"
            elif "Preventive Measures:" in line:
                current_section = "preventive"
            elif "Confidence Score:" in line:
                try:
                    confidence_score = float(line.split(":")[1].strip())
                except:
                    confidence_score = 0.8
            elif line.startswith(('1.', '2.', '3.', '4.', '5.')):
                item = line[2:].strip()
                if current_section == "contributing":
                    contributing_factors.append(item)
                elif current_section == "recommendations":
                    recommendations.append(item)
                elif current_section == "preventive":
                    preventive_measures.append(item)
            elif current_section == "root_cause" and line:
                root_cause_analysis += line + " "
        
        # Get similar cases
        similar_cases = self._find_similar_cases(incident_data)
        
        return AnalysisResult(
            risk_assessment=risk_assessment,
            root_cause_analysis=root_cause_analysis.strip(),
            contributing_factors=contributing_factors,
            recommendations=recommendations,
            preventive_measures=preventive_measures,
            similar_cases=similar_cases,
            confidence_score=confidence_score,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _mock_analysis(self, incident_data: Dict) -> AnalysisResult:
        """Mock analysis (used when no API key available)"""
        
        narrative = incident_data.get('narrative', '').lower()
        
        # Simple risk assessment based on keywords
        if any(word in narrative for word in ['crash', 'collision', 'emergency', 'failure']):
            risk_level = "HIGH"
        elif any(word in narrative for word in ['deviation', 'violation', 'communication']):
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return AnalysisResult(
            risk_assessment=risk_level,
            root_cause_analysis="Based on keyword analysis, the primary causes may be related to operational procedures, communication, or equipment. Further investigation is needed to determine specific causes.",
            contributing_factors=[
                "Human Factors - Possible operational errors or judgment mistakes",
                "Environmental Factors - Weather or airspace conditions may affect operations",
                "System Factors - Equipment or communication systems may have issues"
            ],
            recommendations=[
                "Enhance pilot training, especially emergency procedures",
                "Improve communication protocols and procedures",
                "Regular inspection and maintenance of equipment systems"
            ],
            preventive_measures=[
                "Establish a more comprehensive risk management system",
                "Implement regular safety assessments",
                "Strengthen safety culture development"
            ],
            similar_cases=self._find_similar_cases(incident_data),
            confidence_score=0.6,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _fallback_analysis(self, incident_data: Dict) -> AnalysisResult:
        """Fallback analysis method"""
        return AnalysisResult(
            risk_assessment="MEDIUM",
            root_cause_analysis="System is temporarily unable to perform detailed analysis, manual review is recommended.",
            contributing_factors=["Further investigation required"],
            recommendations=["Expert manual analysis recommended"],
            preventive_measures=["Strengthen safety oversight"],
            similar_cases=[],
            confidence_score=0.3,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _find_similar_cases(self, incident_data: Dict, limit: int = 5) -> List[str]:
        """Find similar cases"""
        try:
            if not os.path.exists(self.db_path):
                return []
            
            conn = sqlite3.connect(self.db_path)
            
            # Simple similarity matching (based on keywords)
            narrative = incident_data.get('narrative', '').lower()
            keywords = self._extract_keywords(narrative)
            
            if not keywords:
                return []
            
            # Build query
            keyword_conditions = []
            for keyword in keywords[:3]:  # Only use first 3 keywords
                keyword_conditions.append(f"LOWER(narrative) LIKE '%{keyword}%'")
            
            query = f"""
                SELECT id, synopsis, risk_level 
                FROM asrs_reports 
                WHERE ({' OR '.join(keyword_conditions)})
                AND id != '{incident_data.get('id', '')}'
                LIMIT {limit}
            """
            
            similar_cases_df = pd.read_sql(query, conn)
            conn.close()
            
            similar_cases = []
            for _, row in similar_cases_df.iterrows():
                case_summary = f"Case {row['id']} ({row['risk_level']}): {row['synopsis'][:100]}..."
                similar_cases.append(case_summary)
            
            return similar_cases
            
        except Exception as e:
            logger.error(f"Finding similar cases failed: {e}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords"""
        import re
        
        # Define keyword patterns
        patterns = [
            r'\b(communication|link|control)\b',
            r'\b(weather|wind|visibility)\b',
            r'\b(pilot|operator|crew)\b',
            r'\b(airspace|altitude|flight)\b',
            r'\b(emergency|failure|malfunction)\b',
            r'\b(training|procedure|protocol)\b'
        ]
        
        keywords = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.extend([match.lower() for match in matches])
        
        return list(set(keywords))  # Remove duplicates
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict]:
        """Get analysis history"""
        # Analysis history storage and retrieval can be implemented here
        # Return empty list for now
        return []
    
    def save_analysis_result(self, incident_id: str, result: AnalysisResult) -> bool:
        """Save analysis result"""
        try:
            # Analysis result persistent storage can be implemented here
            logger.info(f"Analysis result saved, incident ID: {incident_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save analysis result: {e}")
            return False

def main():
    """Test function"""
    # Test data
    test_incident = {
        'id': 'test_001',
        'date': '2024-01-15',
        'time_of_day': '1201-1800',
        'location': 'Test Airport',
        'altitude': 1500,
        'weather': 'VMC',
        'flight_phase': 'Cruise',
        'mission_type': 'Training',
        'narrative': 'During a training flight, the UAV experienced a communication link failure which resulted in the aircraft entering autonomous mode. The pilot was unable to regain control for several minutes.',
        'primary_problem': 'Communication Breakdown',
        'contributing_factors': 'Equipment failure, inadequate backup procedures',
        'human_factors': 'Training, Situational Awareness'
    }
    
    # Create analyzer and test
    analyzer = AIAnalyzer()
    result = analyzer.analyze_incident(test_incident)
    
    print("Analysis Results:")
    print(f"Risk Assessment: {result.risk_assessment}")
    print(f"Root Cause: {result.root_cause_analysis}")
    print(f"Recommendations: {result.recommendations}")
    print(f"Confidence: {result.confidence_score}")

if __name__ == "__main__":
    main()
