// 导入axios（前端请求工具，已通过npm install安装）
import axios from 'axios';

// 创建axios实例，配置基础路径和超时时间
const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API || 'http://localhost:5000', // 后端服务地址（与后端端口一致）
  timeout: 10000 // 请求超时时间（10秒）
});

// 封装问答接口请求函数（供QaComponent.vue调用）
export const requestQa = (question) => {
  return service({
    url: '/api/qa', // 后端问答接口路径（与qa_api.py中定义的一致）
    method: 'post', // 请求方式（与后端接口一致）
    data: {
      question: question // 传递给后端的参数（问题内容）
    }
  });
};