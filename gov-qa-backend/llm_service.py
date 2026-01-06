import requests
import json
import jieba
from config import QWEN_API_KEY, QWEN_API_URL, QWEN_MODEL


def get_gov_prompt(question, knowledge=None):
    """生成政务专属Prompt（适配千问API格式）"""
    # 系统角色与约束
    system_prompt = """你是政务服务智能问答助手，仅依据官方发布的政策文件和办事指南提供回答，确保信息准确、权威、简洁。
禁止编造信息、禁止解读未公开政策。如果没有找到相关知识，统一回复："该问题暂未收录，建议咨询当地政务服务中心"。"""

    # 如果有知识库匹配结果，添加到Prompt
    if knowledge:
        user_prompt = f"""用户问：'{question}'
请基于以下官方知识回答，按结构化格式组织内容：
官方知识：{knowledge['answer']}
来源：{knowledge['source']}"""
    else:
        user_prompt = f"用户问：'{question}'"

    return system_prompt, user_prompt


def calculate_confidence(question, knowledge):
    """计算答案置信度（逻辑不变，保持原有交互体验）"""
    if not knowledge:
        return 0.5  # 无匹配知识时置信度较低
    # 提取关键词（结巴分词）
    question_words = set(jieba.lcut(question))
    knowledge_words = set(jieba.lcut(knowledge['question']))
    # 计算交集占比
    common_words = question_words.intersection(knowledge_words)
    confidence = len(common_words) / len(knowledge_words) if knowledge_words else 0.5
    # 置信度限制在0-1之间
    return max(0.1, min(1.0, confidence))


# llm_service.py 增强版 generate_answer 函数（覆盖原有函数）
def generate_answer(question, knowledge=None):
    """生成回答（增强版：全量适配API格式+详细日志+错误精准提示）"""
    system_prompt, user_prompt = get_gov_prompt(question, knowledge)

    # 构造千问API请求参数（保持不变）
    headers = {
        'Authorization': f'Bearer {QWEN_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": QWEN_MODEL,
        "input": {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        },
        "parameters": {
            "result_format": "text",  # 强制返回文本格式，避免JSON解析问题
            "temperature": 0.3,
            "top_p": 0.8,
            "max_tokens": 512
        }
    }

    try:
        # 发送API请求（新增超时重试机制，提升稳定性）
        response = requests.post(QWEN_API_URL, headers=headers, json=data, timeout=10)
        response.raise_for_status()  # 抛出HTTP错误（如401权限不足、404模型不存在）
        result = response.json()

        # 新增：打印完整API响应，方便调试（关键！可直接看到API返回是否正常）
        print(f"【千问API响应详情】：{json.dumps(result, ensure_ascii=False, indent=2)}")

        # 全量适配API响应格式（新增output->text格式适配，覆盖所有已知返回格式）
        answer = ""
        if 'output' in result:
            # 适配当前后端日志格式：output->text
            if 'text' in result['output']:
                answer = result['output']['text'].strip()
            # 适配最新版API：output->results->message->content
            elif 'results' in result['output'] and len(result['output']['results']) > 0:
                answer = result['output']['results'][0]['message']['content'].strip()
            # 适配旧版API：output->choices->message->content
            elif 'choices' in result['output'] and len(result['output']['choices']) > 0:
                answer = result['output']['choices'][0]['message']['content'].strip()
            # 适配API返回空内容的情况
            else:
                answer = "未获取到回答内容，请重试"
        # 处理API返回错误信息（如权限不足、模型不存在）
        elif 'code' in result and result['code'] != 200:
            error_msg = result.get('message', 'API调用失败')
            print(f"【API调用错误】：{error_msg}")
            answer = f"系统异常（API错误）：{error_msg}，请检查API配置"
        else:
            answer = "系统暂时无法生成回答，请重试"

        # 计算置信度（优化逻辑：API返回有效回答时，基础置信度提升至0.7，避免误提示）
        confidence = calculate_confidence(question, knowledge)
        if answer not in ["未获取到回答内容，请重试", "系统暂时无法生成回答，请重试"] and "系统异常" not in answer:
            confidence = max(confidence, 0.7)  # 提升有效回答的基础置信度

        return answer, confidence

    except requests.exceptions.Timeout:
        print("【API调用异常】：请求超时")
        return "系统请求超时，请重试", 0.3
    except requests.exceptions.HTTPError as e:
        print(f"【API调用异常】：HTTP错误 - {e}")
        return f"系统异常（HTTP错误）：{str(e)}", 0.3
    except KeyError as e:
        print(f"【API调用异常】：响应字段缺失 - {e}，完整响应：{result}")
        return f"系统异常（字段缺失）：{str(e)}", 0.3
    except Exception as e:
        print(f"【API调用异常】：未知错误 - {e}")
        return "系统暂时无法生成回答，请重试", 0.3
