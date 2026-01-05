from flask import Blueprint, request, jsonify
from db import query_knowledge, insert_interaction_log, update_feedback
from llm_service import generate_answer
from config import CONFIDENCE_THRESHOLD, MANUAL_CHAT_URL

# 创建Blueprint（接口路由分组）
qa_bp = Blueprint('qa_api', __name__, url_prefix='/api/gov/qa')


@qa_bp.route('/query', methods=['POST'])
def query_qa():
    """用户提问接口"""
    try:
        # 获取请求参数
        data = request.get_json()
        required_params = ['question', 'user_type', 'requestId']
        for param in required_params:
            if param not in data:
                return jsonify({
                    'code': 400,
                    'message': f'缺少参数：{param}',
                    'data': None
                })

        question = data['question']
        user_type = data['user_type']
        request_id = data['requestId']
        source = data.get('source', 'unknown')

        # 1. 查询知识库
        knowledge = query_knowledge(question)

        # 2. 调用大模型生成回答
        answer, confidence = generate_answer(question, knowledge)

        # 3. 补充默认信息（无知识库匹配时）
        if not knowledge:
            source_info = '本地测试知识库'
        else:
            source_info = knowledge['source']

        # 4. 插入交互日志
        insert_interaction_log(request_id, question, user_type, source, answer, confidence)

        # 5. 构建响应（判断是否需要人工转接）
        response_data = {
            'requestId': request_id,
            'answer': answer,
            'confidence': round(confidence, 2),
            'source': source_info
        }
        if confidence < CONFIDENCE_THRESHOLD:
            response_data['manualTransferUrl'] = '/api/gov/qa/manual'

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': response_data
        })
    except Exception as e:
        print(f"查询接口异常：{e}")
        return jsonify({
            'code': 500,
            'message': '系统异常，请重试',
            'data': None
        })


@qa_bp.route('/feedback', methods=['POST'])
def feedback_qa():
    """答案反馈接口"""
    try:
        data = request.get_json()
        required_params = ['requestId', 'feedbackType']
        for param in required_params:
            if param not in data:
                return jsonify({
                    'code': 400,
                    'message': f'缺少参数：{param}',
                    'data': None
                })

        request_id = data['requestId']
        feedback_type = data['feedbackType']
        feedback_remark = data.get('remark', '')

        # 更新反馈信息
        update_feedback(request_id, feedback_type, feedback_remark)

        return jsonify({
            'code': 200,
            'message': '反馈成功',
            'data': None
        })
    except Exception as e:
        print(f"反馈接口异常：{e}")
        return jsonify({
            'code': 500,
            'message': '反馈失败，请重试',
            'data': None
        })


@qa_bp.route('/manual', methods=['POST'])
def transfer_manual():
    """人工转接接口"""
    try:
        data = request.get_json()
        required_params = ['requestId', 'question']
        for param in required_params:
            if param not in data:
                return jsonify({
                    'code': 400,
                    'message': f'缺少参数：{param}',
                    'data': None
                })

        # 本地模拟人工转接（实际应对接真实人工客服系统）
        return jsonify({
            'code': 200,
            'message': '已转接人工客服',
            'data': {
                'manualChatUrl': MANUAL_CHAT_URL,
                'waitTime': '当前等待人数3人，预计等待2分钟（本地测试）'
            }
        })
    except Exception as e:
        print(f"人工转接接口异常：{e}")
        return jsonify({
            'code': 500,
            'message': '转接失败，请重试',
            'data': None
        })


# 模拟人工聊天页面接口（本地测试用）
@qa_bp.route('/manual_chat.html')
def manual_chat_page():
    return '''
    <html>
    <head><title>人工客服聊天（本地模拟）</title></head>
    <body>
        <h1>人工客服聊天窗口（本地测试版）</h1>
        <p>当前为模拟页面，实际应对接政务真实人工客服系统</p>
        <div style="height: 400px; border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;" id="chatContent">
            <p>客服：您好，请问有什么可以帮您？</p>
        </div>
        <input type="text" id="chatInput" style="width: 80%; padding: 5px;" placeholder="请输入消息...">
        <button onclick="sendMessage()">发送</button>
        <script>
            function sendMessage() {
                const input = document.getElementById('chatInput');
                const content = input.value.trim();
                if (!content) return;
                const chatContent = document.getElementById('chatContent');
                chatContent.innerHTML += '<p>我：' + content + '</p>';
                input.value = '';
                // 模拟客服回复
                setTimeout(() => {
                    chatContent.innerHTML += '<p>客服：已收到您的问题，将为您核实后回复</p>';
                }, 1000);
            }
        </script>
    </body>
    </html>
    '''