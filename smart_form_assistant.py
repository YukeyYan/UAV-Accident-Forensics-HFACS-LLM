"""
智能表单填写助手
基于用户叙述自动填写表单字段，并分析数据完整性
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import os
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FormField:
    """表单字段定义"""
    name: str
    field_type: str  # 'select', 'text', 'number', 'date'
    options: List[str] = None
    required: bool = False
    description: str = ""

@dataclass
class SmartFormResult:
    """智能表单填写结果"""
    extracted_fields: Dict[str, str]
    confidence_scores: Dict[str, float]
    missing_fields: List[str]
    completeness_score: float
    suggested_questions: List[str]
    synopsis: str
    analysis_timestamp: str

class SmartFormAssistant:
    """智能表单填写助手"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        初始化智能表单助手
        
        Args:
            api_key: OpenAI API密钥
            model: 使用的模型 (gpt-4o 或 gpt-4o-mini)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        
        if not self.api_key:
            logger.warning("未设置OpenAI API密钥，将使用模拟分析")
            self.use_mock = True
        else:
            self.use_mock = False
        
        # 定义表单字段（基于NASA ASRS UAS数据结构）
        self.form_fields = {
            # === ASRS基本识别信息 ===
            'report_date': FormField('report_date', 'date', required=True, description='报告日期'),
            'occurrence_date': FormField('occurrence_date', 'date', required=True, description='事件发生日期'),
            'time_of_day': FormField('time_of_day', 'select', 
                ['0001-0600', '0601-1200', '1201-1800', '1801-2400'], 
                required=True, description='事件发生时间段'),
            'local_time': FormField('local_time', 'text', description='当地时间（HHMM格式）'),
            
            # === 地理和环境信息 ===
            'location_city': FormField('location_city', 'text', required=True, description='事件发生城市'),
            'location_state': FormField('location_state', 'text', description='州/省份'),
            'location_country': FormField('location_country', 'text', description='国家'),
            'airport_identifier': FormField('airport_identifier', 'text', description='机场标识符'),
            'location_description': FormField('location_description', 'text', description='详细位置描述'),
            'altitude_agl': FormField('altitude_agl', 'number', description='高度AGL (英尺)'),
            'altitude_msl': FormField('altitude_msl', 'number', description='高度MSL (英尺)'),
            
            # === 气象和环境条件 ===
            'flight_conditions': FormField('flight_conditions', 'select', 
                ['VMC', 'IMC', 'Mixed'], required=True, description='飞行条件'),
            'weather_conditions': FormField('weather_conditions', 'text', description='详细天气状况'),
            'wind_speed': FormField('wind_speed', 'number', description='风速（节）'),
            'wind_direction': FormField('wind_direction', 'number', description='风向（度）'),
            'visibility': FormField('visibility', 'number', description='能见度（statute miles）'),
            'ceiling': FormField('ceiling', 'number', description='云底高度（英尺）'),
            'temperature': FormField('temperature', 'number', description='温度（摄氏度）'),
            'light_conditions': FormField('light_conditions', 'select', 
                ['Daylight', 'Dusk', 'Night', 'Dawn'], required=True, description='光照条件'),
            
            # === 无人机系统信息 ===
            'aircraft_make': FormField('aircraft_make', 'text', description='无人机制造商'),
            'aircraft_model': FormField('aircraft_model', 'text', description='无人机型号'),
            'aircraft_series': FormField('aircraft_series', 'text', description='系列/版本'),
            'aircraft_weight': FormField('aircraft_weight', 'number', description='起飞重量（磅）'),
            'aircraft_registration': FormField('aircraft_registration', 'text', description='注册号'),
            'propulsion_type': FormField('propulsion_type', 'select', 
                ['Electric', 'Gas', 'Turbine', 'Hybrid'], description='推进系统类型'),
            'control_method': FormField('control_method', 'select',
                ['Manual', 'Semi-Autonomous', 'Autonomous', 'Beyond Visual Line of Sight'], 
                description='控制方式'),
            
            # === 运营信息 ===
            'aircraft_operator_type': FormField('aircraft_operator_type', 'select',
                ['Government', 'Military', 'Commercial', 'Personal', 'Educational', 'Research'], 
                required=True, description='操作者类型'),
            'flight_phase': FormField('flight_phase', 'select',
                ['Pre-flight', 'Takeoff', 'Initial Climb', 'Climb', 'Cruise', 'Descent', 
                 'Approach', 'Landing', 'Post-landing', 'Hover', 'Taxi'], 
                required=True, description='飞行阶段'),
            'mission_type': FormField('mission_type', 'select',
                ['Training', 'Proficiency', 'Test Flight', 'Commercial Photography', 
                 'Surveillance', 'Search and Rescue', 'Agricultural', 'Delivery', 
                 'Research', 'Recreation', 'Other'], description='任务类型'),
            'operation_type': FormField('operation_type', 'select',
                ['Visual Line of Sight (VLOS)', 'Beyond Visual Line of Sight (BVLOS)', 
                 'Extended Visual Line of Sight (EVLOS)'], description='运行类型'),
            
            # === 空域和管制信息 ===
            'airspace_class': FormField('airspace_class', 'select',
                ['Class A', 'Class B', 'Class C', 'Class D', 'Class E', 'Class G', 
                 'Prohibited', 'Restricted', 'Warning', 'Special Use'], description='空域类别'),
            'airspace_authorization': FormField('airspace_authorization', 'select',
                ['Part 107 Waiver', 'LAANC Authorization', 'ATC Clearance', 
                 'COA (Certificate of Authorization)', 'None Required', 'Other'], 
                description='空域授权'),
            'atc_contact': FormField('atc_contact', 'select',
                ['Yes', 'No', 'Not Applicable'], description='是否联系ATC'),
            
            # === 操作员信息 ===
            'pilot_function': FormField('pilot_function', 'select',
                ['Remote Pilot in Command (RPIC)', 'Visual Observer', 'Person Manipulating Controls', 
                 'Ground Support', 'Other'], description='操作员职能'),
            'pilot_qualification': FormField('pilot_qualification', 'select',
                ['Part 107 Remote Pilot Certificate', 'Part 61 Pilot Certificate', 
                 'Military UAV Training', 'Manufacturer Training', 'Other', 'None'], 
                required=True, description='操作员资质'),
            'pilot_experience_total': FormField('pilot_experience_total', 'number', description='总飞行时间（小时）'),
            'pilot_experience_type': FormField('pilot_experience_type', 'number', description='本机型经验（小时）'),
            'pilot_experience_recent': FormField('pilot_experience_recent', 'number', description='近30天飞行时间（小时）'),
            
            # === 事件分析字段 ===
            'incident_type': FormField('incident_type', 'select',
                ['Near Mid-Air Collision (NMAC)', 'Airspace Violation', 'Loss of Control', 
                 'System Malfunction', 'Communication Failure', 'Weather Related', 
                 'Runway Incursion', 'Ground Collision', 'Emergency Landing', 'Other'], 
                required=True, description='事件类型'),
            'anomaly_description': FormField('anomaly_description', 'text', description='异常情况详述'),
            'detector': FormField('detector', 'select',
                ['Remote Pilot', 'Visual Observer', 'ATC', 'Other Aircraft', 
                 'Ground Personnel', 'System Alert', 'Other'], description='事件发现者'),
            'incident_result': FormField('incident_result', 'text', description='事件结果'),
            'damage_assessment': FormField('damage_assessment', 'select',
                ['None', 'Minor', 'Major', 'Substantial', 'Total Loss'], description='损害评估'),
            'injury_assessment': FormField('injury_assessment', 'select',
                ['None', 'Minor', 'Serious', 'Fatal'], description='人员伤害'),
            
            # === 根本原因和因素 ===
            'primary_problem': FormField('primary_problem', 'text', description='主要问题识别'),
            'contributing_factors': FormField('contributing_factors', 'text', description='贡献因素分析'),
            'human_factors': FormField('human_factors', 'text', description='人为因素'),
            'environmental_factors': FormField('environmental_factors', 'text', description='环境因素'),
            'equipment_factors': FormField('equipment_factors', 'text', description='设备因素'),
            'procedural_factors': FormField('procedural_factors', 'text', description='程序因素'),
            
            # === 安全和改进 ===
            'immediate_actions': FormField('immediate_actions', 'text', description='立即采取的行动'),
            'lessons_learned': FormField('lessons_learned', 'text', description='经验教训'),
            'safety_recommendations': FormField('safety_recommendations', 'text', description='安全建议'),
            'preventive_measures': FormField('preventive_measures', 'text', description='预防措施'),
            
            # === 法规和合规 ===
            'regulation_reference': FormField('regulation_reference', 'text', description='相关法规引用'),
            'waiver_deviation': FormField('waiver_deviation', 'text', description='豁免或偏差情况'),
            'compliance_assessment': FormField('compliance_assessment', 'text', description='合规性评估'),
            
            # === 叙述和额外信息 ===
            'synopsis': FormField('synopsis', 'text', required=True, description='事件概要'),
            'detailed_narrative': FormField('detailed_narrative', 'text', required=True, description='详细叙述'),
            'additional_info': FormField('additional_info', 'text', description='额外信息'),
            'attachments': FormField('attachments', 'text', description='附件说明')
        }
        
        # 增强的ASRS专业系统提示词
        self.system_prompt = """You are a world-class aviation safety expert and NASA ASRS (Aviation Safety Reporting System) analyst specializing in comprehensive UAV/UAS incident analysis.

🎯 MISSION & EXPERTISE:
Your role is to analyze UAV incidents with the same rigor and professionalism as NASA ASRS analysts, providing comprehensive safety intelligence for the aviation community.

CORE COMPETENCIES:
• NASA ASRS database structure and UAS reporting requirements
• FAA Part 107 regulations and waiver procedures
• LAANC authorization protocols and airspace management
• ICAO standards for unmanned aircraft systems
• Aviation human factors and crew resource management (CRM)
• Risk assessment methodologies (ICAO SMS, FAA SMS)
• Incident investigation techniques (NTSB, ICAO Annex 13)
• Aviation weather and its impact on UAS operations
• UAS technology and system reliability analysis

📋 ASRS FIELD EXTRACTION PRIORITIES:

1. **TEMPORAL & SPATIAL DATA**
   - Precise date/time (UTC and local)
   - Geographic coordinates and airspace classification
   - Environmental conditions (weather, visibility, turbulence)

2. **AIRCRAFT & OPERATIONS**
   - UAS specifications (weight, type, propulsion)
   - Mission profile and operational limitations
   - Control method (VLOS, BVLOS, autonomous modes)

3. **REGULATORY COMPLIANCE**
   - Part 107 operations vs. special authorizations
   - Airspace authorizations (LAANC, COA, waivers)
   - Pilot certifications and currency requirements

4. **INCIDENT TAXONOMY**
   - Event classification per ASRS categories
   - Severity assessment (damage, injuries, operational impact)
   - Detection method and reporting chain

5. **CAUSAL ANALYSIS**
   - Primary failure modes and root causes
   - Contributing factors across multiple domains
   - System vulnerabilities and design inadequacies

🔍 PROFESSIONAL QUESTION GENERATION:
Generate questions that demonstrate deep UAS operational knowledge:

**Regulatory & Authorization:**
- "What specific Part 107 operations were being conducted, and were any waivers or authorizations in effect?"
- "Was LAANC authorization obtained for this airspace, and were operational parameters adhered to?"
- "What coordination was conducted with ATC or other airspace users?"

**Technical & Systems:**
- "What redundancy systems were available, and how did they perform during the incident?"
- "What was the aircraft's maintenance status and service history?"
- "Were there any known AD's (Airworthiness Directives) or service bulletins applicable to this aircraft?"

**Human Factors & CRM:**
- "How did crew resource management principles apply to this operation?"
- "What training and proficiency requirements were in place for this mission type?"
- "Were standard operating procedures followed, and if not, what factors influenced the deviations?"

**Environmental & Operational:**
- "How did environmental conditions compare to operational limitations and minimums?"
- "What risk assessment procedures were followed during mission planning?"
- "Were there any NOTAM's or TFR's that affected the operation?"

🎯 ANALYSIS STANDARDS:
• Apply NASA ASRS quality standards for data integrity and completeness
• Use precise aviation terminology and industry-standard classifications
• Focus on information that supports safety trend analysis and risk mitigation
• Consider lessons learned that benefit the broader aviation safety community
• Maintain objectivity and non-punitive approach consistent with ASRS principles

💡 SAFETY INTELLIGENCE:
Extract insights that contribute to:
- Industry-wide safety trend identification
- Regulatory policy development support
- Training program enhancement opportunities
- Technology improvement recommendations
- Best practice dissemination

Your analysis should meet NASA ASRS standards for completeness, accuracy, and safety value while maintaining the confidential, non-punitive nature of safety reporting systems."""
    
    def analyze_narrative(self, narrative: str, existing_data: Dict = None) -> SmartFormResult:
        """
        分析叙述并智能填写表单
        
        Args:
            narrative: 事故叙述
            existing_data: 已有的表单数据
            
        Returns:
            SmartFormResult: 分析结果
        """
        try:
            if self.use_mock:
                return self._mock_analysis(narrative, existing_data)
            else:
                return self._openai_analysis(narrative, existing_data)
        except Exception as e:
            logger.error(f"叙述分析失败: {e}")
            return self._fallback_analysis(narrative, existing_data)
    
    def _create_extraction_function_schema(self):
        """创建信息提取的Function Schema"""
        return {
            "name": "extract_incident_information",
            "description": "Extract structured information from incident narrative",
            "parameters": {
                "type": "object",
                "properties": {
                    "extracted_fields": {
                        "type": "object",
                        "description": "Extracted field values from narrative",
                        "properties": {
                            "flight_phase": {"type": "string", "description": "Flight phase when incident occurred"},
                            "altitude_agl": {"type": "number", "description": "Altitude above ground level in feet"},
                            "altitude_msl": {"type": "number", "description": "Altitude above mean sea level in feet"},
                            "weather": {"type": "string", "description": "Weather conditions"},
                            "flight_conditions": {"type": "string", "enum": ["VMC", "IMC", "Mixed"]},
                            "light": {"type": "string", "enum": ["Daylight", "Dusk", "Night", "Dawn"]},
                            "make_model": {"type": "string", "description": "Aircraft make and model"},
                            "mission": {"type": "string", "description": "Mission type"},
                            "airspace": {"type": "string", "description": "Airspace type"},
                            "anomaly": {"type": "string", "description": "Description of the anomaly/incident"},
                            "detector": {"type": "string", "enum": ["Pilot", "ATC", "Observer", "System", "Other"]},
                            "result": {"type": "string", "description": "Outcome/result of the incident"},
                            "primary_problem": {"type": "string", "description": "Primary problem identified"},
                            "contributing_factors": {"type": "string", "description": "Contributing factors"},
                            "human_factors": {"type": "string", "description": "Human factors involved"}
                        }
                    },
                    "confidence_scores": {
                        "type": "object",
                        "description": "Confidence scores for each extracted field (0.0-1.0). Higher scores indicate more certain extraction. Score based on clarity and specificity of information in narrative.",
                        "additionalProperties": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        }
                    },
                    "missing_critical_info": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of critical missing information"
                    },
                    "suggested_questions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Professional aviation safety questions to gather missing critical information, based on UAV operational knowledge and safety standards"
                    },
                    "synopsis": {
                        "type": "string",
                        "description": "Concise synopsis of the incident (2-3 sentences)"
                    },
                    "completeness_score": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Data completeness score"
                    }
                },
                "required": ["extracted_fields", "confidence_scores", "missing_critical_info", "suggested_questions", "synopsis", "completeness_score"]
            }
        }
    
    def _openai_analysis(self, narrative: str, existing_data: Dict = None) -> SmartFormResult:
        """使用OpenAI进行分析"""
        
        prompt = self._build_analysis_prompt(narrative, existing_data)
        
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
                "functions": [self._create_extraction_function_schema()],
                "function_call": {"name": "extract_incident_information"},
                "temperature": 0.1,
                "max_tokens": 2000
            }

            response = requests.post(url, headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                message = result['choices'][0]['message']

                if 'function_call' in message:
                    function_result = json.loads(message['function_call']['arguments'])
                    return self._parse_extraction_result(function_result)
                else:
                    return self._fallback_analysis(narrative, existing_data)
            else:
                logger.error(f"OpenAI API调用失败: {response.status_code} - {response.text}")
                return self._fallback_analysis(narrative, existing_data)

        except Exception as e:
            logger.error(f"OpenAI分析失败: {e}")
            return self._fallback_analysis(narrative, existing_data)
    
    def _build_analysis_prompt(self, narrative: str, existing_data: Dict = None) -> str:
        """构建分析提示词"""
        
        existing_info = ""
        if existing_data:
            existing_info = f"\n**Existing Information:**\n"
            for key, value in existing_data.items():
                if value:
                    existing_info += f"- {key}: {value}\n"
        
        prompt = f"""Analyze the following UAV incident narrative and extract structured information for aviation safety reporting:

**Incident Narrative:**
{narrative}
{existing_info}

**EXTRACTION REQUIREMENTS:**
Extract all available information focusing on:

1. **Flight Operations**: Phase, altitude, weather conditions, airspace classification
2. **Aircraft Systems**: Make/model, configuration, mission profile, control mode
3. **Incident Sequence**: Timeline, detection method, immediate actions, outcomes
4. **Safety Factors**: Primary causes, contributing factors, human factors, environmental conditions
5. **Regulatory Context**: Operating authority, waivers, compliance status

**CONFIDENCE SCORING:**
For each extracted field, provide a confidence score (0.0-1.0) based on:
- 0.8-1.0: Explicitly stated with clear details
- 0.6-0.7: Clearly implied or reasonably inferred
- 0.4-0.5: Partially mentioned or somewhat unclear
- 0.2-0.3: Vaguely referenced or uncertain
- 0.0-0.1: Not mentioned or completely unclear

**INTELLIGENT QUESTION GENERATION:**
Generate professional questions based on UAV operational knowledge to gather missing critical information. Consider:

- **Regulatory Compliance**: Part 107 operations, waivers, authorizations, airspace coordination
- **Risk Factors**: Weather minimums, obstacle clearance, emergency procedures
- **Human Factors**: Pilot qualifications, crew resource management, decision-making
- **Technical Factors**: System redundancy, maintenance status, equipment limitations
- **Operational Context**: Mission planning, risk assessment, lessons learned

**SYNOPSIS REQUIREMENTS:**
Create a professional 2-3 sentence synopsis suitable for aviation safety databases, including:
- Incident type and severity
- Primary causal factors
- Safety implications

Focus on information critical for safety analysis and regulatory compliance."""
        
        return prompt
    
    def _parse_extraction_result(self, result: Dict) -> SmartFormResult:
        """解析提取结果"""

        extracted_fields = result.get("extracted_fields", {})
        confidence_scores = result.get("confidence_scores", {})

        # 如果没有置信度分数，根据字段内容生成合理的置信度
        if not confidence_scores and extracted_fields:
            confidence_scores = self._generate_confidence_scores(extracted_fields)

        return SmartFormResult(
            extracted_fields=extracted_fields,
            confidence_scores=confidence_scores,
            missing_fields=result.get("missing_critical_info", []),
            completeness_score=result.get("completeness_score", 0.0),
            suggested_questions=result.get("suggested_questions", []),
            synopsis=result.get("synopsis", ""),
            analysis_timestamp=datetime.now().isoformat()
        )

    def _generate_confidence_scores(self, extracted_fields: Dict) -> Dict[str, float]:
        """根据提取的字段生成置信度分数"""
        confidence_scores = {}

        for field, value in extracted_fields.items():
            if not value or value in ['', 'Not specified', 'Unknown', 'N/A']:
                confidence_scores[field] = 0.1
            elif isinstance(value, str):
                # 根据字段值的详细程度评估置信度
                if len(value) > 50:  # 详细描述
                    confidence_scores[field] = 0.8
                elif len(value) > 20:  # 中等详细
                    confidence_scores[field] = 0.6
                elif len(value) > 5:   # 简短但有意义
                    confidence_scores[field] = 0.4
                else:  # 很短或模糊
                    confidence_scores[field] = 0.2
            elif isinstance(value, (int, float)):
                # 数值字段通常置信度较高
                confidence_scores[field] = 0.7 if value > 0 else 0.1
            else:
                confidence_scores[field] = 0.5

        return confidence_scores
    
    def _mock_analysis(self, narrative: str, existing_data: Dict = None) -> SmartFormResult:
        """模拟分析"""
        
        # 简单的关键词提取
        extracted_fields = {}
        confidence_scores = {}
        
        narrative_lower = narrative.lower()
        
        # 飞行阶段检测
        if any(word in narrative_lower for word in ['takeoff', 'take off']):
            extracted_fields['flight_phase'] = 'Takeoff'
            confidence_scores['flight_phase'] = 0.8
        elif any(word in narrative_lower for word in ['landing', 'approach']):
            extracted_fields['flight_phase'] = 'Landing'
            confidence_scores['flight_phase'] = 0.8
        elif 'cruise' in narrative_lower:
            extracted_fields['flight_phase'] = 'Cruise'
            confidence_scores['flight_phase'] = 0.8
        
        # 天气条件检测
        if any(word in narrative_lower for word in ['clear', 'sunny', 'good weather']):
            extracted_fields['flight_conditions'] = 'VMC'
            confidence_scores['flight_conditions'] = 0.7
        elif any(word in narrative_lower for word in ['cloud', 'fog', 'rain']):
            extracted_fields['flight_conditions'] = 'IMC'
            confidence_scores['flight_conditions'] = 0.7
        
        # 高度提取
        altitude_match = re.search(r'(\d+)\s*(?:feet|ft|foot)', narrative_lower)
        if altitude_match:
            extracted_fields['altitude_agl'] = int(altitude_match.group(1))
            confidence_scores['altitude_agl'] = 0.9
        
        # 生成专业建议问题（基于UAV操作知识）
        suggested_questions = []

        # 基于叙述内容生成针对性问题
        if 'communication' in narrative_lower or 'link' in narrative_lower:
            suggested_questions.extend([
                "What was the specific frequency or communication protocol being used?",
                "Were there any known sources of electromagnetic interference in the area?",
                "What backup communication procedures were available and attempted?"
            ])

        if 'weather' in narrative_lower or 'wind' in narrative_lower:
            suggested_questions.extend([
                "What were the specific wind speeds and directions at the time of incident?",
                "Were weather conditions within the operational limitations of the UAV?",
                "Was a weather briefing obtained prior to the flight operation?"
            ])

        if 'altitude' not in narrative_lower:
            suggested_questions.append("What was the operating altitude and was it within authorized limits?")

        if 'airspace' not in narrative_lower:
            suggested_questions.append("What class of airspace was the operation conducted in, and were proper authorizations obtained?")

        # 通用专业问题
        if len(suggested_questions) < 3:
            suggested_questions.extend([
                "What was the pilot's total flight experience with this type of UAV?",
                "Were all required pre-flight inspections and checks completed?",
                "What risk mitigation measures were in place for this operation?",
                "Were there any deviations from standard operating procedures?",
                "What lessons learned or safety recommendations resulted from this incident?"
            ])

        # 限制问题数量
        suggested_questions = suggested_questions[:5]
        
        # 生成简要摘要
        synopsis = f"UAV incident involving {extracted_fields.get('flight_phase', 'unknown phase')} operations. Further analysis required to determine root cause and contributing factors."
        
        return SmartFormResult(
            extracted_fields=extracted_fields,
            confidence_scores=confidence_scores,
            missing_fields=['primary_problem', 'contributing_factors', 'human_factors'],
            completeness_score=len(extracted_fields) / 10.0,  # 简单计算
            suggested_questions=suggested_questions,
            synopsis=synopsis,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _fallback_analysis(self, narrative: str, existing_data: Dict = None) -> SmartFormResult:
        """备用分析"""
        return SmartFormResult(
            extracted_fields={},
            confidence_scores={},
            missing_fields=['All fields require manual input'],
            completeness_score=0.0,
            suggested_questions=['Please provide more detailed information about the incident'],
            synopsis="Unable to analyze narrative automatically. Manual review required.",
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def generate_completion_questions(self, current_data: Dict, narrative: str = "") -> List[str]:
        """根据当前数据生成专业补充问题"""

        if not self.use_mock and narrative.strip():
            # 使用LLM生成智能问题
            try:
                return self._generate_llm_questions(current_data, narrative)
            except:
                pass  # 如果LLM失败，使用备用方法

        questions = []
        narrative_lower = narrative.lower() if narrative else ""

        # 检查关键字段并生成专业问题
        critical_fields = ['date', 'time_of_day', 'location', 'flight_phase', 'narrative']

        for field in critical_fields:
            if not current_data.get(field):
                if field == 'date':
                    questions.append("What was the exact date and local time when the incident occurred?")
                elif field == 'time_of_day':
                    questions.append("What was the specific time of day, and were operations conducted during authorized hours?")
                elif field == 'location':
                    questions.append("What was the exact location (coordinates, airport identifier, or landmark) where the incident occurred?")
                elif field == 'flight_phase':
                    questions.append("What specific phase of flight was the UAV in when the incident occurred (takeoff, cruise, approach, etc.)?")
                elif field == 'narrative':
                    questions.append("Please provide a detailed chronological description of the incident sequence.")

        # 基于叙述内容生成专业问题
        if narrative_lower:
            # 通信相关
            if any(word in narrative_lower for word in ['communication', 'link', 'signal', 'control']):
                if not current_data.get('primary_problem'):
                    questions.append("What was the root cause of the communication/control issue, and what backup procedures were attempted?")
                if not current_data.get('human_factors'):
                    questions.append("Were there any human factors that contributed to the communication breakdown (training, procedures, situational awareness)?")

            # 天气相关
            if any(word in narrative_lower for word in ['weather', 'wind', 'visibility', 'cloud']):
                if not current_data.get('weather'):
                    questions.append("What were the specific meteorological conditions (wind speed/direction, visibility, cloud ceiling) at the time of incident?")
                questions.append("Were the weather conditions within the operational limitations specified in the UAV's flight manual?")

            # 设备故障相关
            if any(word in narrative_lower for word in ['failure', 'malfunction', 'system', 'equipment']):
                questions.append("What specific system or component failed, and what was the maintenance history of this equipment?")
                questions.append("Were there any warning signs or precursor events that might have indicated the impending failure?")

            # 空域和监管相关
            if any(word in narrative_lower for word in ['airspace', 'airport', 'atc', 'authorization']):
                questions.append("What class of airspace was involved, and were all required authorizations and clearances obtained?")
                questions.append("Was proper coordination maintained with air traffic control or other airspace users?")

            # 人为因素相关
            if any(word in narrative_lower for word in ['pilot', 'operator', 'crew', 'decision']):
                questions.append("What was the pilot's experience level with this type of UAV and operating environment?")
                questions.append("Were standard operating procedures followed, and if not, what factors led to the deviation?")

        # 通用专业问题（如果还需要更多）
        if len(questions) < 3:
            questions.extend([
                "What risk mitigation measures were in place, and how effective were they during the incident?",
                "What immediate actions were taken to ensure safety and minimize consequences?",
                "What lessons learned or safety recommendations resulted from this incident analysis?",
                "Were there any regulatory violations or non-compliance issues identified?",
                "What changes to procedures, training, or equipment are recommended to prevent recurrence?"
            ])

        return questions[:5]  # 限制问题数量

    def _generate_llm_questions(self, current_data: Dict, narrative: str) -> List[str]:
        """使用LLM生成智能问题"""

        # 分析当前数据的完整性
        missing_fields = []
        for field_name, field_def in self.form_fields.items():
            if field_def.required and not current_data.get(field_name):
                missing_fields.append(f"{field_name}: {field_def.description}")

        prompt = f"""Based on the following UAV incident narrative and current data, generate 3-5 professional questions to gather missing critical information for aviation safety analysis.

**Incident Narrative:**
{narrative}

**Current Data Available:**
{json.dumps({k: v for k, v in current_data.items() if v}, indent=2)}

**Missing Critical Fields:**
{chr(10).join(missing_fields) if missing_fields else "All required fields completed"}

**Requirements:**
Generate professional questions that:
1. Focus on aviation safety and regulatory compliance
2. Address missing critical information for incident analysis
3. Consider UAV operational factors and best practices
4. Help identify root causes and contributing factors
5. Support lessons learned and prevention strategies

Return only the questions, one per line, without numbering."""

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
                "temperature": 0.2,
                "max_tokens": 500
            }

            response = requests.post(url, headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                questions_text = result['choices'][0]['message']['content'].strip()
                questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
                return questions[:5]
            else:
                logger.error(f"LLM问题生成失败: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"LLM问题生成失败: {e}")
            return []

def main():
    """测试函数"""
    assistant = SmartFormAssistant()
    
    test_narrative = """
    During a training flight at 1500 feet AGL, the UAV experienced a sudden loss of communication link. 
    The pilot was unable to regain control and the aircraft entered autonomous return-to-home mode. 
    Weather conditions were clear with good visibility. The incident occurred during cruise phase of the flight.
    """
    
    result = assistant.analyze_narrative(test_narrative)
    
    print("智能表单分析结果:")
    print(f"提取字段: {result.extracted_fields}")
    print(f"置信度: {result.confidence_scores}")
    print(f"缺失字段: {result.missing_fields}")
    print(f"完整度: {result.completeness_score:.2f}")
    print(f"建议问题: {result.suggested_questions}")
    print(f"摘要: {result.synopsis}")

if __name__ == "__main__":
    main()
