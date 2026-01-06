<template>
  <div id="app">
    <!-- 页面头部：系统标题和主导航 -->
    <header class="app-header">
      <h1>政务高频问答系统</h1>
      <nav>
        <span class="nav-item active">智能问答</span>
        <span class="nav-item" @click="goToManual">人工咨询</span>
      </nav>
    </header>

    <!-- 新增：政务导航分区（按时政、政务、生活分类） -->
    <section class="gov-nav-area">
      <h2 class="nav-title">政务服务导航</h2>
      <div class="nav-container">
        <!-- 时政板块 -->
        <div class="nav-card">
          <h3 class="card-title">时政资讯</h3>
          <ul class="link-list">
            <li><a href="https://www.gov.cn/zhengce/zuixin.htm" target="_blank">国务院最新政策</a></li>
            <li><a href="https://www.gov.cn/fuwu/zt/zwfwzt.htm" target="_blank">政务服务最新动态</a></li>
            <li><a href="https://www.mca.gov.cn/" target="_blank">民政部政策解读</a></li>
            <li><a href="https://www.mohrss.gov.cn/" target="_blank">人社部最新公告</a></li>
          </ul>
        </div>

        <!-- 政务板块 -->
        <div class="nav-card">
          <h3 class="card-title">政务办理</h3>
          <ul class="link-list">
            <li><a href="https://gjj.mohurd.gov.cn/" target="_blank">全国公积金查询</a></li>
            <li><a href="https://12333.gov.cn/" target="_blank">全国社保公共服务平台</a></li>
            <li><a href="https://pss.mps.gov.cn/" target="_blank">公安政务服务平台</a></li>
            <li><a href="https://etax.chinatax.gov.cn/" target="_blank">电子税务局</a></li>
          </ul>
        </div>

        <!-- 生活板块 -->
        <div class="nav-card">
          <h3 class="card-title">生活服务</h3>
          <ul class="link-list">
            <li><a href="https://www.12306.cn/index/index.html" target="_blank">铁路12306购票</a></li>
            <li><a href="https://gjj.mohurd.gov.cn/" target="_blank">公积金提取指南</a></li>
            <li><a href="https://www.122.gov.cn/" target="_blank">交通违法查询处理</a></li>
            <li><a href="https://zwfw.mot.gov.cn/" target="_blank">交通运输政务服务</a></li>
          </ul>
        </div>
      </div>
    </section>

    <!-- 核心内容区：原有问答组件 -->
    <main class="app-main">
      <QaComponent />
    </main>

    <!-- 页面底部：版权信息 -->
    <footer class="app-footer">
      <p>© 2026 政务服务中心 版权所有 | 本系统仅提供政策咨询参考</p>
    </footer>
  </div>
</template>

<script setup>
// 导入问答组件（路径需正确，@对应src目录）
import QaComponent from '@/components/QaComponent.vue';
import { ElMessage } from 'element-plus';

// 人工咨询跳转逻辑（与QaComponent中功能一致，统一管理）
const goToManual = () => {
  window.open('/manual_chat.html', '_blank');
  ElMessage.info('正在跳转至人工咨询页面...');
};
</script>

<style>
/* 全局样式重置，避免默认边距影响布局 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 头部样式：标题+导航 */
.app-header {
  background-color: #1989fa;
  color: #fff;
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.app-header h1 {
  font-size: 20px;
  margin-bottom: 8px;
}
.nav-item {
  margin-right: 20px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}
.nav-item.active {
  background-color: rgba(255, 255, 255, 0.2);
}
.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

/* 新增：政务导航区样式 */
.gov-nav-area {
  padding: 20px;
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
}
.nav-title {
  font-size: 18px;
  margin-bottom: 16px;
  color: #1989fa;
  padding-left: 8px;
  border-left: 4px solid #1989fa;
}
.nav-container {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 20px;
}
.nav-card {
  flex: 1;
  min-width: 280px;
  max-width: 350px;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.3s ease;
}
.nav-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
.card-title {
  font-size: 16px;
  margin-bottom: 12px;
  color: #2c3e50;
  display: flex;
  align-items: center;
}
.card-title::before {
  content: "";
  display: inline-block;
  width: 4px;
  height: 16px;
  background-color: #1989fa;
  margin-right: 8px;
  border-radius: 2px;
}
.link-list {
  list-style: none;
}
.link-list li {
  margin-bottom: 8px;
}
.link-list a {
  color: #4e5969;
  text-decoration: none;
  padding: 4px 0;
  display: inline-block;
  transition: color 0.2s ease;
}
.link-list a:hover {
  color: #1989fa;
  text-decoration: underline;
}

/* 核心内容区：居中展示，限制宽度 */
.app-main {
  flex: 1;
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  background-color: #f9f9f9;
}

/* 底部样式：版权信息 */
.app-footer {
  text-align: center;
  padding: 16px;
  font-size: 12px;
  color: #666;
  border-top: 1px solid #e6e6e6;
  background-color: #fff;
}
</style>