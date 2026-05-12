<template>
  <div class="pos-shell">

    <!-- ── 侧边栏 ── -->
    <aside class="pos-sidebar">
      <div class="sidebar-header">
        <div class="sidebar-logo">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M12 2C6 2 4 8 4 12c0 4 2 8 8 10 6-2 8-6 8-10 0-4-2-10-8-10z"/>
            <path d="M12 22V10"/><path d="M8 6c2 2 6 2 8 0"/>
          </svg>
        </div>
        <div class="sidebar-brand">{{ shopName }}</div>
      </div>

      <nav class="sidebar-nav">
        <div class="cat-label">{{ t('categories') }}</div>

        <button
          class="cat-btn"
          :class="{ active: activeCategory === 0 }"
          @click="setCategory(0)"
        >
          <div class="cat-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </div>
          <span>{{ t('all') }}</span>
          <span class="cat-count">{{ products.length }}</span>
        </button>

        <button
          v-for="cat in categories"
          :key="cat.id"
          class="cat-btn"
          :class="{ active: activeCategory === cat.id }"
          @click="setCategory(cat.id)"
        >
          <div class="cat-icon">{{ cat.id }}</div>
          <span>{{ getCatName(cat) }}</span>
          <span class="cat-count">{{ getCatCount(cat.id) }}</span>
        </button>
      </nav>

      <div class="sidebar-footer">
        <button class="btn btn-ghost btn-full" @click="goRefund">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
            <path d="M3 3v5h5"/>
          </svg>
          {{ t('refund') }}
        </button>
      </div>
    </aside>

    <!-- ── 主区域 ── -->
    <main class="pos-main">
      <!-- 顶部栏 -->
      <header class="pos-topbar">
        <div class="topbar-title">{{ t('menu') }}</div>
        <div class="topbar-right">
          <select v-model="lang" class="lang-select" @change="saveLang">
            <option value="zh">中文</option>
            <option value="en">EN</option>
            <option value="ru">RU</option>
          </select>
        </div>
      </header>

      <!-- 产品网格 -->
      <div class="products-area">
        <div class="products-grid">
          <div
            v-for="product in filteredProducts"
            :key="product.id"
            class="product-card fade-in"
            :class="{
              'out-of-stock': product.stock === 0,
              'low-stock': product.stock > 0 && product.stock <= 3
            }"
            @click="handleCardClick(product)"
          >
            <div class="product-image">
              <img v-if="product.image_url" :src="product.image_url" :alt="getProdName(product)" loading="lazy" />
              <div v-else class="product-image-placeholder">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                  <path d="M12 2C6 2 4 8 4 12c0 4 2 8 8 10 6-2 8-6 8-10 0-4-2-10-8-10z"/>
                  <path d="M12 22V10"/><path d="M8 6c2 2 6 2 8 0"/>
                </svg>
              </div>
              <!-- 库存标识 -->
              <div v-if="product.stock === 0" class="product-overlay out-of-stock">
                {{ t('soldOut') }}
              </div>
              <div v-else-if="product.stock <= 3" class="product-overlay low-stock">
                {{ t('lowStock') }} {{ product.stock }}
              </div>
            </div>

            <div class="product-info">
              <div class="product-name">{{ getProdName(product) }}</div>
              <div v-if="product.spec" class="product-spec">{{ product.spec }}</div>
              <div class="product-bottom">
                <div class="product-price">{{ currencySymbol }}{{ product.price.toFixed(0) }}</div>

                <template v-if="product.stock > 0">
                  <!-- 已选数量 -->
                  <div v-if="getCartQty(product.id) > 0" class="qty-stepper">
                    <button class="qty-btn" @click.stop="adjustQty(product, -1)">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <path d="M5 12h14"/>
                      </svg>
                    </button>
                    <span class="qty-num">{{ getCartQty(product.id) }}</span>
                    <button class="qty-btn" @click.stop="adjustQty(product, 1)">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <path d="M12 5v14M5 12h14"/>
                      </svg>
                    </button>
                  </div>
                  <!-- 未选：显示添加按钮 -->
                  <button v-else class="add-btn" @click.stop="addToCart(product)">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <path d="M12 5v14M5 12h14"/>
                    </svg>
                  </button>
                </template>
                <span v-else class="unavailable-text">{{ t('na') }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="filteredProducts.length === 0" class="empty-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <p>{{ t('noProducts') }}</p>
        </div>
      </div>
    </main>

    <!-- ── 购物车栏 ── -->
    <div class="cart-bar" :class="{ 'has-items': cartStore.totalCount > 0 }" @click="goCheckout">
      <div class="cart-bar-inner">
        <div class="cart-summary">
          <span class="cart-icon-wrap">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>
              <path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/>
            </svg>
            <span class="cart-badge" v-if="cartStore.totalCount > 0">{{ cartStore.totalCount }}</span>
          </span>
          <span>{{ t('cart') }}</span>
        </div>
        <template v-if="cartStore.totalCount > 0">
          <div class="cart-total-label">{{ t('total') }}</div>
          <div class="cart-total">{{ currencySymbol }}{{ cartStore.subtotal.toFixed(0) }}</div>
          <button class="checkout-btn" @click.stop="goCheckout">
            {{ t('checkout') }}
          </button>
        </template>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore, type CartItem } from '../../stores/cart'
