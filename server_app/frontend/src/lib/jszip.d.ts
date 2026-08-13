// jszip 无内置类型声明，这里给一个最小声明满足 tsc
declare module 'jszip' {
  interface JSZip {
    file(path: string, data: Uint8Array | string | Blob): JSZip
    generateAsync(options: { type: 'blob' }): Promise<Blob>
  }
  const JSZip: new () => JSZip
  export default JSZip
}
