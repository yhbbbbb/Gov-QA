import axios from 'axios';

// 创建axios实例，指向本地后端服务
const service = axios.create({
  baseURL: 'http://localhost:5000',  // 本地后端地址
  timeout: 3000,  // 超时时间3秒
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  }
});

// 请求拦截器（可选，用于添加token）
service.interceptors.request.use(
  config => {
    // 本地运行简化，暂不添加复杂认证
    config.headers['Authorization'] = 'Bearer local-test-token';
    return config;
  },
  error => Promise.reject(error)
);

// 响应拦截器（统一处理结果）
service.interceptors.response.use(
  response => response.data,
  error => {
    console.error('请求错误：', error);
    return Promise.reject({ code: 500, message: '请求超时，请重试' });
  }
);

// 核心API接口
export default {
  // 用户提问接口
  queryQa: (params) => service.post('/api/gov/qa/query', params),
  // 答案反馈接口
  feedbackQa: (params) => service.post('/api/gov/qa/feedback', params),
  // 人工转接接口
  transferManual: (params) => service.post('/api/gov/qa/manual', params)
};