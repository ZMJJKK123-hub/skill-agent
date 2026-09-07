/**
 * 图片附件工具：压缩编码 + 数量上限。
 * 由 conversation.tsx 原样迁出，行为不变。
 */

/** 每条消息最多携带的图片数（与后端 /api/task 的 images 上限一致） */
export const MAX_IMAGES_PER_MESSAGE = 4

/** 图片文件 → data URL：小图（≤600KB）原样返回；
 *  大图 canvas 缩放到 1280 内并转 JPEG 0.85，控制上传与 token 体积 */
export async function fileToDataUrl(file: File): Promise<string> {
  const raw = await new Promise<string>((resolve, reject) => {
    const r = new FileReader()
    r.onload = () => resolve(String(r.result))
    r.onerror = () => reject(new Error('读取图片失败'))
    r.readAsDataURL(file)
  })
  if (file.size <= 600 * 1024) return raw
  try {
    const img = await new Promise<HTMLImageElement>((resolve, reject) => {
      const im = new Image()
      im.onload = () => resolve(im)
      im.onerror = () => reject(new Error('解析图片失败'))
      im.src = raw
    })
    const scale = Math.min(1, 1280 / Math.max(img.width, img.height))
    if (scale >= 1) return raw
    const canvas = document.createElement('canvas')
    canvas.width = Math.round(img.width * scale)
    canvas.height = Math.round(img.height * scale)
    const ctx = canvas.getContext('2d')
    if (!ctx) return raw
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
    return canvas.toDataURL('image/jpeg', 0.85)
  } catch {
    return raw
  }
}
