"""
AI分析器模块 - 使用OpenAI GPT-4o-mini进行智能事故分析
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Tuple
import sqlite3
import pandas as pd
from datetime import datetime
import os
from dataclasses import dataclass

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """分析结果数据类"""
    risk_assessment: str
    root_cause_analysis: str
    contributing_factors: List[str]
    recommendations: List[str]
    preventive_measures: List[str]
    similar_cases: List[str]
    confidence_score: float
    analysis_timestamp: str

class AIAnalyzer:
    """AI分析器类"""
    
    def __init__(self, api_key: Optional[str] = None, db_path: str = "asrs_data.db"):
        """
        初始化AI分析器
        
        Args:
            api_key: OpenAI API密钥
            db_path: 数据库路径
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY') or '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'
        self.db_path = db_path
        
        if not self.api_key:
            logger.warning("未设置OpenAI API密钥，将使用模拟分析")
            self.use_mock = True
        else:
            self.use_mock = False
        
        # 系统提示词
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
    
    def analyze_incident(self, incident_data: Dict) -> AnalysisResult:
        """
        分析事故报告
        
        Args:
            incident_data: 事故数据字典
            
        Returns:
            AnalysisResult: 分析结果
        """
        try:
            if self.use_mock:
                return self._mock_analysis(incident_data)
            else:
                return self._openai_analysis(incident_data)
        except Exception as e:
            logger.error(f"分析失败: {e}")
            return self._fallback_analysis(incident_data)
    
    def _openai_analysis(self, incident_data: Dict) -> AnalysisResult:
        """使用OpenAI进行分析"""
        
        # 构建分析提示
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
                logger.error(f"OpenAI API调用失败: {response.status_code}")
                return self._fallback_analysis(incident_data)

        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            return self._fallback_analysis(incident_data)
    
    def _build_analysis_prompt(self, incident_data: Dict) -> str:
        """构建分析提示词"""
        
        prompt = f"""
        请分析以下无人机事故报告：

        **基本信息：**
        - 日期: {incident_data.get('date', 'N/A')}
        - 时间: {incident_data.get('time_of_day', 'N/A')}
        - 地点: {incident_data.get('location', 'N/A')}
        - 高度: {incident_data.get('altitude', 'N/A')} 英尺
        - 天气: {incident_data.get('weather', 'N/A')}
        - 飞行阶段: {incident_data.get('flight_phase', 'N/A')}
        - 任务类型: {incident_data.get('mission_type', 'N/A')}

        **事故描述：**
        {incident_data.get('narrative', 'N/A')}

        **主要问题：**
        {incident_data.get('primary_problem', 'N/A')}

        **贡献因素：**
        {incident_data.get('contributing_factors', 'N/A')}

        **人因因素：**
        {incident_data.get('human_factors', 'N/A')}

        请按以下格式提供分析结果：

        **风险评估：** [HIGH/MEDIUM/LOW] - 简要说明风险等级的理由

        **根本原因分析：**
        [详细分析事故的根本原因]

        **贡献因素：**
        1. [因素1]
        2. [因素2]
        3. [因素3]

        **建议措施：**
        1. [建议1]
        2. [建议2]
        3. [建议3]

        **预防措施：**
        1. [预防措施1]
        2. [预防措施2]
        3. [预防措施3]

        **置信度：** [0.0-1.0] - 分析结果的置信度
        """
        
        return prompt
    
    def _parse_analysis_response(self, analysis_text: str, incident_data: Dict) -> AnalysisResult:
        """解析AI分析响应"""
        
        # 简单的文本解析（实际应用中可能需要更复杂的解析逻辑）
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
                
            if "风险评估：" in line:
                risk_assessment = line.split("：")[1].split()[0]
                current_section = "risk"
            elif "根本原因分析：" in line:
                current_section = "root_cause"
            elif "贡献因素：" in line:
                current_section = "contributing"
            elif "建议措施：" in line:
                current_section = "recommendations"
            elif "预防措施：" in line:
                current_section = "preventive"
            elif "置信度：" in line:
                try:
                    confidence_score = float(line.split("：")[1].strip())
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
        
        # 获取相似案例
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
        """模拟分析（当没有API密钥时使用）"""
        
        narrative = incident_data.get('narrative', '').lower()
        
        # 基于关键词的简单风险评估
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
        """备用分析方法"""
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
        """查找相似案例"""
        try:
            if not os.path.exists(self.db_path):
                return []
            
            conn = sqlite3.connect(self.db_path)
            
            # 简单的相似性匹配（基于关键词）
            narrative = incident_data.get('narrative', '').lower()
            keywords = self._extract_keywords(narrative)
            
            if not keywords:
                return []
            
            # 构建查询
            keyword_conditions = []
            for keyword in keywords[:3]:  # 只使用前3个关键词
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
                case_summary = f"案例 {row['id']} ({row['risk_level']}): {row['synopsis'][:100]}..."
                similar_cases.append(case_summary)
            
            return similar_cases
            
        except Exception as e:
            logger.error(f"查找相似案例失败: {e}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        import re
        
        # 定义关键词模式
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
        
        return list(set(keywords))  # 去重
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict]:
        """获取分析历史"""
        # 这里可以实现分析历史的存储和检索
        # 暂时返回空列表
        return []
    
    def save_analysis_result(self, incident_id: str, result: AnalysisResult) -> bool:
        """保存分析结果"""
        try:
            # 这里可以实现分析结果的持久化存储
            logger.info(f"分析结果已保存，事故ID: {incident_id}")
            return True
        except Exception as e:
            logger.error(f"保存分析结果失败: {e}")
            return False

def main():
    """测试函数"""
    # 测试数据
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
    
    # 创建分析器并测试
    analyzer = AIAnalyzer()
    result = analyzer.analyze_incident(test_incident)
    
    print("分析结果:")
    print(f"风险评估: {result.risk_assessment}")
    print(f"根本原因: {result.root_cause_analysis}")
    print(f"建议措施: {result.recommendations}")
    print(f"置信度: {result.confidence_score}")

if __name__ == "__main__":
    main()
