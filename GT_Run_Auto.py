#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GT_Run_Auto - HFACS分类自动化评估器
基于GT_Run的评估逻辑，使用OpenAI和本地LLM自动评估HFACS分类结果的正确性
支持18类别+4层级双重评估，批量处理，CSV导出
"""

import argparse
import json
import os
import sys
import glob
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from openai import OpenAI
from tqdm import tqdm
import requests
import pandas as pd
import re  # ✅ 用于从LLM返回文本中提取JSON

# 18个HFACS 8.0分类定义
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

# HFACS四个层级
HFACS_LAYERS = [
    "UNSAFE ACTS", 
    "PRECONDITIONS", 
    "SUPERVISION/LEADERSHIP", 
    "ORGANIZATIONAL INFLUENCES"
]

# 类别到层级的映射
CATEGORY_TO_LAYER = {}
for category in HFACS_CATEGORIES:
    for layer in HFACS_LAYERS:
        if category.startswith(layer):
            CATEGORY_TO_LAYER[category] = layer
            break

# 评估专用的Function Schema
EVALUATION_FUNCTION_SCHEMA = {
    "name": "evaluate_hfacs_classification",
    "description": "Evaluate the correctness of HFACS classifications for multiple sentences",
    "parameters": {
        "type": "object",
        "properties": {
            "evaluations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "sentence_id": {"type": "string"},
                        "category_is_correct": {
                            "type": "integer",
                            "enum": [0, 1, -1],
                            "description": "Whether the HFACS category classification is correct: 1=correct, 0=incorrect, -1=skip/uncertain"
                        },
                        "category_evaluation_reason": {
                            "type": "string",
                            "description": "Brief reason for category evaluation decision"
                        },
                        "layer_is_correct": {
                            "type": "integer", 
                            "enum": [0, 1, -1],
                            "description": "Whether the HFACS layer classification is correct: 1=correct, 0=incorrect, -1=skip/uncertain"
                        },
                        "layer_evaluation_reason": {
                            "type": "string",
                            "description": "Brief reason for layer evaluation decision"
                        },
                        "final_category": {
                            "type": "string",
                            "description": "Final HFACS category (one of 18 categories). If category_is_correct=1, use original; if 0, select correct one; if -1, leave empty"
                        },
                        "final_layer": {
                            "type": "string",
                            "description": "Final HFACS layer (one of 4 layers). If layer_is_correct=1, use original; if 0, select correct one; if -1, leave empty"
                        }
                    },
                    "required": [
                        "sentence_id",
                        "category_is_correct", 
                        "category_evaluation_reason",
                        "layer_is_correct",
                        "layer_evaluation_reason",
                        "final_category",
                        "final_layer"
                    ]
                }
            }
        },
        "required": ["evaluations"]
    }
}

# 系统提示词 - 专门用于评估HFACS分类正确性（强调保持"怀疑"态度）
EVALUATION_SYSTEM_PROMPT = """You are an expert aviation-safety analyst specialised in HFACS (Human Factors Analysis and Classification System) evaluation.

Your mission is to SKEPTICALLY evaluate whether each provided HFACS classification is correct AND provide the final correct classification.

Analyse for every sentence:
1. The raw sentence text.
2. The assigned HFACS category (one of the 18 specific categories).
3. The assigned HFACS layer (one of the 4 general layers).
4. The original reasoning that was given for the classification.

When judging, keep a critical mindset – if evidence is weak or ambiguous, mark the classification incorrect (0) or uncertain (-1). Do NOT give credit without strong textual support.

EVALUATION CRITERIA:
• Category: Is the 18-category classification accurate?
• Layer: Is the 4-layer classification accurate?

EVALUATION VALUES:
• 1 = Correct
• 0 = Incorrect
• -1 = Skip / Uncertain (evidence ambiguous)

FINAL CLASSIFICATION RULES:
• final_category: 
  - If category_is_correct = 1, use the original assigned category
  - If category_is_correct = 0, select the correct category from the 18 HFACS categories
  - If category_is_correct = -1, leave empty string ""
• final_layer:
  - If layer_is_correct = 1, use the original assigned layer
  - If layer_is_correct = 0, select the correct layer from the 4 HFACS layers
  - If layer_is_correct = -1, leave empty string ""

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

REASONING GUIDELINES:
• Be concise (≤ 30 words per reason)
• Explicitly reference sentence content when possible
• Remain objective and consistent with HFACS definitions
• Default to doubt; better to mark 0/-1 than to approve a wrong label"""

# Few-shot示例：覆盖全部18类，每类 1 句。前 10 条示范"正确"评估，后 8 条示范"错误"评估，体现批判思维。
_FEW_SHOT_USER_CONTENT = """Evaluate these HFACS classifications:

ID: s1
Text: "The mechanic torqued the main-rotor nut 40 % beyond the published limit."
Assigned Category: UNSAFE ACTS—Errors—Performance/Skill-Based
Assigned Layer: UNSAFE ACTS
Original Reason: "Over-torque due to poor skill usage."

ID: s2
Text: "The pilot elected VFR into forecast embedded thunderstorms despite an IFR alternative."
Assigned Category: UNSAFE ACTS—Errors—Judgement & Decision-Making
Assigned Layer: UNSAFE ACTS
Original Reason: "Risky decision-making shows judgement error."

