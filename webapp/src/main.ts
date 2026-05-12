import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

// Pages
import PosIndex from './pages/pos/Index.vue'
import PosCheckout from './pages/pos/Checkout.vue'
import PosRefund from './pages/pos/Refund.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',          component: PosIndex,    name: 'pos' },
    { path: '/checkout', component: PosCheckout, name: 'checkout' },
    { path: '/refund',   component: PosRefund,   name: 'refund' },
  ],
})

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
app.use(router)
app.mount('#app')
