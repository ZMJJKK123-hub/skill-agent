/**
 * McTerminal —— MC 原版终端板块。
 * 头部（标题 + 事件计数）+ 事件列表（thinking 琥珀 / tool_call 蓝 / done 绿）+ 空态闪烁点。
 * 使用现有 AgentEvent 类型，替代被移除的 EventTimeline。
 */
"use client";

import type { AgentEvent } from "../../../lib/types";

interface McTerminalProps {
  events: AgentEvent[];
  loading: boolean;
}

/** 从工具事件内容提取工具名："write_file | 参数..." → "write_file"（调试需要：不截断） */
function parseToolText(content: string): string {
  const idx = content.indexOf("|");
  if (idx === -1) return content.trim();
  return content.slice(0, idx).trim();
}

/** 事件详细信息（第二个字段，完整保留） */
function parseToolArgs(content: string): string {
  const idx = content.indexOf("|");
  return idx === -1 ? "" : content.slice(idx + 1).trim();
}

export default function McTerminal({ events, loading }: McTerminalProps) {
  return (
    <div
      className="flex h-[640px] flex-col"
      style={{ background: "#0D0D0D", border: "2px solid #373737" }}
    >
      {/* 头部 */}
      <div
        className="flex items-center gap-2 px-3 py-2"
        style={{ background: "rgba(0,0,0,0.5)", borderBottom: "1px solid rgba(255,255,255,0.05)" }}
      >
        <span style={{ fontWeight: 700, fontSize: 14 }}>智能体工作台</span>
        <span className="ml-auto" style={{ fontSize: 12, color: "#808090" }}>
          {events.length} 事件
        </span>
      </div>

      {/* 事件体 */}
      <div className="flex flex-1 flex-col gap-1 overflow-y-auto p-2" style={{ fontSize: 14 }}>
        {loading && events.length === 0 && (
          <div
            className="flex h-full items-center justify-center gap-1.5"
            style={{ color: "#525252" }}
          >
            <span
              style={{ width: 5, height: 5, background: "#7EFC20", borderRadius: "50%", animation: "mcBlink 1.5s infinite" }}
            />
            等待智能体输出...
          </div>
        )}

        {events.length === 0 && !loading && (
          <div
            className="flex h-full items-center justify-center gap-1.5"
            style={{ color: "#525252" }}
          >
            <span
              style={{ width: 5, height: 5, background: "#7EFC20", borderRadius: "50%", animation: "mcBlink 1.5s infinite" }}
            />
            等待智能体输出...
          </div>
        )}

        {events.map((ev, idx) => (
          <div key={`${ev.id}-${idx}`} className="px-1.5 py-[3px]" style={{ animation: "mcEvIn .25s ease" }}>
            {ev.type === "thinking" && (
              <span>
                <span style={{ color: "#F59E0B" }}>🧠 思考</span>
                <span style={{ color: "#BFBFBF" }}> · {ev.content}</span>
              </span>
            )}
            {ev.type === "tool_call" && (
              <span>
                <span style={{ color: "#60A5FA" }}>🔧 工具调用</span>
                <span style={{ color: "#BFBFBF" }}> · </span>
                <span style={{ color: "#22D3EE" }}>{parseToolText(ev.content)}</span>
                {parseToolArgs(ev.content) && (
                  <span style={{ color: "#808090" }}> · {parseToolArgs(ev.content)}</span>
                )}
              </span>
            )}
            {ev.type === "todo" && (
              <span style={{ color: "#34D399" }}>
                📋 待办
                <span style={{ color: "#BFBFBF" }}> · {ev.content}</span>
              </span>
            )}
            {(ev.type === "log" || ev.type === "round" || ev.type === "system") && (
              <span style={{ color: "#BFBFBF" }}>
                {ev.type === "system" ? "ℹ️ " : ev.type === "round" ? "🔄 " : ""}[{ev.type}] {ev.content}
              </span>
            )}
            {(ev.type === "background" || ev.type === "teammate_report" ||
              ev.type === "protocol" || ev.type === "worktree") && (
              <span style={{ color: "#808090" }}>
                [{ev.type}] {ev.content}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}