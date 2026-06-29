import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()
app.use(ElementPlus)
app.use(pinia)
app.use(router)

// 刷新后恢复用户信息
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
authStore.restoreUser().finally(() => {
  app.mount('#app')
})
