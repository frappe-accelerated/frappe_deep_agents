import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import './index.css'

const app = createApp(App)

app.use(router)

// Make frappe available globally (for API calls)
window.frappe = window.frappe || {}

// Mount to #agent-chat-app if in Desk, otherwise #app
const mountPoint = document.getElementById('agent-chat-app') ? '#agent-chat-app' : '#app'
app.mount(mountPoint)
