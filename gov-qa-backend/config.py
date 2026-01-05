# 数据库配置
DATABASE_PATH = 'gov_qa.db'  # SQLite本地数据库文件

# 千问API核心配置
QWEN_API_KEY = 'sk-3071ea1b5617422c9542c88863b58e'  # 替换为你的千问API-KEY
QWEN_API_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'  # 千问API官方地址
QWEN_MODEL = 'qwen-turbo'  # 选用的千问模型（qwen-turbo为轻量版，响应快，适合问答场景）

# API配置
API_PORT = 5000  # 本地运行端口
API_HOST = '0.0.0.0'  # 允许外部访问

# 置信度阈值
CONFIDENCE_THRESHOLD = 0.85

# 人工客服配置
MANUAL_CHAT_URL = 'http://localhost:5000/manual_chat.html'  # 模拟人工聊天页面
