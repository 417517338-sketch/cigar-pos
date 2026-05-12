/**
 * 摄像头扫码服务
 */
import { BrowserMultiFormatReader } from '@zxing/library'

let reader: BrowserMultiFormatReader | null = null

export async function initScanner(
  videoEl: HTMLVideoElement,
  onResult: (text: string) => void
): Promise<void> {
  reader = new BrowserMultiFormatReader()
  const devices = await reader.listVideoInputDevices()
  const back = devices.find(d =>
    d.label.toLowerCase().includes('back') ||
    d.label.toLowerCase().includes('rear')
  )
  const deviceId = back?.deviceId ?? devices[0]?.deviceId
  await reader.decodeFromVideoDevice(deviceId, videoEl, (result, err) => {
    if (result) onResult(result.getText())
  })
}

export function stopScanner() {
  if (reader) {
    reader.stopAsyncDecode()
    reader = null
  }
}

export function parseQR(content: string) {
  if (/wxp:\/\/|wechat|微信/.test(content)) return { type: 'wechat' as const, raw: content }
  if (/alipay:\/\/|alipay|支付宝/.test(content)) return { type: 'alipay' as const, raw: content }
  return { type: 'other' as const, raw: content }
}
