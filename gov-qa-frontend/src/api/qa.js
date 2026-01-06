import axios from 'axios';

// 创建axios实例，配置基础路径和超时时间
const service = axios.create({
  baseURL: '',
  timeout: 10000 // 请求超时时间（10秒）
});

// 封装问答接口请求函数（供QaComponent.vue调用）
export const requestQa = (question) => {
  return service({
    url: '/api/qa', // 后端问答接口路径（与qa_api.py中定义的一致）
    method: 'POST', // 请求方式
    data: {
      question: question // 传递给后端的参数
    }
  });
};

