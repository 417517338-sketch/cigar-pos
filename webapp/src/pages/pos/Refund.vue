<template>
  <div class="refund-shell">
    <header class="refund-header">
      <button class="btn btn-ghost btn-icon" @click="router.back()">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 5l-7 7 7 7"/>
        </svg>
      </button>
      <h2>{{ t('refund') }}</h2>
      <div style="width:40px"></div>
    </header>

    <div class="refund-body">
      <!-- 扫码退 -->
      <div class="refund-section">
        <div class="section-label">{{ t('scanToRefund') }}</div>
        <div v-if="!order" class="scan-prompt" @click="startScan">
          <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M3 7V5a2 2 0 012-2h2M17 3h2a2 2 0 012 2v2M21 17v2a2 2 0 01-2 2h-2M7 21H5a2 2 0 01-2-2v-2"/>
            <rect x="7" y="7" width="10" height="10" rx="1"/>
          </svg>
          <p>{{ t('tapToScanOrder') }}</p>
        </div>
      </div>

      <!-- 手动输入订单号 -->
      <div class="manual-section">
        <div class="section-label">{{ t('orEnterManually') }}</div>
        <div class="manual-row">
          <input
            v-model="manualOrderNo"
            :placeholder="t('orderNoPlaceholder')"
            class="manual-input"
            @keyup.enter="lookupOrder"
          />
          <button class="btn btn-outline" @click="lookupOrder">{{ t('lookup') }}</button>
        </div>
      </div>

      <!-- 订单详情 -->
      <div v-if="order" class="order-detail card">
        <div class="order-detail-header">
          <div>
            <div class="order-no mono">{{ order.order_no }}</div>
            <div class="order-date dim-text">{{ formatDate(order.paid_at) }}</div>
          </div>
          <div class="order-status" :class="'status-' + order.status">
            {{ statusLabel(order.status) }}
          </div>
        </div>

        <div class="divider"></div>

        <!-- 订单明细 -->
        <div v-if="orderItems.length" class="order-items-list">
          <div v-for="item in orderItems" :key="item.id" class="order-item-row">
            <span>{{ item.product_name }} × {{ item.quantity }}</span>
            <span class="mono">{{ currencySymbol }}{{ (item.unit_price * item.quantity).toFixed(0) }}</span>
          </div>
        </div>

        <div class="divider"></div>

        <div class="order-total">
          <span>{{ t('total') }}</span>
          <span class="mono total-price">{{ currencySymbol }}{{ order.total.toFixed(0) }}</span>
        </div>

        <!-- 退单原因 -->
        <div class="refund-reason">
          <textarea
            v-model="refundNote"
            :placeholder="t('refundNotePlaceholder')"
            class="refund-note-input"
            rows="2"
          ></textarea>
        </div>

        <!-- 确认退单 -->
        <button
          class="btn btn-danger btn-full btn-lg"
          :disabled="isRefunding"
          @click="confirmRefund"
        >
          <template v-if="isRefunding">
            <span class="spinner-white"></span> {{ t('processing') }}
          </template>
          <template v-else>
            {{ t('confirmRefund') }} {{ currencySymbol }}{{ order.total.toFixed(0) }}
          </template>
        </button>
      </div>

      <!-- 无订单 -->
      <div v-if="notFound" class="not-found">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/>
          <path d="M15 9l-6 6M9 9l6 6"/>
        </svg>
        <p>{{ t('orderNotFound') }}</p>
      </div>
    </div>

    <!-- 扫码弹窗 -->
    <div v-if="showScanner" class="modal-overlay" @click.self="closeScanner">
      <div class="modal scanner-modal">
        <div class="scanner-header">
          <h3>{{ t('scanOrderQR') }}</h3>
          <button class="btn btn-ghost btn-icon" @click="closeScanner">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <video ref="videoEl" class="scanner-video" autoplay playsinline></video>
        <p class="scanner-hint">{{ t('scannerHint') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { api, type Order, type OrderItem } from '../../services/api'
import { tts } from '../../services/tts'
import { initScanner, stopScanner } from '../../services/scanner'

const router = useRouter()

const currencySymbol = ref('¥')
const lang = ref('zh')
const manualOrderNo = ref('')
const order = ref<Order | null>(null)
const orderItems = ref<OrderItem[]>([])
const notFound = ref(false)
const showScanner = ref(false)
const isRefunding = ref(false)
const refundNote = ref('')
const videoEl = ref<HTMLVideoElement | null>(null)

const T = {
  zh: {
    refund:'退单', scanToRefund:'扫码退单', tapToScanOrder:'点击扫描小票二维码', orEnterManually:'或手动输入', orderNoPlaceholder:'输入订单号', lookup:'查询',
    total:'合计', refundNotePlaceholder:'退单备注（可选）', processing:'处理中...', confirmRefund:'确认退单', orderNotFound:'未找到该订单', scanOrderQR:'扫描订单二维码', scannerHint:'将二维码放入框内',
    status_pending:'待支付', status_paid:'已支付', status_refunded:'已退款', status_cancelled:'已取消',
  },
  en: {
    refund:'Refund', scanToRefund:'Scan to refund', tapToScanOrder:'Tap to scan receipt QR', orEnterManually:'Or enter manually', orderNoPlaceholder:'Order number', lookup:'Lookup',
    total:'Total', refundNotePlaceholder:'Refund note (optional)', processing:'Processing...', confirmRefund:'Confirm refund', orderNotFound:'Order not found', scanOrderQR:'Scan order QR', scannerHint:'Align QR in frame',
    status_pending:'Pending', status_paid:'Paid', status_refunded:'Refunded', status_cancelled:'Cancelled',
  },
  ru: {
    refund:'Возврат', scanToRefund:'Сканировать возврат', tapToScanOrder:'Нажмите сканировать QR чека', orEnterManually:'Или введите вручную', orderNoPlaceholder:'Номер заказа', lookup:'Найти',
    total:'Итого', refundNotePlaceholder:'Примечание (необязательно)', processing:'Обработка...', confirmRefund:'Подтвердить возврат', orderNotFound:'Заказ не найден', scanOrderQR:'Сканировать QR заказа', scannerHint:'Расположите QR в рамке',
    status_pending:'Ожидает', status_paid:'Оплачен', status_refunded:'Возвращен', status_cancelled:'Отменен',
  },
}
function t(key: keyof typeof T.zh) { return T[lang.value as keyof typeof T]?.[key] ?? T.zh[key] }

function statusLabel(s: string) {
  return t(`status_${s}` as keyof typeof T.zh) ?? s
}

function formatDate(d?: string) {
  if (!d) return ''
  return new Date(d).toLocaleString(lang.value === 'zh' ? 'zh-CN' : lang.value === 'en' ? 'en-US' : 'ru-RU')
}

async function lookupOrder(orderNo?: string) {
  const no = orderNo ?? manualOrderNo.value.trim()
  if (!no) return
  notFound.value = false
  order.value = null
  try {
    const orders = await api.getOrders({ status: 'paid' })
    const found = orders.find(o => o.order_no === no)
    if (!found || found.status !== 'paid') {
      notFound.value = true
      return
    }
    order.value = found
  } catch {
    notFound.value = true
  }
}

async function startScan() {
  if (!videoEl.value) return
  showScanner.value = true
  try {
    await initScanner(videoEl.value, (text) => {
      closeScanner()
      // text 是订单号或 URL
      const no = text.includes('order_no=') ? text.split('order_no=')[1].split('&')[0] : text.trim()
      manualOrderNo.value = no
      lookupOrder(no)
      tts.speak('订单已找到')
    })
  } catch {
    closeScanner()
    tts.scanFailed()
  }
}

function closeScanner() {
  stopScanner()
  showScanner.value = false
}

async function confirmRefund() {
  if (!order.value || isRefunding.value) return
  isRefunding.value = true
  try {
    await api.updateOrderStatus(order.value.id!, 'refunded')
    tts.refundSuccess()
    order.value = null
    router.push('/')
  } catch (e) {
    console.error(e)
  } finally {
    isRefunding.value = false
  }
}

lang.value = localStorage.getItem('pos_lang') ?? 'zh'
api.getSettings().then(s => { currencySymbol.value = s.currency_symbol || '¥' }).catch(() => {})

onUnmounted(() => { stopScanner() })
</script>

<style scoped>
.refund-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  height: 100dvh;
  background: var(--bg-root);
}
.refund-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.refund-header h2 { font-size: 16px; font-weight: 700; }

.refund-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px 40px;
  max-width: 600px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--cream-dim);
  margin-bottom: 10px;
}