ID: s3
Text: "Crew knowingly disabled the landing-gear warning horn to eliminate its noise."
Assigned Category: UNSAFE ACTS—Known Deviations
Assigned Layer: UNSAFE ACTS
Original Reason: "Deliberate violation of safety device."

ID: s4
Text: "Freezing rain coated the runway with ice during landing."
Assigned Category: PRECONDITIONS—Physical Environment
Assigned Layer: PRECONDITIONS
Original Reason: "Adverse weather is physical environment factor."

ID: s5
Text: "A false stall warning distracted the crew during climb-out."
Assigned Category: PRECONDITIONS—Technological Environment
Assigned Layer: PRECONDITIONS
Original Reason: "Malfunctioning warning system is technological factor."

ID: s6
Text: "Captain ignored the first-officer's 'minimums' call-out and continued descent."
Assigned Category: PRECONDITIONS—Team Coordination/Communication
Assigned Layer: PRECONDITIONS
Original Reason: "Breakdown in crew communication."

ID: s7
Text: "The loader had never been trained on the new hydraulic hoist."
Assigned Category: PRECONDITIONS—Training Conditions
Assigned Layer: PRECONDITIONS
Original Reason: "Lack of task-specific training."

ID: s8
Text: "Pilot fixated on the TCAS display and missed altitude deviations."
Assigned Category: PRECONDITIONS—Mental Awareness (Attention)
Assigned Layer: PRECONDITIONS
Original Reason: "Attention fixation degraded situational awareness."

ID: s9
Text: "Engineer dismissed rising vibration as normal for the old airframe."
Assigned Category: PRECONDITIONS—State of Mind
Assigned Layer: PRECONDITIONS
Original Reason: "Complacency influenced hazard appraisal."

ID: s10
Text: "Driver had been awake for 22 hours before starting the night convoy."
Assigned Category: PRECONDITIONS—Adverse Physiological
Assigned Layer: PRECONDITIONS
Original Reason: "Severe fatigue impairs performance."

ID: s11
Text: "Squadron slogan 'mission first, paperwork later' discouraged near-miss reporting."
Assigned Category: SUPERVISION/LEADERSHIP—Unit Safety Culture
Assigned Layer: SUPERVISION/LEADERSHIP
Original Reason: "Local culture prioritised schedule over safety."

ID: s12
Text: "Commander ordered crews to skip brake-temperature checks to save time."
Assigned Category: SUPERVISION/LEADERSHIP—Supervisory Known Deviations
Assigned Layer: SUPERVISION/LEADERSHIP
Original Reason: "Supervisor knowingly waived mandatory step."

ID: s13
Text: "Scheduled maintenance audits were never conducted despite written policy."
Assigned Category: SUPERVISION/LEADERSHIP—Ineffective Supervision
Assigned Layer: SUPERVISION/LEADERSHIP
Original Reason: "Lack of oversight allowed unsafe practice."

ID: s14
Text: "Duty roster paired two low-time pilots on a night cargo run."
Assigned Category: SUPERVISION/LEADERSHIP—Ineffective Planning & Coordination
Assigned Layer: SUPERVISION/LEADERSHIP
Original Reason: "Poor crew pairing shows bad planning."

ID: s15
Text: "Headquarters campaign 'Fly more, spend less' pushed bases to lengthen duty days."
Assigned Category: ORGANIZATIONAL INFLUENCES—Climate/Culture
Assigned Layer: ORGANIZATIONAL INFLUENCES
Original Reason: "High-level culture increased operational risk."

ID: s16
Text: "Two maintenance manuals listed conflicting torque limits for the same engine model."
Assigned Category: ORGANIZATIONAL INFLUENCES—Policy/Procedures/Process
Assigned Layer: ORGANIZATIONAL INFLUENCES
Original Reason: "Unclear documentation is process flaw."

ID: s17
Text: "Funding shortages delayed replacement of cracked tow-bars across the fleet."
Assigned Category: ORGANIZATIONAL INFLUENCES—Resource Support
Assigned Layer: ORGANIZATIONAL INFLUENCES
Original Reason: "Inadequate resources left hazards unmitigated."

