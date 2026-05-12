<template>
  <div class="checkout-shell">

    <!-- 顶部 -->
    <header class="checkout-header">
      <button class="btn btn-ghost btn-icon" @click="router.back()">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 5l-7 7 7 7"/>
        </svg>
      </button>
      <h2>{{ t('checkout') }}</h2>
      <div style="width:40px"></div>
    </header>

    <!-- 订单明细 -->
    <div class="checkout-body">
      <div class="order-items">
        <div v-for="item in cartStore.items" :key="item.product_id" class="order-item">
          <div class="order-item-info">
            <div class="order-item-name">{{ item.name }}</div>
            <div class="order-item-qty">x{{ item.quantity }}</div>
          </div>
          <div class="order-item-price">{{ currencySymbol }}{{ (item.price * item.quantity).toFixed(0) }}</div>
        </div>
      </div>

      <div class="divider"></div>

      <!-- 折扣码 -->
      <div class="discount-row">
        <input
          v-model="discountCode"
          :placeholder="t('discountPlaceholder')"
          class="discount-input"
          @keyup.enter="applyDiscount"
        />
        <button class="btn btn-outline" @click="applyDiscount">{{ t('apply') }}</button>
      </div>
      <div v-if="discountLabel" class="discount-applied">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 6L9 17l-5-5"/>
        </svg>
        {{ discountLabel }}
        <button class="btn-remove" @click="removeDiscount">×</button>
      </div>

      <div class="divider"></div>

      <!-- 金额 -->
      <div class="amount-rows">
        <div class="amount-row">
          <span>{{ t('subtotal') }}</span>
          <span class="mono">{{ currencySymbol }}{{ subtotal.toFixed(2) }}</span>
        </div>
        <div v-if="discountAmount > 0" class="amount-row discount-row-amount">
          <span>{{ t('discount') }}</span>
          <span class="mono text-danger">-{{ currencySymbol }}{{ discountAmount.toFixed(2) }}</span>
        </div>
        <div class="amount-row total-row">
          <span>{{ t('total') }}</span>
          <span class="mono total-amount">{{ currencySymbol }}{{ total.toFixed(2) }}</span>
        </div>
      </div>

      <div class="divider"></div>

      <!-- 收款方式 -->
      <div class="payment-section">
        <div class="section-label">{{ t('paymentMethod') }}</div>
        <div class="payment-methods">
          <button
            v-for="m in paymentMethods"
            :key="m.id"
            class="payment-btn"
            :class="{ active: paymentMethod === m.id }"
            @click="paymentMethod = m.id"
          >
            <span class="payment-icon" v-html="m.icon"></span>
            <span>{{ m.label }}</span>
          </button>
        </div>
      </div>

      <!-- 扫码 -->
      <div v-if="paymentMethod === 'scan'" class="scan-section">
        <div v-if="!scanned" class="scan-prompt" @click="startScan">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <path d="M3 7V5a2 2 0 012-2h2M17 3h2a2 2 0 012 2v2M21 17v2a2 2 0 01-2 2h-2M7 21H5a2 2 0 01-2-2v-2"/>
            <rect x="7" y="7" width="10" height="10" rx="1"/>
          </svg>
          <p>{{ t('tapToScan') }}</p>
        </div>

        <div v-else class="scan-result">
          <div class="scan-ok">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--success)" stroke-width="2">
              <path d="M20 6L9 17l-5-5"/>
            </svg>
            <p>{{ t('scanSuccess') }}</p>
          </div>
        </div>
      </div>

      <!-- 确认按钮 -->
      <button
        class="btn btn-gold btn-full btn-lg confirm-btn"
        :disabled="isSubmitting"
        @click="confirmPayment"
      >
        <template v-if="isSubmitting">
          <span class="spinner"></span> {{ t('processing') }}
        </template>
        <template v-else>
          {{ t('confirmPayment') }} {{ currencySymbol }}{{ total.toFixed(0) }}
        </template>
      </button>
    </div>

    <!-- 扫码弹窗 -->
    <div v-if="showScanner" class="modal-overlay" @click.self="closeScanner">
      <div class="modal scanner-modal">
        <div class="scanner-header">
          <h3>{{ t('scanQRCode') }}</h3>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../../stores/cart'
import { api } from '../../services/api'
import { tts } from '../../services/tts'
import { initScanner, stopScanner } from '../../services/scanner'

const router = useRouter()
const cartStore = useCartStore()

const currencySymbol = ref('¥')
const lang = ref('zh')
const discountCode = ref('')
const discountLabel = ref('')
const discountRate = ref(0)
const discountAmount = ref(0)
const paymentMethod = ref('scan')
const scanned = ref(false)
const showScanner = ref(false)
const isSubmitting = ref(false)
const videoEl = ref<HTMLVideoElement | null>(null)

const paymentMethods = [
  {
    id: 'scan',
    label: '微信/支付宝',
    icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 7h10M7 12h10M7 17h6"/></svg>`,
  },
  {
    id: 'cash',
    label: '现金',
    icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M6 12h.01M18 12h.01"/></svg>`,
  },
]