.scan-prompt {
  border: 2px dashed var(--gold-dim);
  border-radius: var(--radius);
  padding: 36px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--gold-dim);
  cursor: pointer;
  transition: border-color 150ms, color 150ms;
}
.scan-prompt:hover { border-color: var(--gold); color: var(--gold); }

.manual-section {}
.manual-row { display: flex; gap: 10px; }
.manual-input { flex: 1; }

.order-detail {}
.order-detail-header { display: flex; justify-content: space-between; align-items: flex-start; }
.order-no { font-size: 15px; font-weight: 700; color: var(--cream); }
.order-date { font-size: 12px; margin-top: 2px; }
.order-status {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
}
.status-paid { background: rgba(74,156,109,0.2); color: var(--success); }
.status-refunded { background: rgba(201,74,74,0.2); color: var(--danger); }

.order-items-list { display: flex; flex-direction: column; gap: 6px; }
.order-item-row { display: flex; justify-content: space-between; font-size: 13px; color: var(--cream-dim); }

.order-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 700;
}
.total-price { font-size: 20px; color: var(--gold); }

.refund-reason { margin: 12px 0; }
.refund-note-input {
  width: 100%;
  resize: none;
  background: var(--bg-input);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--cream);
  font-family: inherit;
  font-size: 13px;
  padding: 10px 14px;
  outline: none;
}
.refund-note-input:focus { border-color: var(--gold); }
.refund-note-input::placeholder { color: var(--cream-dim); }

.spinner-white {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px;
  color: var(--cream-dim);
  text-align: center;
}

/* Scanner */
.scanner-modal { width: 100%; max-width: 420px; padding: 0; overflow: hidden; }
.scanner-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid var(--border); }
.scanner-header h3 { font-size: 16px; font-weight: 700; }
.scanner-video { width: 100%; aspect-ratio: 1; background: #000; display: block; }
.scanner-hint { padding: 12px; text-align: center; font-size: 13px; color: var(--cream-dim); }
</style>
