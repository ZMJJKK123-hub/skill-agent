// 插画使用本地 SVG 图形，避免远程图片和额外资源加载。
import type { ReactElement } from 'react'

/** 展示欢迎页的悬浮方块与等距网格，不接收输入、不挂载全局接口。
 * Args: None。Returns: 仅用于装饰、对辅助技术隐藏的 SVG。
 * Globals Used: None。Dependencies: 当前主题 CSS 令牌；无请求或错误分支。
 */
export function ForgeScene(): ReactElement {
  return (
    <svg className="forge-scene" viewBox="0 0 320 200" fill="none" aria-hidden="true" focusable="false">
      <ellipse cx="160" cy="152" rx="124" ry="35" className="scene-orbit" />
      <ellipse cx="160" cy="152" rx="93" ry="25" className="scene-orbit" />
      <path d="m52 141 108-59 108 59-108 59L52 141Zm27-15 108 59m-81-74 108 59m-81-74 108 59m-54-59L79 185m135-74L106 170m135-44-108 59" className="scene-grid" />
      <g className="scene-platform">
        <path d="m94 132 66-37 66 37-66 38-66-38Z" fill="var(--cube-top)" opacity=".15" />
        <path d="m94 132 66 38v14l-66-38v-14Z" fill="var(--cube-left)" opacity=".2" />
        <path d="m160 170 66-38v14l-66 38v-14Z" fill="var(--cube-right)" opacity=".4" />
        <path d="m94 132 66 38 66-38M160 170v14" stroke="var(--accent)" strokeOpacity=".2" />
      </g>
      <g className="scene-main-block">
        <path d="m160 36 48 27-48 28-48-28 48-27Z" fill="var(--cube-top)" />
        <path d="m112 63 48 28v55l-48-28V63Z" fill="var(--cube-left)" />
        <path d="m160 91 48-28v55l-48 28V91Z" fill="var(--cube-right)" />
        <path d="m112 63 48 28 48-28M160 91v55" stroke="#d8ffe7" strokeOpacity=".45" />
        <path d="m136 50 48 27m-48 0 48-27M128 72v14l16 9v15l16 9m16-37v15l16-9v15l16-9" stroke="#d2ffe0" strokeOpacity=".22" strokeWidth="2" />
        <path d="m115 92 13 8v15l-13-8V92Zm29 18 13 8v16l-13-8v-16Z" fill="#284d3d" opacity=".25" />
        <path d="m163 108 14-8v15l-14 8v-15Zm29-18 13-8v16l-13 8V90Z" fill="#183b30" opacity=".3" />
        <path d="m160 36 48 27v55l-48 28-48-28V63l48-27Z" stroke="var(--accent)" strokeOpacity=".45" />
      </g>
      <g className="scene-small-block">
        <path d="m73 91 16 9-16 10-17-10 17-9Z" fill="#d3c398" />
        <path d="m56 100 17 10v19l-17-10v-19Z" fill="#a69772" />
        <path d="m73 110 16-10v19l-16 10v-19Z" fill="#756f55" />
      </g>
      <g opacity=".7">
        <path d="m243 111 12 7-12 7-12-7 12-7Z" fill="var(--cube-top)" />
        <path d="m231 118 12 7v14l-12-7v-14Z" fill="var(--cube-left)" />
        <path d="m243 125 12-7v14l-12 7v-14Z" fill="var(--cube-right)" />
      </g>
      <path d="M243 59v12m-6-6h12M91 44v8m-4-4h8" stroke="var(--accent)" strokeOpacity=".6" />
      <circle cx="216" cy="33" r="2" fill="var(--accent)" opacity=".4" />
      <circle cx="103" cy="151" r="1.5" fill="var(--accent)" opacity=".6" />
      <path d="m160 9 3 5-3 5-3-5 3-5Z" fill="var(--accent)" opacity=".55" />
    </svg>
  )
}