ID: s18
Text: "The formal school syllabus for the new UAV lacked any night-operations module."
Assigned Category: ORGANIZATIONAL INFLUENCES—Training Program Issues
Assigned Layer: ORGANIZATIONAL INFLUENCES
Original Reason: "Training program omitted essential content."
"""

# 生成对应的 assistant function-call结果（前10正确，后8错误）

# 定义18个示例的原始分类（与上面的示例对应）
_EXAMPLE_CATEGORIES = [
    "UNSAFE ACTS—Errors—Performance/Skill-Based",  # s1
    "UNSAFE ACTS—Errors—Judgement & Decision-Making",  # s2
    "UNSAFE ACTS—Known Deviations",  # s3
    "PRECONDITIONS—Physical Environment",  # s4
    "PRECONDITIONS—Technological Environment",  # s5
    "PRECONDITIONS—Team Coordination/Communication",  # s6
    "PRECONDITIONS—Training Conditions",  # s7
    "PRECONDITIONS—Mental Awareness (Attention)",  # s8
    "PRECONDITIONS—State of Mind",  # s9
    "PRECONDITIONS—Adverse Physiological",  # s10
    "SUPERVISION/LEADERSHIP—Unit Safety Culture",  # s11
    "SUPERVISION/LEADERSHIP—Supervisory Known Deviations",  # s12
    "SUPERVISION/LEADERSHIP—Ineffective Supervision",  # s13
    "SUPERVISION/LEADERSHIP—Ineffective Planning & Coordination",  # s14
    "ORGANIZATIONAL INFLUENCES—Climate/Culture",  # s15
    "ORGANIZATIONAL INFLUENCES—Policy/Procedures/Process",  # s16
    "ORGANIZATIONAL INFLUENCES—Resource Support",  # s17
    "ORGANIZATIONAL INFLUENCES—Training Program Issues"  # s18
]

_EXAMPLE_LAYERS = [
    "UNSAFE ACTS",  # s1
    "UNSAFE ACTS",  # s2
    "UNSAFE ACTS",  # s3
    "PRECONDITIONS",  # s4
    "PRECONDITIONS",  # s5
    "PRECONDITIONS",  # s6
    "PRECONDITIONS",  # s7
    "PRECONDITIONS",  # s8
    "PRECONDITIONS",  # s9
    "PRECONDITIONS",  # s10
    "SUPERVISION/LEADERSHIP",  # s11
    "SUPERVISION/LEADERSHIP",  # s12
    "SUPERVISION/LEADERSHIP",  # s13
    "SUPERVISION/LEADERSHIP",  # s14
    "ORGANIZATIONAL INFLUENCES",  # s15
    "ORGANIZATIONAL INFLUENCES",  # s16
    "ORGANIZATIONAL INFLUENCES",  # s17
    "ORGANIZATIONAL INFLUENCES"  # s18
]

# 为后8个错误示例定义正确的分类
_CORRECT_CATEGORIES_FOR_ERRORS = [
    "SUPERVISION/LEADERSHIP—Ineffective Supervision",  # s11 应该是这个
    "UNSAFE ACTS—Known Deviations",  # s12 应该是这个
    "ORGANIZATIONAL INFLUENCES—Policy/Procedures/Process",  # s13 应该是这个
    "SUPERVISION/LEADERSHIP—Ineffective Supervision",  # s14 应该是这个
    "ORGANIZATIONAL INFLUENCES—Policy/Procedures/Process",  # s15 应该是这个
    "ORGANIZATIONAL INFLUENCES—Training Program Issues",  # s16 应该是这个
    "ORGANIZATIONAL INFLUENCES—Policy/Procedures/Process",  # s17 应该是这个
    "PRECONDITIONS—Training Conditions"  # s18 应该是这个
]

_CORRECT_LAYERS_FOR_ERRORS = [
    "SUPERVISION/LEADERSHIP",  # s11
    "UNSAFE ACTS",  # s12
    "ORGANIZATIONAL INFLUENCES",  # s13
    "SUPERVISION/LEADERSHIP",  # s14
    "ORGANIZATIONAL INFLUENCES",  # s15
    "ORGANIZATIONAL INFLUENCES",  # s16
    "ORGANIZATIONAL INFLUENCES",  # s17
    "PRECONDITIONS"  # s18
]

_ASSIST_EVALS = []
for i in range(1, 19):
    sid = f"s{i}"
    correct = 1 if i <= 10 else 0  # 前10正确，后8错误
    layer_correct = 1 if i <= 10 else 0
    
    if correct:
        cat_reason = "Sentence content aligns with assigned category"
        layer_reason = "Layer correctly matches the category"
        final_category = _EXAMPLE_CATEGORIES[i-1]
        final_layer = _EXAMPLE_LAYERS[i-1]
    else:
        cat_reason = "Sentence content does not support assigned category"
        layer_reason = "Layer assignment is incorrect"
        # 对于错误的示例，使用正确的分类
        final_category = _CORRECT_CATEGORIES_FOR_ERRORS[i-11]
        final_layer = _CORRECT_LAYERS_FOR_ERRORS[i-11]
        
    _ASSIST_EVALS.append({
        "sentence_id": sid,
        "category_is_correct": correct,
        "category_evaluation_reason": cat_reason,
        "layer_is_correct": layer_correct,
        "layer_evaluation_reason": layer_reason,
        "final_category": final_category,
        "final_layer": final_layer
    })

# 组装few-shot消息列表
EVALUATION_FEW_SHOT = [
    {"role": "user", "content": _FEW_SHOT_USER_CONTENT},
    {
        "role": "assistant",
        "content": None,
        "function_call": {
            "name": "evaluate_hfacs_classification",
            "arguments": json.dumps({"evaluations": _ASSIST_EVALS})
        }
    }
]

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        
    def chat_completion(self, model: str, messages: list, temperature: float = 0.1,
                        max_tokens: int = 4000, force_json: bool = True):
        """调用Ollama API进行聊天补全"""
        url = f"{self.base_url}/api/chat"
        
        data = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                # ✅ Ollama 官方支持 format=json，用于禁止额外说明文字
                **({"format": "json"} if force_json else {})
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=300)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API调用失败: {str(e)}")

def test_ollama_connection(ollama_client: OllamaClient, model: str) -> bool:
    """测试Ollama连接"""
    try:
        response = ollama_client.chat_completion(
            model=model,
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.1,
            max_tokens=10
        )
        return response and 'message' in response
    except Exception:
        return False

def load_classification_results(json_file: str) -> Dict[str, List[Dict]]:
    """加载分类结果JSON文件"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"加载分类结果文件失败: {str(e)}")

