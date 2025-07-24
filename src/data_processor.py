"""
ASRS UAV Incident Report Data Processing Module
Process CSV data, extract key information, prepare for AI analysis
"""

import pandas as pd
import numpy as np
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ASRSDataProcessor:
    """ASRS Data Processor"""
    
    def __init__(self, csv_file_path: str, db_path: str = "asrs_data.db"):
        self.csv_file_path = csv_file_path
        self.db_path = db_path
        self.df = None
        self.processed_data = []
        
    def load_data(self) -> pd.DataFrame:
        """Load CSV data with fallback for cloud deployment"""
        try:
            # Check if CSV file exists
            import os
            if not os.path.exists(self.csv_file_path):
                logger.warning(f"CSV file not found at {self.csv_file_path}, creating empty DataFrame")
                # Create empty DataFrame with expected columns for cloud deployment
                self.df = pd.DataFrame(columns=[
                    'ACN', 'Time', 'Aircraft_1_Reference', 'Aircraft_1_AircraftCategory', 
                    'Primary_Problem', 'Narrative', 'Human_Factors'
                ])
                return self.df
            # Read CSV file, skip first two rows (multi-line headers), use second row as column names
            self.df = pd.read_csv(self.csv_file_path, skiprows=[0], header=0)
            
            # Remove completely empty rows (like third row)
            self.df = self.df.dropna(how='all')
            
            logger.info(f"Successfully loaded ASRS UAV data, {len(self.df)} records total")
            
            # Display basic statistics
            if len(self.df) > 0:
                logger.info(f"Number of columns: {len(self.df.columns)}")
                logger.info(f"Main fields: ACN, Narrative, Synopsis, etc.")
                
                # Check key fields
                key_fields = ['ACN', 'Narrative', 'Synopsis', 'Primary Problem']
                available_fields = [field for field in key_fields if field in self.df.columns]
                logger.info(f"Available key fields: {available_fields}")
            
            return self.df
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise
    
    def clean_data(self) -> pd.DataFrame:
        """Clean and preprocess data"""
        if self.df is None:
            raise ValueError("Please load data first")
        
        logger.info("开始清理ASRS UAV事故数据...")
        original_count = len(self.df)
        
        # 删除完全空白的行
        self.df = self.df.dropna(how='all')
        logger.info(f"删除空行后，从{original_count}条减少到{len(self.df)}条记录")
        
        # 处理关键字段的缺失值
        key_columns = ['ACN', 'Narrative', 'Synopsis', 'Primary Problem', 'Human Factors']
        for col in key_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna('')
                logger.info(f"处理字段 '{col}' 的缺失值")
            else:
                logger.warning(f"关键字段 '{col}' 不存在于数据中")
        
        # 标准化日期格式 - ASRS日期格式为YYYYMM
        if 'Date' in self.df.columns:
            try:
                # 将YYYYMM格式转换为日期
                self.df['Date'] = pd.to_datetime(self.df['Date'], format='%Y%m', errors='coerce')
                logger.info("日期字段标准化完成")
            except Exception as e:
                logger.warning(f"日期格式转换失败: {e}")
        
        # 过滤掉关键字段为空的记录（ACN是必须的）
        if 'ACN' in self.df.columns:
            before_filter = len(self.df)
            self.df = self.df[self.df['ACN'].notna() & (self.df['ACN'] != '')]
            after_filter = len(self.df)
            if before_filter != after_filter:
                logger.info(f"过滤无ACN记录：从{before_filter}条减少到{after_filter}条")
        
        # 确保数据类型正确
        if 'ACN' in self.df.columns:
            self.df['ACN'] = self.df['ACN'].astype(str)
        
        logger.info(f"数据清理完成！最终有效记录: {len(self.df)}条")
        
        # 显示数据预览
        if len(self.df) > 0:
            logger.info("数据预览 - 前几个ACN号码:")
            acn_sample = self.df['ACN'].head(3).tolist() if 'ACN' in self.df.columns else []
            logger.info(f"ACN样本: {acn_sample}")
        
        return self.df
    
    def extract_key_features(self) -> List[Dict]:
        """提取关键特征用于AI分析"""
        if self.df is None:
            raise ValueError("Please load data first")
        
        self.processed_data = []
        
        for idx, row in self.df.iterrows():
            try:
                # 提取基本信息
                record = {
                    'id': str(row.get('ACN', f'record_{idx}')),
                    'date': self._safe_get(row, 'Date'),
                    'time_of_day': self._safe_get(row, 'Local Time Of Day'),
                    'location': {
                        'locale': self._safe_get(row, 'Locale Reference'),
                        'state': self._safe_get(row, 'State Reference'),
                        'altitude_agl': self._safe_get(row, 'Altitude.AGL.Single Value'),
                        'altitude_msl': self._safe_get(row, 'Altitude.MSL.Single Value')
                    },
                    'environment': {
                        'flight_conditions': self._safe_get(row, 'Flight Conditions'),
                        'weather': self._safe_get(row, 'Weather Elements / Visibility'),
                        'light': self._safe_get(row, 'Light'),
                        'ceiling': self._safe_get(row, 'Ceiling')
                    },
                    'aircraft': {
                        'operator': self._safe_get(row, 'Aircraft Operator'),
                        'make_model': self._safe_get(row, 'Make Model Name'),
                        'flight_phase': self._safe_get(row, 'Flight Phase'),
                        'mission': self._safe_get(row, 'Mission'),
                        'airspace': self._safe_get(row, 'Airspace')
                    },
                    'personnel': {
                        'function': self._safe_get(row, 'Function'),
                        'qualification': self._safe_get(row, 'Qualification'),
                        'experience': self._safe_get(row, 'Experience')
                    },
                    'event': {
                        'anomaly': self._safe_get(row, 'Anomaly'),
                        'primary_problem': self._safe_get(row, 'Primary Problem'),
                        'contributing_factors': self._safe_get(row, 'Contributing Factors / Situations'),
                        'human_factors': self._safe_get(row, 'Human Factors'),
                        'detector': self._safe_get(row, 'Detector'),
                        'result': self._safe_get(row, 'Result')
                    },
                    'narrative': self._safe_get(row, 'Narrative'),
                    'synopsis': self._safe_get(row, 'Synopsis'),
                    'callback': self._safe_get(row, 'Callback')
                }
                
                # 计算风险等级（基于多个因素）
                record['risk_level'] = self._calculate_risk_level(record)
                
                # 提取关键词
                record['keywords'] = self._extract_keywords(record)
                
                self.processed_data.append(record)
                
            except Exception as e:
                logger.warning(f"处理第{idx}行数据时出错: {e}")
                continue
        
        logger.info(f"特征提取完成，处理了{len(self.processed_data)}条记录")
        return self.processed_data
    
    def _safe_get(self, row: pd.Series, column: str, default: str = '') -> str:
        """安全获取列值"""
        try:
            value = row.get(column, default)
            return str(value) if pd.notna(value) else default
        except:
            return default
    
    def _calculate_risk_level(self, record: Dict) -> str:
        """计算风险等级"""
        risk_score = 0
        
        # 基于事故类型评分
        high_risk_keywords = ['collision', 'crash', 'emergency', 'loss of control', 'system failure']
        medium_risk_keywords = ['deviation', 'violation', 'communication breakdown']
        
        narrative = record.get('narrative', '').lower()
        primary_problem = record.get('event', {}).get('primary_problem', '').lower()
        
        for keyword in high_risk_keywords:
            if keyword in narrative or keyword in primary_problem:
                risk_score += 3
        
        for keyword in medium_risk_keywords:
            if keyword in narrative or keyword in primary_problem:
                risk_score += 2
        
        # 基于人因评分
        human_factors = record.get('event', {}).get('human_factors', '').lower()
        if 'fatigue' in human_factors or 'stress' in human_factors:
            risk_score += 2
        
        # 基于环境因素评分
        weather = record.get('environment', {}).get('weather', '').lower()
        if 'imc' in weather or 'thunderstorm' in weather:
            risk_score += 2
        
        # 转换为风险等级
        if risk_score >= 6:
            return 'HIGH'
        elif risk_score >= 3:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _extract_keywords(self, record: Dict) -> List[str]:
        """提取关键词"""
        text = f"{record.get('narrative', '')} {record.get('synopsis', '')}"
        
        # 定义关键词模式
        patterns = [
            r'\b(UAV|UAS|drone|unmanned)\b',
            r'\b(collision|crash|emergency|failure)\b',
            r'\b(communication|link|control)\b',
            r'\b(weather|wind|visibility)\b',
            r'\b(pilot|operator|crew)\b',
            r'\b(airspace|altitude|flight)\b'
        ]
        
        keywords = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.extend([match.lower() for match in matches])
        
        return list(set(keywords))  # 去重
    
    def save_to_database(self) -> None:
        """保存处理后的数据到SQLite数据库"""
        if not self.processed_data:
            raise ValueError("没有处理后的数据可保存")
        
        conn = sqlite3.connect(self.db_path)
        
        try:
            # 创建表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS asrs_reports (
                    id TEXT PRIMARY KEY,
                    date TEXT,
                    time_of_day TEXT,
                    location TEXT,
                    environment TEXT,
                    aircraft TEXT,
                    personnel TEXT,
                    event TEXT,
                    narrative TEXT,
                    synopsis TEXT,
                    callback TEXT,
                    risk_level TEXT,
                    keywords TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 插入数据
            for record in self.processed_data:
                conn.execute('''
                    INSERT OR REPLACE INTO asrs_reports 
                    (id, date, time_of_day, location, environment, aircraft, 
                     personnel, event, narrative, synopsis, callback, risk_level, keywords)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record['id'],
                    str(record['date']),
                    record['time_of_day'],
                    json.dumps(record['location']),
                    json.dumps(record['environment']),
                    json.dumps(record['aircraft']),
                    json.dumps(record['personnel']),
                    json.dumps(record['event']),
                    record['narrative'],
                    record['synopsis'],
                    record['callback'],
                    record['risk_level'],
                    json.dumps(record['keywords'])
                ))
            
            conn.commit()
            logger.info(f"成功保存{len(self.processed_data)}条记录到数据库")
            
        except Exception as e:
            logger.error(f"保存数据库失败: {e}")
            raise
        finally:
            conn.close()
    
    def get_statistics(self) -> Dict:
        """获取数据统计信息"""
        if not self.processed_data:
            return {}
        
        stats = {
            'total_records': len(self.processed_data),
            'risk_distribution': {},
            'common_problems': {},
            'flight_phases': {},
            'operators': {}
        }
        
        # 风险等级分布
        risk_levels = [record['risk_level'] for record in self.processed_data]
        stats['risk_distribution'] = {level: risk_levels.count(level) for level in set(risk_levels)}
        
        # 常见问题
        problems = [record['event']['primary_problem'] for record in self.processed_data if record['event']['primary_problem']]
        problem_counts = {}
        for problem in problems:
            problem_counts[problem] = problem_counts.get(problem, 0) + 1
        stats['common_problems'] = dict(sorted(problem_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # 飞行阶段分布
        phases = [record['aircraft']['flight_phase'] for record in self.processed_data if record['aircraft']['flight_phase']]
        phase_counts = {}
        for phase in phases:
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        stats['flight_phases'] = dict(sorted(phase_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return stats

def main():
    """主函数，用于测试数据处理器"""
    from config.config import Config
    processor = ASRSDataProcessor(Config.CSV_DATA_PATH)
    
    # 加载和处理数据
    processor.load_data()
    processor.clean_data()
    processor.extract_key_features()
    
    # 保存到数据库
    processor.save_to_database()
    
    # 打印统计信息
    stats = processor.get_statistics()
    print("数据统计信息:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