const T = {
  zh: { checkout:'结算', discountPlaceholder:'输入折扣码', apply:'应用', subtotal:'小计', discount:'折扣', total:'合计', paymentMethod:'支付方式', tapToScan:'点击扫码', scanSuccess:'扫码成功', processing:'处理中...', confirmPayment:'确认收款', scanQRCode:'扫描收款码', scannerHint:'将二维码放入框内' },
  en: { checkout:'Checkout', discountPlaceholder:'Discount code', apply:'Apply', subtotal:'Subtotal', discount:'Discount', total:'Total', paymentMethod:'Payment', tapToScan:'Tap to scan', scanSuccess:'Scanned', processing:'Processing...', confirmPayment:'Confirm payment', scanQRCode:'Scan QR Code', scannerHint:'Align QR code in frame' },
  ru: { checkout:'Оплата', discountPlaceholder:'Скидка', apply:'Применить', subtotal:'Подитог', discount:'Скидка', total:'Итого', paymentMethod:'Оплата', tapToScan:'Нажмите сканировать', scanSuccess:'Отсканировано', processing:'Обработка...', confirmPayment:'Подтвердить оплату', scanQRCode:'Сканировать QR', scannerHint:'Расположите QR в рамке' },
}
function t(key: keyof typeof T.zh) { return T[lang.value as keyof typeof T]?.[key] ?? T.zh[key] }

const subtotal = computed(() => cartStore.subtotal)
const total = computed(() => subtotal.value - discountAmount.value)

async function applyDiscount() {
  if (!discountCode.value) return
  try {
    const res = await api.getProducts()
    // 折扣码校验后续实现，这里简化处理
    discountLabel.value = `${discountCode.value} 已应用`
    discountRate.value = 0.1
    discountAmount.value = subtotal.value * 0.1
  } catch {
    discountLabel.value = ''
    discountAmount.value = 0
  }
}

function removeDiscount() {
  discountCode.value = ''
  discountLabel.value = ''
  discountRate.value = 0
  discountAmount.value = 0
}

async function startScan() {
  if (!videoEl.value) return
  showScanner.value = true
  try {
    await initScanner(videoEl.value, (text) => {
      scanned.value = true
      closeScanner()
      tts.speak('扫码成功')
    })
  } catch (e) {
    closeScanner()
    tts.scanFailed()
  }
}

function closeScanner() {
  stopScanner()
  showScanner.value = false
}

async function confirmPayment() {
  if (isSubmitting.value) return
  isSubmitting.value = true
  try {
    const orderNo = `CL-${new Date().toISOString().slice(0,10).replace(/-/g,'')}-${Date.now().toString().slice(-4)}`
    const items = cartStore.items.map(i => ({
      product_id: i.product_id,
      product_name: i.name,
      quantity: i.quantity,
      unit_price: i.price,
    }))
    await api.createOrder({
      items,
      payment_method: paymentMethod.value === 'scan' ? 'wechat' : 'cash',
      discount_code: discountCode.value || undefined,
    })
    tts.paymentSuccess(total.value)
    cartStore.clearCart()
    router.push('/')
  } catch (e) {
    console.error(e)
    tts.scanFailed()
  } finally {
    isSubmitting.value = false
  }
}

onMounted(async () => {
  lang.value = localStorage.getItem('pos_lang') ?? 'zh'
  try {
    const s = await api.getSettings()
    currencySymbol.value = s.currency_symbol || '¥'
  } catch {}
})

onUnmounted(() => { stopScanner() })
</script>

<style scoped>
.checkout-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  height: 100dvh;
  background: var(--bg-root);
}

.checkout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.checkout-header h2 { font-size: 16px; font-weight: 700; }

.checkout-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px 120px;
  max-width: 600px;
  margin: 0 auto;
  width: 100%;
}

.order-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}
.order-item:last-child { border-bottom: none; }
.order-item-info { display: flex; flex-direction: column; gap: 2px; }
.order-item-name { font-size: 14px; font-weight: 600; color: var(--cream); }
.order-item-qty { font-size: 12px; color: var(--cream-dim); }
.order-item-price { font-family: var(--font-mono); font-size: 15px; font-weight: 700; color: var(--gold); }

.discount-row { display: flex; gap: 10px; margin-bottom: 10px; }
.discount-input { flex: 1; }
.discount-applied {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--success);
  margin-bottom: 10px;
}
.btn-remove {
  margin-left: auto;
  background: none;
  border: none;
  color: var(--cream-dim);
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
}

.amount-rows { display: flex; flex-direction: column; gap: 8px; }
.amount-row { display: flex; justify-content: space-between; font-size: 14px; color: var(--cream-dim); }
.amount-row.discount-row-amount { color: var(--danger); }
.total-row { font-size: 16px; font-weight: 700; color: var(--cream); margin-top: 4px; }
.total-amount { font-size: 20px; color: var(--gold); }
.text-danger { color: var(--danger); }

.payment-section { margin: 8px 0; }
.section-label { font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--cream-dim); margin-bottom: 12px; }
.payment-methods { display: flex; gap: 10px; }
.payment-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 12px;
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  color: var(--cream-dim);
  cursor: pointer;
  font-size: 13px;
  font-family: inherit;
  transition: border-color 150ms, color 150ms;
}
.payment-btn.active { border-color: var(--gold); color: var(--gold); }
.payment-icon { display: flex; }

.scan-section { margin: 16px 0; }
.scan-prompt {
  border: 2px dashed var(--gold-dim);
  border-radius: var(--radius);
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--gold-dim);
  cursor: pointer;
  transition: border-color 150ms, color 150ms;
}
.scan-prompt:hover { border-color: var(--gold); color: var(--gold); }
.scan-ok { display: flex; flex-direction: column; align-items: center; gap: 8px; color: var(--success); }

.confirm-btn { margin-top: 16px; }
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0,0,0,0.3);
  border-top-color: #0F0D0B;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Scanner Modal */
.scanner-modal {
  width: 100%;
  max-width: 420px;
  padding: 0;
  overflow: hidden;
}
.scanner-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}
.scanner-header h3 { font-size: 16px; font-weight: 700; }
.scanner-video {
  width: 100%;
  aspect-ratio: 1;
  background: #000;
  display: block;
}
.scanner-hint {
  padding: 12px;
  text-align: center;
  font-size: 13px;
  color: var(--cream-dim);
}
</style>
