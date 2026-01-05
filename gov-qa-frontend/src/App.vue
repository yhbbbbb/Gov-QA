<template>
  <div id="app">
    <div>QaComponent </div> <!-- 引入问答组件 -->
  </div>
</template>

<script setup>
// 导入问答组件（路径需正确，@对应src目录）
import QaComponent from '@/components/QaComponent.vue';
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
}
</style>