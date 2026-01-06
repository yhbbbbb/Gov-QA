<template>
  <div class="qa-container">
    <!-- 合规提示 -->
    <div class="compliance-tip">
      本系统仅提供政务政策咨询参考，具体以官方最新政策为准!
    </div>

    <!-- 问答区域 -->
    <div class="chat-area">
      <div class="message-list" v-for="(msg, index) in messageList" :key="index">
        <div :class="msg.role === 'user' ? 'user-message' : 'assistant-message'">
          {{ msg.content }}
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <el-input
        v-model="inputValue"
        placeholder="请输入政务相关问题（如：社保断缴影响购房吗？）"
        @keyup.enter="sendMessage"
      ></el-input>
      <el-button type="primary" @click="sendMessage" style="margin-left: 10px;">发送</el-button>
      <el-button type="text" @click="switchToManual" style="margin-left: 10px;">人工咨询</el-button>
    </div>

  </div>

</template>

<script setup>
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { requestQa } from '@/api/qa'; // 导入后端接口请求函数

// 响应式数据
const inputValue = ref('');
const messageList = ref([
  { role: 'assistant', content: '您好！请问有什么政务相关问题需要咨询？' }
]);

// 发送问题
const sendMessage = async () => {
  if (!inputValue.value.trim()) {
    ElMessage.warning('请输入问题内容');
    return;
  }
  // 添加用户消息到列表
  messageList.value.push({ role: 'user', content: inputValue.value.trim() });
  const question = inputValue.value.trim();
  inputValue.value = '';

  try {
    // 调用后端问答接口
    const res = await requestQa(question);
    // 添加助手回复到列表
    messageList.value.push({ role: 'assistant', content: res.data.answer });
    // 置信度低于阈值提示人工咨询
    if (res.data.confidence < 0.80) {
      ElMessage.info('当前回答置信度较低，建议咨询人工客服');
    }
  } catch (error) {
    messageList.value.push({ role: 'assistant', content: '系统异常，请重试' });
    ElMessage.error('请求失败');
  }
};

// 切换到人工咨询
const switchToManual = () => {
  window.open('/manual_chat.html', '_blank');
};
</script>

<style scoped>
.qa-container {
  width: 800px;
  margin: 10px auto;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}
.compliance-tip {
  color: #666;
  font-size: 12px;
  margin-bottom: 20px;
  padding: 8px;
  background-color: #f5f5f5;
  border-radius: 4px;
}
.chat-area {
  height: 400px;
  overflow-y: auto;
  margin-bottom: 20px;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 10px;
}
.message-list {
  margin-bottom: 15px;
  clear: both; /* 清除浮动，避免消息重叠 */
}
.user-message {
  text-align: right;
  color: #fff;
  background-color: #1989fa;
  padding: 8px 12px;
  border-radius: 16px;
  display: inline-block;
  max-width: 70%;
  float: right;
}
.assistant-message {
  text-align: left;
  color: #333;
  background-color: #f5f5f5;
  padding: 8px 12px;
  border-radius: 16px;
  display: inline-block;
  max-width: 70%;
  float: left;
}
.input-area {
  display: flex;
  align-items: center;
}
.el-input {
  flex: 1;
}
</style>