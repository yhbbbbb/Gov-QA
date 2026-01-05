import sqlite3
from config import DATABASE_PATH

def get_db_connection():
    """创建并返回数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # 使查询结果可通过列名访问
    return conn

def init_db():
    """初始化数据库（创建知识库表、交互日志表）"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. 政务知识库表（存储标准化问答）- 替换#注释为--注释（SQLite兼容）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gov_knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT NOT NULL,  -- 政务领域（如社保、公积金、企业登记）
        business_type TEXT NOT NULL,  -- 业务类型（如养老保险、提取业务）
        question TEXT NOT NULL UNIQUE,  -- 标准问题
        answer TEXT NOT NULL,  -- 标准回答
        policy_basis TEXT,  -- 政策依据
        process TEXT,  -- 办事流程
        source TEXT NOT NULL,  -- 来源（如XX市政务服务中心）
        update_time TEXT NOT NULL  -- 更新时间
    )
    ''')

    # 2. 交互日志表（存储用户提问与反馈）- 替换#注释为--注释（SQLite兼容）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interaction_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id TEXT NOT NULL UNIQUE,  -- 唯一请求ID
        question TEXT NOT NULL,  -- 用户提问
        user_type TEXT NOT NULL,  -- 用户类型（personal/enterprise）
        source TEXT,  -- 访问来源
        answer TEXT,  -- 系统回答
        confidence REAL,  -- 置信度
        feedback_type TEXT,  -- 反馈类型（useful/useless/null）
        feedback_remark TEXT,  -- 反馈备注
        create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 创建时间
    )
    ''')

    # 插入测试数据（社保、公积金相关高频问题）
    test_data = [
        (
            '社保',
            '灵活就业参保',
            '灵活就业人员如何办理社保参保？',
            '1. 申请条件：年满16周岁、未在用人单位参加社会保险的灵活就业人员；2. 所需材料：身份证原件及复印件、户口本复印件、近期免冠1寸照片；3. 办理渠道：线下政务服务中心窗口或线上政务APP；4. 办理时限：3个工作日内审核完成。',
            '《社会保险法》第10条、《灵活就业人员社会保险参保管理办法》第5条',
            '1. 提交申请材料；2. 工作人员审核；3. 审核通过后办理参保登记；4. 缴纳保费',
            'XX市政务服务中心官方指南（2024年）',
            '2024-01-01'
        ),
        (
            '社保',
            '断缴影响',
            '社保断缴有什么影响？',
            '1. 医保：断缴期间无法享受医保报销，断缴3个月以上视为重新参保，有6个月等待期；2. 养老保险：影响累计缴费年限，可能导致退休后养老金减少；3. 购房/购车资格：部分城市要求连续缴纳社保满一定年限，断缴会重置年限；4. 公积金贷款：部分城市公积金贷款需连续缴纳6个月以上，断缴影响贷款申请。',
            '《社会保险法》第23条、各城市购房资格管理办法',
            '无特定办事流程，建议及时补缴',
            'XX市社保中心官方解读（2024年）',
            '2024-01-01'
        ),
        (
            '公积金',
            '提取条件',
            '公积金提取条件是什么？',
            '常见提取条件：1. 购买、建造、翻建、大修自住住房；2. 偿还购房贷款本息；3. 租赁自住住房（租金超过家庭收入一定比例）；4. 退休；5. 完全丧失劳动能力并与单位终止劳动关系；6. 出国（境）定居。具体以当地最新政策为准。',
            '《住房公积金管理条例》第24条',
            '1. 准备提取材料；2. 向公积金管理中心提交申请；3. 审核；4. 资金到账',
            'XX市公积金管理中心官方指南（2024年）',
            '2024-01-01'
        ),
        (
            '企业登记',
            '营业执照办理',
            '营业执照办理需要哪些材料？',
            '1. 经营者身份证原件及复印件；2. 经营场所证明（租赁合同或房产证明）；3. 经营范围（需符合国家规定）；4. 企业名称预先核准通知书；5. 申请书（可在政务服务网下载）。',
            '《市场主体登记管理条例》第12条',
            '1. 名称预先核准；2. 提交申请材料；3. 审核；4. 领取营业执照',
            'XX市市场监督管理局官方指南（2024年）',
            '2024-01-01'
        )
    ]

    # 批量插入测试数据（忽略已存在的）
    for data in test_data:
        try:
            cursor.execute('''
            INSERT INTO gov_knowledge (domain, business_type, question, answer, policy_basis, process, source, update_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
        except sqlite3.IntegrityError:
            # 问题已存在，跳过
            continue

    conn.commit()
    conn.close()

def query_knowledge(question):
    """根据用户问题查询知识库（模糊匹配）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    # 模糊匹配问题关键词- 替换#注释为--注释（SQLite兼容）
    cursor.execute('''
    SELECT question, answer, source, policy_basis FROM gov_knowledge
    WHERE question LIKE ?
    ''', (f'%{question}%',))
    result = cursor.fetchone()
    conn.close()
    if result:
        # 拼接政策依据到答案
        answer = f"{result['answer']}【政策依据：{result['policy_basis']}】"
        return {
            'question': result['question'],
            'answer': answer,
            'source': result['source']
        }
    return None

def insert_interaction_log(request_id, question, user_type, source, answer, confidence):
    """插入交互日志"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO interaction_log (request_id, question, user_type, source, answer, confidence)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (request_id, question, user_type, source, answer, confidence))
    conn.commit()
    conn.close()

def update_feedback(request_id, feedback_type, feedback_remark):
    """更新反馈信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE interaction_log
    SET feedback_type = ?, feedback_remark = ?
    WHERE request_id = ?
    ''', (feedback_type, feedback_remark, request_id))
    conn.commit()
    conn.close()

# 初始化数据库（程序启动时执行）
init_db()