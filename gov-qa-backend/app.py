from flask import Flask
from flask_cors import CORS  # 解决跨域问题
from api.qa_api import qa_bp
from config import API_HOST, API_PORT
import db  # 初始化数据库

# 创建Flask应用
app = Flask(__name__)

# 允许跨域（前端本地运行地址）
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080"}})

# 注册API蓝图
app.register_blueprint(qa_bp, url_prefix='/api')

if __name__ == '__main__':
    # 本地运行Flask服务
    print(f"后端服务启动成功，地址：http://{API_HOST}:{API_PORT}")
    app.run(host=API_HOST, port=API_PORT, debug=True)  # debug模式便于本地调试