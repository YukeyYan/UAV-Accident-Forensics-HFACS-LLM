#!/usr/bin/env python3
"""
ASRS无人机事故智能分析系统启动脚本
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import config

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """检查依赖包是否安装"""
    logger.info("检查依赖包...")
    
    required_packages = [
        'streamlit', 'pandas', 'numpy', 'openai', 
        'plotly', 'sqlite3', 'json', 'datetime'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            elif package == 'json':
                import json
            elif package == 'datetime':
                import datetime
            else:
                __import__(package)
            logger.debug(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"❌ {package} 未安装")
    
    if missing_packages:
        logger.error(f"缺少依赖包: {', '.join(missing_packages)}")
        logger.info("请运行: pip install -r requirements.txt")
        return False
    
    logger.info("✅ 所有依赖包检查通过")
    return True

def check_data_files():
    """检查数据文件是否存在"""
    logger.info("检查数据文件...")
    
    if not os.path.exists(config.CSV_DATA_PATH):
        logger.error(f"❌ CSV数据文件不存在: {config.CSV_DATA_PATH}")
        return False
    
    logger.info(f"✅ CSV数据文件存在: {config.CSV_DATA_PATH}")
    return True

def check_openai_config():
    """检查OpenAI配置"""
    logger.info("检查OpenAI配置...")
    
    if not config.OPENAI_API_KEY:
        logger.warning("⚠️ 未设置OpenAI API密钥，将使用模拟分析模式")
        return True
    
    # 简单验证API密钥格式
    if not config.OPENAI_API_KEY.startswith('sk-'):
        logger.warning("⚠️ OpenAI API密钥格式可能不正确")
    
    logger.info("✅ OpenAI配置检查完成")
    return True

def setup_environment():
    """设置环境"""
    logger.info("设置运行环境...")
    
    # 创建必要的目录
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # 设置环境变量
    os.environ['PYTHONPATH'] = str(project_root)
    
    logger.info("✅ 环境设置完成")

def run_streamlit():
    """运行Streamlit应用"""
    logger.info("启动Streamlit应用...")
    
    cmd = [
        'streamlit', 'run', 'streamlit_app.py',
        '--server.port', str(config.STREAMLIT_SERVER_PORT),
        '--server.address', config.STREAMLIT_SERVER_ADDRESS,
        '--server.headless', 'true' if not config.DEBUG else 'false',
        '--server.fileWatcherType', 'none',
        '--browser.gatherUsageStats', 'false'
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"启动Streamlit失败: {e}")
        return False
    except KeyboardInterrupt:
        logger.info("用户中断，正在关闭应用...")
        return True
    
    return True

def run_data_processor():
    """运行数据处理器"""
    logger.info("运行数据处理器...")
    
    try:
        from data_processor import main as process_data
        process_data()
        logger.info("✅ 数据处理完成")
        return True
    except Exception as e:
        logger.error(f"数据处理失败: {e}")
        return False

def run_tests():
    """运行测试"""
    logger.info("运行系统测试...")
    
    try:
        # 测试数据处理器
        from data_processor import ASRSDataProcessor
        processor = ASRSDataProcessor(config.CSV_DATA_PATH)
        logger.info("✅ 数据处理器测试通过")
        
        # 测试AI分析器
        from ai_analyzer import AIAnalyzer
        analyzer = AIAnalyzer()
        logger.info("✅ AI分析器测试通过")
        
        # 测试HFACS分析器
        from hfacs_analyzer import HFACSAnalyzer
        hfacs = HFACSAnalyzer()
        logger.info("✅ HFACS分析器测试通过")
        
        logger.info("✅ 所有测试通过")
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='ASRS无人机事故智能分析系统')
    parser.add_argument('--mode', choices=['web', 'process', 'test'], default='web',
                       help='运行模式: web(启动Web应用), process(处理数据), test(运行测试)')
    parser.add_argument('--skip-checks', action='store_true',
                       help='跳过环境检查')
    parser.add_argument('--debug', action='store_true',
                       help='启用调试模式')
    
    args = parser.parse_args()
    
    # 设置调试模式
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("启用调试模式")
    
    logger.info(f"启动 {config.APP_NAME} v{config.APP_VERSION}")
    
    # 环境检查
    if not args.skip_checks:
        logger.info("开始环境检查...")
        
        if not check_dependencies():
            logger.error("依赖检查失败，退出")
            sys.exit(1)
        
        if not check_data_files():
            logger.error("数据文件检查失败，退出")
            sys.exit(1)
        
        if not check_openai_config():
            logger.error("OpenAI配置检查失败，退出")
            sys.exit(1)
        
        logger.info("✅ 环境检查通过")
    
    # 设置环境
    setup_environment()
    
    # 根据模式运行
    if args.mode == 'web':
        logger.info("启动Web应用模式")
        success = run_streamlit()
    elif args.mode == 'process':
        logger.info("启动数据处理模式")
        success = run_data_processor()
    elif args.mode == 'test':
        logger.info("启动测试模式")
        success = run_tests()
    else:
        logger.error(f"未知模式: {args.mode}")
        sys.exit(1)
    
    if success:
        logger.info("✅ 程序执行完成")
        sys.exit(0)
    else:
        logger.error("❌ 程序执行失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