def extract_classification_items(classification_data: Dict[str, List[Dict]]) -> List[Dict]:
    """从分类结果中提取所有分类条目"""
    items = []
    for category, predictions in classification_data.items():
        # 处理所有分类，通过前缀匹配推断层级
        layer = "Unknown"
        for hfacs_layer in HFACS_LAYERS:
            if category.startswith(hfacs_layer):
                layer = hfacs_layer
                break
        
        # 如果是标准分类，使用映射表
        if category in CATEGORY_TO_LAYER:
            layer = CATEGORY_TO_LAYER[category]
            
        for pred in predictions:
            items.append({
                'sentence_id': f"s{pred.get('index', -1)}",
                'index': pred.get('index', -1),
                'text': pred.get('text', ''),
                'category': category,
                'layer': layer,
                'reason': pred.get('reason', '')
            })
    return items

def chunk(lst, size):
    """将列表分块"""
    for i in range(0, len(lst), size):
        yield lst[i : i + size]

def evaluate_with_openai(items: List[Dict], batch_size: int, model: str, client: OpenAI, temperature: float = 0.1, enable_few_shot: bool = True) -> List[Dict]:
    """使用OpenAI进行HFACS分类评估"""
    evaluations = []
    
    for batch_idx, batch in enumerate(tqdm(list(chunk(items, batch_size)), desc="OpenAI-evaluating")):
        # 构建评估内容
        evaluation_content = "Evaluate these HFACS classifications:\n\n"
        for item in batch:
            evaluation_content += f"ID: {item['sentence_id']}\n"
            evaluation_content += f"Text: \"{item['text']}\"\n"
            evaluation_content += f"Assigned Category: {item['category']}\n"
            evaluation_content += f"Assigned Layer: {item['layer']}\n"
            evaluation_content += f"Original Reason: \"{item['reason']}\"\n\n"
        
        # 构建消息
        messages = [{"role": "system", "content": EVALUATION_SYSTEM_PROMPT}]
        
        # 根据开关决定是否添加few-shot示例
        if enable_few_shot:
            messages.extend(EVALUATION_FEW_SHOT)
        
        # 添加当前评估任务
        messages.append({"role": "user", "content": evaluation_content})
        
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                functions=[EVALUATION_FUNCTION_SCHEMA],
                function_call={"name": "evaluate_hfacs_classification"},
                temperature=temperature
            )
            
            msg = resp.choices[0].message
            if msg.function_call:
                result = json.loads(msg.function_call.arguments)
                batch_evaluations = result.get("evaluations", [])
                
                # 将评估结果与原始条目合并
                for eval_result in batch_evaluations:
                    sentence_id = eval_result["sentence_id"]
                    # 查找对应的原始条目
                    original_item = next((item for item in batch if item['sentence_id'] == sentence_id), None)
                    if original_item:
                        evaluation = {
                            'source_file': '',  # 在调用者处设置
                            'index': original_item['index'],
                            'sentence_text': original_item['text'],
                            'assigned_category': original_item['category'],
                            'assigned_layer': original_item['layer'],
                            'original_reason': original_item['reason'],
                            'category_is_correct': eval_result['category_is_correct'],
                            'category_evaluation_reason': eval_result['category_evaluation_reason'],
                            'layer_is_correct': eval_result['layer_is_correct'],
                            'layer_evaluation_reason': eval_result['layer_evaluation_reason'],
                            'final_category': eval_result.get('final_category', ''),
                            'final_layer': eval_result.get('final_layer', ''),
                            'evaluation_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'evaluator': f'GT_Auto_{model}'
                        }
                        evaluations.append(evaluation)
        
        except Exception as e:
            print(f"  ❌ 批次 {batch_idx+1}: 处理时出错: {e}")
            # 为当前批次的所有条目创建错误记录
            for item in batch:
                evaluation = {
                    'source_file': '',
                    'index': item['index'],
                    'sentence_text': item['text'],
                    'assigned_category': item['category'],
                    'assigned_layer': item['layer'],
                    'original_reason': item['reason'],
                    'category_is_correct': -1,
                    'category_evaluation_reason': f"Processing error: {str(e)}",
                    'layer_is_correct': -1,
                    'layer_evaluation_reason': f"Processing error: {str(e)}",
                    'final_category': '',
                    'final_layer': '',
                    'evaluation_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'evaluator': f'GT_Auto_{model}'
                }
                evaluations.append(evaluation)
    
    return evaluations