import { api, type Category, type Product } from '../../services/api'
import { tts } from '../../services/tts'

const router = useRouter()
const cartStore = useCartStore()

// ── State ──
const shopName = ref('Cigar Lounge')
const currencySymbol = ref('¥')
const lang = ref('zh')
const categories = ref<Category[]>([])
const products = ref<Product[]>([])
const activeCategory = ref(0)

// ── i18n ──
const T = {
  zh: {
    categories: '分类', all: '全部', menu: '精选菜单', refund: '退单',
    soldOut: '已售罄', lowStock: '仅剩', na: '缺货',
    noProducts: '暂无产品', cart: '购物车', total: '合计', checkout: '去结算',
  },
  en: {
    categories: 'Categories', all: 'All', menu: 'Curated Menu', refund: 'Refund',
    soldOut: 'Sold Out', lowStock: 'Left', na: 'N/A',
    noProducts: 'No products', cart: 'Cart', total: 'Total', checkout: 'Checkout',
  },
  ru: {
    categories: 'Категории', all: 'Все', menu: 'Меню', refund: 'Возврат',
    soldOut: 'Нет в наличии', lowStock: 'Осталось', na: 'Нет',
    noProducts: 'Нет товаров', cart: 'Корзина', total: 'Итого', checkout: 'Оплатить',
  },
}
function t(key: keyof typeof T.zh) { return T[lang.value as keyof typeof T]?.[key] ?? T.zh[key] }

function getCatName(c: Category) {
  return lang.value === 'zh' ? c.name_zh : lang.value === 'en' ? c.name_en : c.name_ru
}
function getProdName(p: Product) {
  return lang.value === 'zh' ? p.name_zh : lang.value === 'en' ? p.name_en : p.name_ru
}

const filteredProducts = computed(() => {
  if (activeCategory.value === 0) return products.value.filter(p => p.status === 'active')
  return products.value.filter(p => p.category_id === activeCategory.value && p.status === 'active')
})

function getCatCount(catId: number) {
  return products.value.filter(p => p.category_id === catId && p.status === 'active').length
}

function getCartQty(productId: number) {
  return cartStore.items.find(i => i.product_id === productId)?.quantity ?? 0
}

// ── Actions ──
function setCategory(catId: number) {
  activeCategory.value = catId
}

function addToCart(product: Product) {
  if (product.stock === 0) { tts.lowStock(getProdName(product)); return }
  cartStore.addItem({ product_id: product.id, name: getProdName(product), price: product.price })
}

function adjustQty(product: Product, delta: number) {
  const qty = getCartQty(product.id) + delta
  if (qty <= 0) {
    cartStore.removeItem(product.id)
    return
  }
  if (qty > product.stock) { tts.lowStock(getProdName(product)); return }
  cartStore.updateQty(product.id, qty)
}

function handleCardClick(product: Product) {
  if (product.stock === 0) return
  addToCart(product)
}

function goCheckout() {
  if (cartStore.totalCount > 0) router.push('/checkout')
}

function goRefund() {
  router.push('/refund')
}

function saveLang() {
  localStorage.setItem('pos_lang', lang.value)
}

// ── Load data ──
onMounted(async () => {
  lang.value = localStorage.getItem('pos_lang') ?? 'zh'
  try {
    const [cats, prods, settings] = await Promise.all([
      api.getCategories(),
      api.getProducts(),
      api.getSettings(),
    ])
    categories.value = cats
    products.value = prods
    shopName.value = settings.shop_name || 'Cigar Lounge'
    currencySymbol.value = settings.currency_symbol || '¥'
  } catch (e) {
    console.error('Failed to load data', e)
  }
})
</script>

<style scoped>
/* ── Layout ── */
.pos-shell {
  display: flex;
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
  background: var(--bg-root);
}

/* ── Sidebar ── */
.pos-sidebar {
  width: 180px;
  min-width: 180px;
  background: var(--bg-sidebar);
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border);
}

.sidebar-header {
  padding: 20px 16px 16px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar-logo {
  color: var(--gold);
  display: flex;
}

.sidebar-brand {
  font-size: 15px;
  font-weight: 700;
  color: var(--cream);
  line-height: 1.2;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.cat-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--cream-dim);
  padding: 4px 8px 8px;
}

