import { createApp } from 'vue';
import App from './App.vue';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';

// 创建并挂载应用
createApp(App)
  .use(ElementPlus)
  .mount('#app');