def _extract_json_from_content(content: str) -> str | None:
    """增强版JSON提取函数 - 从LLM返回的content中提取JSON字符串"""
    if not content or not isinstance(content, str):
        return None
    
    content = content.strip()
    
    # 策略1: 直接尝试解析（最严格）
    if content.startswith("{") and content.endswith("}"):
        try:
            json.loads(content)
            return content
        except:
            pass
    
    # 策略2: 去除代码块包装
    if "```" in content:
        # 匹配 ```json ... ``` 或 ``` ... ```
        code_blocks = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.S | re.I)
        for block in code_blocks:
            try:
                json.loads(block)
                return block
            except:
                continue
    
    # 策略3: 查找 Function Call 格式
    # 匹配 "Arguments: { ... }" 或 "Arguments: { ... }" 等变体
    function_patterns = [
        r"Arguments\s*:?\s*(\{.*\})",  # 使用贪婪匹配，确保获取完整JSON
        r"Function\s*Call\s*:?\s*.*?Arguments\s*:?\s*(\{.*\})",  # 使用贪婪匹配
        r"function\s*:?\s*.*?arguments\s*:?\s*(\{.*\})",  # 使用贪婪匹配
    ]
    
    for pattern in function_patterns:
        matches = re.findall(pattern, content, re.S | re.I)
        for match in matches:
            try:
                json.loads(match)
                return match
            except:
                continue
    
    # 策略4: 查找包含 "evaluations" 键的JSON对象
    # 这是最关键的策略，因为我们要找的就是包含evaluations数组的JSON
    evaluation_patterns = [
        r"(\{[^{}]*\"evaluations\"[^{}]*\})",  # 简单匹配
        r"(\{[^{}]*\"evaluations\"[^{}]*\[[^\]]*\][^{}]*\})",  # 包含数组
    ]
    
    for pattern in evaluation_patterns:
        matches = re.findall(pattern, content, re.S)
        for match in matches:
            try:
                # 尝试扩展匹配到完整的JSON对象
                # 从match开始，向前后扩展，找到完整的JSON
                start_pos = content.find(match)
                if start_pos != -1:
                    # 向前找 { 的开始
                    brace_count = 0
                    start_idx = start_pos
                    for i in range(start_pos, -1, -1):
                        if content[i] == "}":
                            brace_count += 1
                        elif content[i] == "{":
                            brace_count -= 1
                            if brace_count == 0:
                                start_idx = i
                                break
                    
                    # 向后找 } 的结束
                    brace_count = 0
                    end_idx = start_pos + len(match)
                    for i in range(start_pos + len(match), len(content)):
                        if content[i] == "{":
                            brace_count += 1
                        elif content[i] == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i + 1
                                break
                    
                    full_json = content[start_idx:end_idx]
                    try:
                        json.loads(full_json)
                        return full_json
                    except:
                        pass
            except:
                continue
    
    # 策略5: 智能提取最外层JSON对象
    # 使用更智能的括号匹配
    try:
        # 找到第一个 { 的位置
        start_pos = content.find("{")
        if start_pos == -1:
            return None
        
        # 从第一个 { 开始，计算括号匹配
        brace_count = 0
        end_pos = -1
        
        for i in range(start_pos, len(content)):
            if content[i] == "{":
                brace_count += 1
            elif content[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i + 1
                    break
        
        if end_pos > start_pos:
            json_str = content[start_pos:end_pos]
            try:
                json.loads(json_str)
                return json_str
            except:
                pass
    except:
        pass
    
    # 策略6: 最后尝试 - 查找任何看起来像JSON的内容
    # 匹配包含常见键的JSON片段
    json_like_patterns = [
        r"(\{[^{}]*\"sentence_id\"[^{}]*\})",
        r"(\{[^{}]*\"category_is_correct\"[^{}]*\})",
        r"(\{[^{}]*\"layer_is_correct\"[^{}]*\})",
    ]
    
    for pattern in json_like_patterns:
        matches = re.findall(pattern, content, re.S)
        for match in matches:
            try:
                # 尝试扩展为完整JSON
                start_pos = content.find(match)
                if start_pos != -1:
                    # 简单的括号匹配扩展
                    brace_count = 0
                    start_idx = start_pos
                    for i in range(start_pos, -1, -1):
                        if content[i] == "}":
                            brace_count += 1
                        elif content[i] == "{":
                            brace_count -= 1
                            if brace_count == 0:
                                start_idx = i
                                break
                    
                    brace_count = 0
                    end_idx = start_pos + len(match)
                    for i in range(start_pos + len(match), len(content)):
                        if content[i] == "{":
                            brace_count += 1
                        elif content[i] == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i + 1
                                break
                    
                    full_json = content[start_idx:end_idx]
                    try:
                        json.loads(full_json)
                        return full_json
                    except:
                        pass
            except:
                continue
    
    return None

def evaluate_with_ollama(items: List[Dict], batch_size: int, model: str, ollama_client: OllamaClient, temperature: float = 0.1, enable_few_shot: bool = True) -> List[Dict]:
    """使用Ollama进行HFACS分类评估"""
    evaluations = []
    
    for batch_idx, batch in enumerate(tqdm(list(chunk(items, batch_size)), desc="Ollama-evaluating")):
        # 构建评估内容
        evaluation_content = "Evaluate these HFACS classifications:\n\n"
        for item in batch:
            evaluation_content += f"ID: {item['sentence_id']}\n"
            evaluation_content += f"Text: \"{item['text']}\"\n"
            evaluation_content += f"Assigned Category: {item['category']}\n"
            evaluation_content += f"Assigned Layer: {item['layer']}\n"
            evaluation_content += f"Original Reason: \"{item['reason']}\"\n\n"
        
        # 构建消息
        messages = [{"role": "system", "content": EVALUATION_SYSTEM_PROMPT}]
        
        # 根据开关决定是否添加few-shot示例
        if enable_few_shot:
            messages.extend(EVALUATION_FEW_SHOT)
        
        # 添加当前评估任务
        messages.append({"role": "user", "content": evaluation_content})
        
        # 为本地LLM添加格式指导
        format_instruction = {
            "role": "user",
            "content": """Please respond with a function call format like this:

**Function Call:**
Function: evaluate_hfacs_classification
Arguments: {"evaluations": [your_evaluation_results_array]}

Where each evaluation result should have:
- sentence_id: the ID from input
- category_is_correct: 1 (correct), 0 (incorrect), or -1 (skip)
- category_evaluation_reason: brief reason for category evaluation
- layer_is_correct: 1 (correct), 0 (incorrect), or -1 (skip)  
- layer_evaluation_reason: brief reason for layer evaluation
- final_category: final HFACS category (if correct=1, use original; if 0, select correct one from 18 categories; if -1, use empty string)
- final_layer: final HFACS layer (if correct=1, use original; if 0, select correct one from 4 layers; if -1, use empty string)"""
        }
        messages.append(format_instruction)
        
        try:
            # ⚠️ 不使用 format=json，以保留 function call 格式
            response = ollama_client.chat_completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=4000,
                force_json=False
            )

            content: str = response.get("message", {}).get("content", "")

            # 解析步骤 ①：直接尝试 JSON.loads
            evaluations_data = []
            if content.strip().startswith("{"):
                try:
                    evaluations_data = json.loads(content).get("evaluations", [])
                except Exception:
                    evaluations_data = []

            # 解析步骤 ②：辅助函数提取JSON
            if not evaluations_data:
                json_block = _extract_json_from_content(content)
                if json_block:
                    try:
                        evaluations_data = json.loads(json_block).get("evaluations", [])
                    except Exception:
                        evaluations_data = []
            
            if evaluations_data and isinstance(evaluations_data, list):
                # 将评估结果与原始条目合并
                for eval_result in evaluations_data:
                    if not isinstance(eval_result, dict):
                        continue
                            
                    sentence_id = eval_result.get("sentence_id", "")
                    # 查找对应的原始条目
                    original_item = next((item for item in batch if item['sentence_id'] == sentence_id), None)
                    if original_item:
                        evaluation = {
                            'source_file': '',
                            'index': original_item['index'],
                            'sentence_text': original_item['text'],
                            'assigned_category': original_item['category'],
                            'assigned_layer': original_item['layer'],
                            'original_reason': original_item['reason'],
                            'category_is_correct': eval_result.get('category_is_correct', -1),
                            'category_evaluation_reason': eval_result.get('category_evaluation_reason', ''),
                            'layer_is_correct': eval_result.get('layer_is_correct', -1),
                            'layer_evaluation_reason': eval_result.get('layer_evaluation_reason', ''),
                            'final_category': eval_result.get('final_category', ''),
                            'final_layer': eval_result.get('final_layer', ''),
                            'evaluation_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'evaluator': f'GT_Auto_{model}'
                        }
                        evaluations.append(evaluation)
            else:
                raise ValueError("无法解析有效的evaluations数组")
                    
        except Exception as e:
            print(f"  ❌ 批次 {batch_idx+1}: 处理时出错: {e}")
            
            # 增强调试信息：显示原始响应的前200字符
            if 'content' in locals():
                debug_content = content[:200] + "..." if len(content) > 200 else content
                print(f"  🔍 原始响应预览: {debug_content}")
            
            # 为当前批次的所有条目创建错误记录
            for item in batch:
                evaluation = {
                    'source_file': '',
                    'index': item['index'],
                    'sentence_text': item['text'],
                    'assigned_category': item['category'],
                    'assigned_layer': item['layer'],
                    'original_reason': item['reason'],
                    'category_is_correct': -1,
                    'category_evaluation_reason': f"Processing error: {str(e)}",
                    'layer_is_correct': -1,
                    'layer_evaluation_reason': f"Processing error: {str(e)}",
                    'final_category': '',
                    'final_layer': '',
                    'evaluation_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'evaluator': f'GT_Auto_{model}'
                }
                evaluations.append(evaluation)
    
    return evaluations

