# gov-qa-backend/api/qa_api.py 完整代码（必须存在）
from flask import Blueprint, request, jsonify
from llm_service import generate_answer
from db import search_knowledge, init_db
from config import CONFIDENCE_THRESHOLD

# 创建蓝图（与app.py中注册的蓝图名称一致）
qa_bp = Blueprint('qa', __name__)

# 初始化数据库（首次启动自动创建表和测试数据）
init_db()


# qa_api.py 优化后的 qa 接口函数
@qa_bp.route('/qa', methods=['POST'])
def qa():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        if not question:
            return jsonify({'code': 400, 'msg': '请输入问题内容', 'answer': '', 'confidence': 0})

        # 1. 知识库搜索
        knowledge = search_knowledge(question)
        # 2. 调用千问API生成回答
        answer, confidence = generate_answer(question, knowledge)

        # 核心优化：调整置信度联动逻辑
        msg = 'success'
        # 若回答有效，即使置信度低，也展示回答并提示人工参考
        if answer in ["未获取到回答内容，请重试", "系统暂时无法生成回答，请重试"] or "系统异常" in answer:
            msg = '生成回答失败'
        elif confidence < CONFIDENCE_THRESHOLD:
            # 置信度低但有有效回答：补充提示，而非替换回答
            answer += f"\n\n提示：当前回答置信度较低（{round(confidence, 2)}），若信息不准确，建议咨询人工客服"

        # 3. 返回结果给前端
        return jsonify({
            'code': 200,
            'msg': msg,
            'answer': answer,
            'confidence': round(confidence, 2)
        })
    except Exception as e:
        print(f'接口异常：{e}')
        return jsonify({'code': 500, 'msg': '系统异常', 'answer': '系统异常，请重试', 'confidence': 0})
