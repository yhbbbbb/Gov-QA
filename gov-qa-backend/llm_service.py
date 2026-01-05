import requests
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


def generate_answer(question, knowledge=None):
    """生成回答（核心替换：调用千问API）"""
    system_prompt, user_prompt = get_gov_prompt(question, knowledge)

    # 构造千问API请求参数
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
            "result_format": "text",
            "temperature": 0.3,  # 温度越低越严谨，适合政务问答
            "top_p": 0.8,
            "max_tokens": 512  # 最大生成长度
        }
    }

    try:
        # 发送API请求
        response = requests.post(QWEN_API_URL, headers=headers, json=data, timeout=10)
        response.raise_for_status()  # 抛出HTTP请求异常
        result = response.json()
        answer = result['output']['choices'][0]['message']['content'].strip()

        # 计算置信度
        confidence = calculate_confidence(question, knowledge)
        return answer, confidence

    except requests.exceptions.Timeout:
        print("千问API请求超时")
        return "系统请求超时，请重试", 0.3
    except requests.exceptions.HTTPError as e:
        print(f"千问API请求失败：{e}")
        return "系统异常，请重试", 0.3
    except Exception as e:
        print(f"千问API调用异常：{e}")
        return "系统暂时无法生成回答，请重试", 0.3