def find_json_files(input_path: str, file_pattern: str = "*_classified_results_*.json") -> List[str]:
    """查找输入路径中符合模式的JSON文件"""
    if os.path.isfile(input_path):
        return [input_path]
    elif os.path.isdir(input_path):
        json_files = []
        patterns = [file_pattern, f"**/{file_pattern}"]
        for pattern in patterns:
            json_files.extend(glob.glob(os.path.join(input_path, pattern), recursive=True))
        
        if not json_files and file_pattern != "*.json":
            print(f"⚠️ 未找到符合模式 '{file_pattern}' 的文件，尝试查找所有JSON文件...")
            fallback_patterns = ['*.json', '**/*.json']
            for pattern in fallback_patterns:
                json_files.extend(glob.glob(os.path.join(input_path, pattern), recursive=True))
        
        return sorted(json_files)
    else:
        raise ValueError(f"输入路径不存在: {input_path}")

def process_single_json(json_file: str, batch_size: int, model: str, client, temperature: float, output_dir: str = None, enable_few_shot: bool = True, model_type: str = "openai") -> Dict[str, Any]:
    """处理单个JSON文件进行自动评估"""
    try:
        # 加载分类结果
        classification_data = load_classification_results(json_file)
        items = extract_classification_items(classification_data)
        
        if not items:
            print(f"⚠️ 文件中没有找到有效的分类条目: {json_file}")
            return {
                'input_file': json_file,
                'error': '没有找到有效的分类条目',
                'model': model,
                'model_type': model_type,
                'enable_few_shot': enable_few_shot
            }
        
        # 确定输出路径
        model_name = model.replace(':', '_').replace('/', '_')
        base_name = os.path.basename(json_file)
        if base_name.endswith('.json'):
            base_name = base_name.replace('.json', '')
        
        output_filename = f"{base_name}_gt_evaluation_{model_name}.csv"
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, output_filename)
        else:
            input_dir = os.path.dirname(json_file)
            output_file = os.path.join(input_dir, output_filename)
        
        # 检查是否已处理
        if os.path.exists(output_file):
            print(f"⏭️ 跳过已处理的文件: {json_file}")
            return {
                'input_file': json_file,
                'output_file': output_file,
                'skipped': True,
                'reason': '文件已存在',
                'model': model,
                'model_type': model_type,
                'enable_few_shot': enable_few_shot
            }
        
        print(f"🤖 使用 {model} 评估中...")
        
        # 进行评估
        if model_type == "openai":
            evaluations = evaluate_with_openai(items, batch_size, model, client, temperature, enable_few_shot)
        elif model_type == "ollama":
            evaluations = evaluate_with_ollama(items, batch_size, model, client, temperature, enable_few_shot)
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        # 设置源文件信息
        source_file = os.path.basename(json_file)
        for eval_item in evaluations:
            eval_item['source_file'] = source_file
        
        # 保存结果为CSV
        df = pd.DataFrame(evaluations)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        # 生成统计报告
        generate_summary_report(evaluations, output_file, model)
        
        # 统计信息
        total_evaluations = len(evaluations)
        category_correct = len([e for e in evaluations if e.get('category_is_correct') == 1])
        category_incorrect = len([e for e in evaluations if e.get('category_is_correct') == 0])
        layer_correct = len([e for e in evaluations if e.get('layer_is_correct') == 1])
        layer_incorrect = len([e for e in evaluations if e.get('layer_is_correct') == 0])
        
        print(f"✅ 评估完成: {total_evaluations} 个条目")
        print(f"💾 结果已保存到: {output_file}")
        print(f"📊 类别评估: {category_correct}正确, {category_incorrect}错误")
        print(f"📊 层级评估: {layer_correct}正确, {layer_incorrect}错误")
        
        return {
            'input_file': json_file,
            'output_file': output_file,
            'total_evaluations': total_evaluations,
            'category_correct': category_correct,
            'category_incorrect': category_incorrect,
            'layer_correct': layer_correct,
            'layer_incorrect': layer_incorrect,
            'model': model,
            'model_type': model_type,
            'batch_size': batch_size,
            'enable_few_shot': enable_few_shot
        }
        
    except Exception as e:
        error_msg = f"处理 {json_file} 时出错: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'input_file': json_file,
            'error': error_msg,
            'model': model,
            'model_type': model_type,
            'enable_few_shot': enable_few_shot
        }

