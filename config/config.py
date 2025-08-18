"""
系统配置文件
"""

import os
from typing import Dict, Any

class Config:
    """系统配置类"""
    
    # 基本配置
    APP_NAME = "ASRS无人机事故智能分析系统"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # 项目仓库配置
    GITHUB_REPOSITORY_URL = "https://github.com/YukeyYan/UAV-Accident-Forensics-HFACS-LLM"
    SUPPLEMENTARY_MATERIALS_URL = f"{GITHUB_REPOSITORY_URL}/tree/master/05_Paper/Appendix"
    
    # 数据库配置
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'asrs_data.db')
    # 使用绝对路径确保在部署环境中能找到文件
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up to project root
    CSV_DATA_PATH = os.getenv('CSV_DATA_PATH', os.path.join(BASE_DIR, 'data', 'ASRS_DBOnline_Report.csv'))
    
    # OpenAI配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.1'))
    
    # Streamlit配置
    STREAMLIT_SERVER_PORT = int(os.getenv('STREAMLIT_SERVER_PORT', '8501'))
    STREAMLIT_SERVER_ADDRESS = os.getenv('STREAMLIT_SERVER_ADDRESS', 'localhost')
    
    # 分析配置
    MAX_SIMILAR_CASES = int(os.getenv('MAX_SIMILAR_CASES', '5'))
    ANALYSIS_CONFIDENCE_THRESHOLD = float(os.getenv('ANALYSIS_CONFIDENCE_THRESHOLD', '0.6'))
    
    # 缓存配置
    ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'True').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))  # 1小时
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'asrs_system.log')
    
    # HFACS配置
    HFACS_CONFIDENCE_THRESHOLD = float(os.getenv('HFACS_CONFIDENCE_THRESHOLD', '0.5'))
    
    # 风险评估配置
    RISK_KEYWORDS = {
        'HIGH': ['crash', 'collision', 'emergency', 'failure', 'loss of control'],
        'MEDIUM': ['deviation', 'violation', 'communication breakdown', 'weather'],
        'LOW': ['minor', 'routine', 'normal']
    }
    
    # 数据处理配置
    MAX_RECORDS_PER_BATCH = int(os.getenv('MAX_RECORDS_PER_BATCH', '1000'))
    DATA_VALIDATION_ENABLED = os.getenv('DATA_VALIDATION_ENABLED', 'True').lower() == 'true'
    
    # 安全配置
    ENABLE_API_KEY_VALIDATION = os.getenv('ENABLE_API_KEY_VALIDATION', 'True').lower() == 'true'
    MAX_REQUEST_SIZE = int(os.getenv('MAX_REQUEST_SIZE', '10485760'))  # 10MB
    
    # 性能配置
    ENABLE_PERFORMANCE_MONITORING = os.getenv('ENABLE_PERFORMANCE_MONITORING', 'False').lower() == 'true'
    MAX_CONCURRENT_ANALYSES = int(os.getenv('MAX_CONCURRENT_ANALYSES', '3'))
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """获取配置字典"""
        return {
            key: getattr(cls, key) 
            for key in dir(cls) 
            if not key.startswith('_') and not callable(getattr(cls, key))
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置"""
        errors = []
        
        # 检查必要的文件路径
        if not os.path.exists(cls.CSV_DATA_PATH):
            errors.append(f"CSV数据文件不存在: {cls.CSV_DATA_PATH}")
        
        # 检查OpenAI API密钥（如果启用验证）
        if cls.ENABLE_API_KEY_VALIDATION and not cls.OPENAI_API_KEY:
            errors.append("未设置OpenAI API密钥")
        
        # 检查数值范围
        if not 0 <= cls.OPENAI_TEMPERATURE <= 2:
            errors.append("OpenAI温度参数应在0-2之间")
        
        if not 0 <= cls.ANALYSIS_CONFIDENCE_THRESHOLD <= 1:
            errors.append("分析置信度阈值应在0-1之间")
        
        if errors:
            print("配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True

# 创建全局配置实例
config = Config()

# 环境变量模板（用于部署）
ENV_TEMPLATE = """
# ASRS系统环境变量配置模板
# 复制此文件为 .env 并填入实际值

# 基本配置
DEBUG=False

# 数据库配置
DATABASE_PATH=asrs_data.db
CSV_DATA_PATH=ASRS_DBOnline_Report.csv

# OpenAI配置（必填）
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.3

# Streamlit配置
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost

# 分析配置
MAX_SIMILAR_CASES=5
ANALYSIS_CONFIDENCE_THRESHOLD=0.6

# 缓存配置
ENABLE_CACHE=True
CACHE_TTL=3600

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=asrs_system.log

# HFACS配置
HFACS_CONFIDENCE_THRESHOLD=0.5

# 数据处理配置
MAX_RECORDS_PER_BATCH=1000
DATA_VALIDATION_ENABLED=True

# 安全配置
ENABLE_API_KEY_VALIDATION=True
MAX_REQUEST_SIZE=10485760

# 性能配置
ENABLE_PERFORMANCE_MONITORING=False
MAX_CONCURRENT_ANALYSES=3
"""

def create_env_file():
    """创建环境变量模板文件"""
    if not os.path.exists('.env'):
        with open('.env.template', 'w', encoding='utf-8') as f:
            f.write(ENV_TEMPLATE)
        print("已创建环境变量模板文件: .env.template")
        print("请复制为 .env 文件并填入实际配置值")

if __name__ == "__main__":
    # 验证配置
    if config.validate_config():
        print("✅ 配置验证通过")
    else:
        print("❌ 配置验证失败")
    
    # 创建环境变量模板
    create_env_file()
    
    # 显示当前配置
    print("\n当前配置:")
    for key, value in config.get_config_dict().items():
        if 'API_KEY' in key and value:
            value = '*' * len(str(value))  # 隐藏API密钥
        print(f"  {key}: {value}")
