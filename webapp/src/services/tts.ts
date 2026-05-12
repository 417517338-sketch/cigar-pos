/**
 * 语音播报服务（Web Speech API）
 * 使用 XiaoxiaoNeural 音色
 */

let voice: SpeechSynthesisVoice | null = null

function pickVoice() {
  if (voice) return voice
  const voices = speechSynthesis.getVoices()
  // 优先中文音色
  voice = voices.find(v => v.lang.includes('zh')) || voices[0] || null
  return voice
}

// 确保语音列表加载完成
if (speechSynthesis.onvoiceschanged !== undefined) {
  speechSynthesis.onvoiceschanged = () => { pickVoice() }
}

export function speak(text: string, lang = 'zh-CN') {
  speechSynthesis.cancel()
  const utt = new SpeechSynthesisUtterance(text)
  utt.lang = lang
  utt.rate = 1.1
  utt.pitch = 1.0
  const v = pickVoice()
  if (v) utt.voice = v
  speechSynthesis.speak(utt)
}

export const tts = {
  paymentSuccess(amount: number) {
    speak(`收款到账，${amount}元`)
  },
  refundSuccess() {
    speak('退单已完成')
  },
  scanFailed() {
    speak('请重新扫码')
  },
  lowStock(name: string) {
    speak(`${name}，库存不足`)
  },
  orderPlaced(orderNo: string) {
    speak(`订单已创建，${orderNo}`)
  }
}
