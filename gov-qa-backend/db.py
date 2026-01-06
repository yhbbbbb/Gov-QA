import sqlite3
from config import DATABASE_PATH  # 从配置文件导入数据库路径


def get_db_connection():
    """创建并返回数据库连接（复用连接，避免重复创建）"""
    conn = sqlite3.connect(DATABASE_PATH)
    # 设置行工厂，使查询结果可通过字典形式访问（如row['question']）
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库：创建政务知识库表，插入测试数据（首次启动自动执行）"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 创建政务知识库表（存储官方政策问答）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gov_knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL UNIQUE,  -- 问题（唯一，避免重复）
            answer TEXT NOT NULL,           -- 官方回答
            source TEXT NOT NULL,           -- 政策来源（如：XX市政务服务中心官网）
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 创建时间
        )
    ''')

    # 新增：上传文件表（存储文件信息和提取的文本）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gov_upload_files (
            file_id TEXT PRIMARY KEY,  -- 唯一文件标识
            file_name TEXT NOT NULL,   -- 原始文件名
            file_path TEXT NOT NULL,   -- 本地存储路径
            text_content TEXT NOT NULL,-- 提取的文本内容（JSON格式）
            position_info TEXT NOT NULL,-- 位置信息（JSON格式）
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_valid BOOLEAN DEFAULT 1 -- 是否有效（1=有效，0=已删除）
        )
    ''')

    # 插入测试数据（政务高频问题示例，可根据实际需求修改）
    test_data = [
        (
            "社保断缴影响购房吗？",
            "根据本市购房资格政策，社保断缴后需重新累计缴费年限：1. 非本地户籍居民购房需连续缴纳社保满24个月（断缴不超过3个月可补缴，超过则重新累计）；2. 本地户籍居民购房无社保连续缴纳要求。具体以最新购房政策为准。",
            "XX市住房和城乡建设局官网"
        ),
        (
            "个人如何办理社保卡？",
            "个人办理社保卡流程：1. 携带身份证原件到就近政务服务中心或银行网点申请；2. 填写《社保卡申领登记表》；3. 采集人像和指纹信息；4. 等待制卡（一般7-15个工作日）；5. 领卡后激活金融功能和社保功能。可通过政务服务APP预约办理，减少排队时间。",
            "XX市人力资源和社会保障局官网"
        ),
        (
            "营业执照办理需要哪些材料？",
            "个体工商户营业执照办理材料：1. 经营者身份证原件及复印件；2. 经营场所证明（租赁合同或房产证明）；3. 经营范围说明；4. 申请书（可在政务服务中心领取或网上下载）。企业营业执照需额外提供公司章程、股东身份证明等材料。",
            "XX市市场监督管理局官网"
        )
    ]

    # 批量插入测试数据（忽略已存在的数据，避免重复插入报错）
    try:
        cursor.executemany('''
            INSERT OR IGNORE INTO gov_knowledge (question, answer, source)
            VALUES (?, ?, ?)
        ''', test_data)
        conn.commit()
        print("数据库初始化成功，已插入测试政务知识")
    except Exception as e:
        print(f"数据库初始化数据插入失败：{e}")
        conn.rollback()
    finally:
        conn.close()


# db.py 优化后的 search_knowledge 函数（覆盖原有函数）
def search_knowledge(question):
    """搜索知识库：优化关键词匹配逻辑，提升匹配成功率"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 优化：拆分问题关键词，进行多关键词匹配（提升精准度）
    # 示例：将"社保断缴影响购房吗？"拆分为["社保","断缴","购房"]
    keywords = question.replace("？", "").replace("?", "").split()
    # 构造多关键词匹配查询（所有关键词都包含在问题或回答中）
    query_conditions = " AND ".join([f"(question LIKE ? OR answer LIKE ?)" for _ in keywords])
    # 构造查询参数（每个关键词对应两个占位符：question和answer）
    query_params = []
    for keyword in keywords:
        query_params.extend([f"%{keyword}%", f"%{keyword}%"])

    # 执行多关键词匹配查询
    if keywords:
        cursor.execute(f'''
            SELECT question, answer, source FROM gov_knowledge
            WHERE {query_conditions}
            LIMIT 1  -- 只返回最匹配的一条知识
        ''', tuple(query_params))
    else:
        # 若问题无有效关键词，返回None
        cursor.execute('''
            SELECT question, answer, source FROM gov_knowledge
            LIMIT 0
        ''')

    result = cursor.fetchone()
    conn.close()

    # 转换为字典返回
    if result:
        return {
            'question': result['question'],
            'answer': result['answer'],
            'source': result['source']
        }
    return None  # 无匹配知识时返回None


def insert_upload_file(file_id, file_name, file_path, text_info):
    """插入上传文件信息到数据库"""
    # 转换文本信息为JSON字符串存储
    import json
    text_content = json.dumps([item['content'] for item in text_info], ensure_ascii=False)
    position_info = json.dumps([item['position'] for item in text_info], ensure_ascii=False)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO gov_upload_files 
            (file_id, file_name, file_path, text_content, position_info)
            VALUES (?, ?, ?, ?, ?)
        ''', (file_id, file_name, file_path, text_content, position_info))
        conn.commit()
        return True
    except Exception as e:
        print(f"插入上传文件信息失败：{e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_upload_file_text(file_id):
    """根据file_id获取上传文件的文本内容和位置信息"""
    import json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT file_name, text_content, position_info 
        FROM gov_upload_files 
        WHERE file_id = ? AND is_valid = 1
    ''', (file_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        # 解析JSON字符串
        text_content = json.loads(result['text_content'])
        position_info = json.loads(result['position_info'])
        # 重组为（内容+位置）的列表
        text_info = [
            {'content': content, 'position': position}
            for content, position in zip(text_content, position_info)
        ]
        return {
            'file_name': result['file_name'],
            'text_info': text_info
        }
    return None


def delete_upload_file(file_id):
    """逻辑删除上传文件（设置is_valid=0）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE gov_upload_files 
            SET is_valid = 0 
            WHERE file_id = ?
        ''', (file_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"删除上传文件失败：{e}")
        conn.rollback()
        return False