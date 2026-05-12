/**
 * Flask API 通信服务
 * 平板本地运行时，baseURL = http://localhost:5000
 * Capacitor Android: 通过 Http plugin 或局域网 IP
 */

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:5000'

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    credentials: 'include',
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }))
    throw new Error(err.message ?? 'Request failed')
  }
  return res.json()
}

// ── Types ──────────────────────────────────────
export interface Category { id: number; name_zh: string; name_en: string; name_ru: string; sort_order: number }
export interface Product { id: number; category_id: number; name_zh: string; name_en: string; name_ru: string; price: number; cost_price: number; stock: number; image_url?: string; status: string }
export interface Order { id?: number; order_no: string; subtotal: number; total: number; discount_amount: number; status: string; payment_method?: string; paid_at?: string; created_at?: string }
export interface OrderItem { product_id: number; product_name: string; quantity: number; unit_price: number }
export interface DailyStats { date: string; total_orders: number; total_sales: number; total_cost: number; profit: number }
export interface Settings { shop_name: string; currency_symbol: string; order_prefix: string; default_lang: string; operational_cost: string }

// ── API ────────────────────────────────────────
export const api = {
  getCategories: () => request<Category[]>('/api/categories'),
  getProducts: () => request<Product[]>('/api/products'),
  getSettings: () => request<Settings>('/api/settings'),
  createOrder: (body: { items: OrderItem[]; payment_method?: string; discount_code?: string }) =>
    request<{ order: Order; order_no: string }>('/api/orders', { method: 'POST', body: JSON.stringify(body) }),
  updateOrderStatus: (id: number, status: string) =>
    request(`/api/orders/${id}`, { method: 'PUT', body: JSON.stringify({ status }) }),
  getOrders: (params?: { date?: string; status?: string }) => {
    const q = new URLSearchParams(params as Record<string, string>).toString()
    return request<Order[]>(`/api/orders${q ? '?' + q : ''}`)
  },
  getDailyStats: (date: string) => request<DailyStats>(`/api/stats/daily?date=${date}`),
  getMonthlyStats: (year: number, month: number) =>
    request<{ orders: number; sales: number; cost: number; profit: number }>(`/api/stats/monthly?year=${year}&month=${month}`),
}