def generate_summary_report(evaluations: List[Dict], csv_path: str, model: str):
    """生成汇总报告"""
    if not evaluations:
        return
    
    # 统计结果
    total = len(evaluations)
    category_correct = len([e for e in evaluations if e.get('category_is_correct') == 1])
    category_incorrect = len([e for e in evaluations if e.get('category_is_correct') == 0])
    category_skipped = len([e for e in evaluations if e.get('category_is_correct') == -1])
    
    layer_correct = len([e for e in evaluations if e.get('layer_is_correct') == 1])
    layer_incorrect = len([e for e in evaluations if e.get('layer_is_correct') == 0])
    layer_skipped = len([e for e in evaluations if e.get('layer_is_correct') == -1])
    
    # 计算正确率
    category_valid = total - category_skipped
    layer_valid = total - layer_skipped
    category_accuracy = (category_correct / category_valid * 100) if category_valid > 0 else 0
    layer_accuracy = (layer_correct / layer_valid * 100) if layer_valid > 0 else 0
    
    # 保存汇总报告
    summary_path = csv_path.replace('.csv', '_summary.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"GT_Run_Auto 自动评估汇总报告\n")
        f.write(f"=" * 50 + "\n\n")
        f.write(f"评估时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"评估模型: {model}\n")
        f.write(f"源文件: {evaluations[0].get('source_file', 'Unknown')}\n\n")
        
        f.write(f"总体统计:\n")
        f.write(f"  总条目数: {total}\n\n")
        
        f.write(f"18类别评估:\n")
        f.write(f"  有效评估: {category_valid}\n")
        f.write(f"  正确: {category_correct}\n")
        f.write(f"  错误: {category_incorrect}\n")
        f.write(f"  跳过: {category_skipped}\n")
        f.write(f"  正确率: {category_accuracy:.1f}%\n\n")
        
        f.write(f"4层级评估:\n")
        f.write(f"  有效评估: {layer_valid}\n")
        f.write(f"  正确: {layer_correct}\n")
        f.write(f"  错误: {layer_incorrect}\n")
        f.write(f"  跳过: {layer_skipped}\n")
        f.write(f"  正确率: {layer_accuracy:.1f}%\n")

def create_batch_summary(results: List[Dict[str, Any]], output_dir: str) -> Dict[str, Any]:
    """创建批量处理汇总报告"""
    successful = [r for r in results if 'output_file' in r and 'error' not in r and not r.get('skipped', False)]
    skipped = [r for r in results if r.get('skipped', False)]
    errors = [r for r in results if 'error' in r]
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_files": len(results),
        "successful": len(successful),
        "skipped": len(skipped),
        "errors": len(errors),
        "results": results
    }
    
    # 保存汇总报告
    summary_file = os.path.join(output_dir, "batch_summary_gt_auto.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"📋 汇总报告已保存到: {summary_file}")
    return summary

# 添加Ollama模型列表获取函数
def get_installed_models(ollama_client: OllamaClient) -> List[str]:
    """获取已安装的模型列表"""
    try:
        url = f"{ollama_client.base_url}/api/tags"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        models = []
        for model in data.get("models", []):
            model_name = model.get("name", "")
            if model_name:
                models.append(model_name)
        
        return sorted(models)
        
    except Exception as e:
        print(f"❌ 获取模型列表失败: {e}")
        return []

def main():
    ap = argparse.ArgumentParser(description="GT_Run_Auto - HFACS分类自动化评估器")
    ap.add_argument("input", nargs='?')
    ap.add_argument("--batch", type=int, default=10)
    ap.add_argument("--model", default="gpt-4o-mini")
    ap.add_argument("--model-type", choices=["openai", "ollama"], default="openai")
    ap.add_argument("--ollama-url", default="http://localhost:11434")
    ap.add_argument("--output-dir")
    ap.add_argument("--temperature", type=float, default=0.1)
    ap.add_argument("--file-pattern", default="*_classified_results_*.json")
    ap.add_argument("--list-models", action="store_true", help="列出Ollama已安装模型")
    fewshot_group = ap.add_mutually_exclusive_group()
    fewshot_group.add_argument("--enable-few-shot", dest="enable_few_shot", action="store_true", help="使用few-shot示例 (默认)")
    fewshot_group.add_argument("--disable-few-shot", dest="enable_few_shot", action="store_false", help="不使用few-shot示例")
    ap.set_defaults(enable_few_shot=True)
    args = ap.parse_args()

    # 如果请求列出模型
    if args.list_models:
        if args.model_type != "ollama":
            print("--list-models 仅支持本地Ollama模式 (请加 --model-type ollama)")
            return
        client = OllamaClient(args.ollama_url)
        models = get_installed_models(client)
        if models:
            print("📋 已安装的Ollama模型:")
            for i, model in enumerate(models, 1):
                print(f"  {i}. {model}")
        else:
            print("❌ 未找到已安装的Ollama模型")
        return

    # 根据模型类型设置客户端
    if args.model_type == "openai":
        # 设置OpenAI API Key
        if not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = "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"
        
        client = OpenAI()
        print(f"🤖 使用OpenAI模型: {args.model}")
    else:
        client = OllamaClient(args.ollama_url)
        print(f"🔍 测试Ollama连接: {args.ollama_url}")
        if not test_ollama_connection(client, args.model):
            sys.exit("❌ 无法连接到Ollama或模型不可用")
        print(f"🤖 使用本地模型: {args.model}")

    # 检查是否提供了输入文件
    if not args.input:
        print("❌ 请提供输入文件或目录路径")
        print("使用 --help 查看帮助信息")
        return

    # 查找所有JSON文件
    json_files = find_json_files(args.input, args.file_pattern)
    
    if not json_files:
        sys.exit(f"❌ 未找到匹配的JSON文件: {args.input}")
    
    print(f"🔍 找到 {len(json_files)} 个 JSON 文件")
    for i, json_file in enumerate(json_files, 1):
        print(f"  {i}. {json_file}")
    
    # 确认是否继续
    if len(json_files) > 1:
        response = input(f"\n是否继续处理这 {len(json_files)} 个文件? (y/N): ")
        if response.lower() not in ['y', 'yes', '是']:
            print("取消处理")
            return
    
    # 批量处理
    results = []
    for i, json_file in enumerate(json_files, 1):
        print(f"\n📁 处理文件 {i}/{len(json_files)}: {os.path.basename(json_file)}")
        result = process_single_json(json_file, args.batch, args.model, client, args.temperature, args.output_dir, args.enable_few_shot, args.model_type)
        results.append(result)
    
    # 创建汇总报告
    if len(json_files) > 1:
        output_dir = args.output_dir or "batch_results_gt_auto"
        os.makedirs(output_dir, exist_ok=True)
        summary = create_batch_summary(results, output_dir)
        
        print(f"\n🎉 批量评估完成!")
        print(f"✅ 成功: {summary['successful']}")
        print(f"⏭️  跳过: {summary['skipped']}")
        print(f"❌ 错误: {summary['errors']}")
    else:
        print(f"\n🎉 评估完成!")

if __name__ == "__main__":
    main() 