.cat-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--cream-dim);
  cursor: pointer;
  font-size: 13px;
  font-family: inherit;
  text-align: left;
  transition: background 120ms, color 120ms;
  width: 100%;
}
.cat-btn:hover { background: rgba(201,168,76,0.08); color: var(--cream); }
.cat-btn.active { background: rgba(201,168,76,0.15); color: var(--gold); }

.cat-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--bg-input);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  flex-shrink: 0;
}
.cat-btn.active .cat-icon { background: var(--gold); color: #0F0D0B; }

.cat-count {
  margin-left: auto;
  font-size: 11px;
  color: var(--cream-dim);
  min-width: 18px;
  text-align: center;
}

.sidebar-footer {
  padding: 12px 8px;
  border-top: 1px solid var(--border);
}

/* ── Main ── */
.pos-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.pos-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-root);
  flex-shrink: 0;
}

.topbar-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--cream);
}

.lang-select {
  width: auto;
  padding: 6px 10px;
  font-size: 12px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  color: var(--cream);
  border-radius: var(--radius-sm);
  cursor: pointer;
}

/* ── Products ── */
.products-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px 100px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 14px;
}

.product-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  cursor: pointer;
  transition: transform 100ms, box-shadow 100ms, border-color 150ms;
}
.product-card:hover { transform: scale(1.02); box-shadow: 0 6px 20px rgba(0,0,0,0.4); }
.product-card:active { transform: scale(0.98); }
.product-card.out-of-stock { opacity: 0.5; cursor: default; }
.product-card.out-of-stock:hover { transform: none; box-shadow: none; }

.product-image {
  position: relative;
  aspect-ratio: 1;
  background: var(--bg-input);
  overflow: hidden;
}
.product-image img { width: 100%; height: 100%; object-fit: cover; }
.product-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--gold-dim);
}

.product-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 6px 8px;
  font-size: 11px;
  font-weight: 600;
  text-align: center;
}
.product-overlay.out-of-stock { background: rgba(0,0,0,0.7); color: var(--cream-dim); }
.product-overlay.low-stock { background: rgba(201,168,76,0.85); color: #0F0D0B; }

.product-info { padding: 10px 12px 12px; }
.product-name { font-size: 13px; font-weight: 600; color: var(--cream); line-height: 1.3; margin-bottom: 4px; }
.product-spec { font-size: 11px; color: var(--cream-dim); margin-bottom: 6px; }

.product-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 6px;
}

.product-price {
  font-family: var(--font-mono);
  font-size: 15px;
  font-weight: 700;
  color: var(--gold);
}

/* ── Qty Stepper ── */
.qty-stepper {
  display: flex;
  align-items: center;
  gap: 0;
  background: var(--bg-input);
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid var(--border);
}
.qty-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--cream);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.qty-btn:active { background: rgba(255,255,255,0.1); }
.qty-num {
  min-width: 24px;
  text-align: center;
  font-size: 13px;
  font-weight: 600;
  color: var(--cream);
  font-family: var(--font-mono);
}

.add-btn {
  width: 28px;
  height: 28px;
  border: 1.5px solid var(--gold);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--gold);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.add-btn:active { background: rgba(201,168,76,0.2); }

.unavailable-text {
  font-size: 11px;
  color: var(--cream-dim);
}

/* ── Empty State ── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--cream-dim);
  gap: 12px;
}
.empty-state p { font-size: 14px; }

/* ── Cart Bar ── */
.cart-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: var(--bg-sidebar);
  border-top: 1px solid var(--border);
  transition: transform 250ms cubic-bezier(0.34,1.56,0.64,1);
}
.cart-bar:not(.has-items) { transform: translateY(60px); }

.cart-bar-inner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  padding-bottom: max(12px, env(safe-area-inset-bottom));
  max-width: 600px;
  margin: 0 auto;
}

.cart-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--cream);
  cursor: pointer;
}

.cart-icon-wrap {
  position: relative;
  display: inline-flex;
}

.cart-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  background: var(--gold);
  color: #0F0D0B;
  border-radius: 9px;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cart-total-label {
  font-size: 12px;
  color: var(--cream-dim);
  margin-left: auto;
}

.cart-total {
  font-family: var(--font-mono);
  font-size: 16px;
  font-weight: 700;
  color: var(--gold);
}

.checkout-btn {
  padding: 10px 20px;
  background: var(--gold);
  color: #0F0D0B;
  border: none;
  border-radius: var(--radius-sm);
  font-family: inherit;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 80ms, background 80ms;
  margin-left: 8px;
}
.checkout-btn:active { transform: scale(0.97); background: #D4B55A; }

/* ── Responsive: 平板横屏 ── */
@media (min-width: 900px) {
  .products-grid { grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); }
}
@media (max-width: 480px) {
  .pos-sidebar { width: 140px; min-width: 140px; }
  .products-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .sidebar-brand { font-size: 13px; }
}
</style>
