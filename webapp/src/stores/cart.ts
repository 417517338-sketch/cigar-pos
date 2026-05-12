import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface CartItem {
  product_id: number
  name: string
  price: number
  quantity: number
  image_url?: string
}

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])

  const totalCount = computed(() =>
    items.value.reduce((s, i) => s + i.quantity, 0)
  )

  const subtotal = computed(() =>
    items.value.reduce((s, i) => s + i.price * i.quantity, 0)
  )

  function addItem(product: Omit<CartItem, 'quantity'>, qty = 1) {
    const existing = items.value.find(i => i.product_id === product.product_id)
    if (existing) {
      existing.quantity += qty
    } else {
      items.value.push({ ...product, quantity: qty })
    }
  }

  function removeItem(product_id: number) {
    items.value = items.value.filter(i => i.product_id !== product_id)
  }

  function updateQty(product_id: number, quantity: number) {
    if (quantity <= 0) { removeItem(product_id); return }
    const item = items.value.find(i => i.product_id === product_id)
    if (item) item.quantity = quantity
  }

  function clearCart() { items.value = [] }

  return { items, totalCount, subtotal, addItem, removeItem, updateQty, clearCart }
})
