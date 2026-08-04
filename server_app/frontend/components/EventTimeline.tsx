import { Braces, Circle, Cpu, FileText, ListChecks } from "lucide-react";
import type { AgentEvent, AgentEventType } from "../lib/types";

/** 事件类型 → Lucide 图标 */
const TYPE_ICON: Record<string, typeof Cpu> = {
  thinking: Cpu,
  tool_call: Braces,
  todo: ListChecks,
  round: Circle,
  system: FileText,
};

/** 事件类型 → 中文标签 */
const TYPE_LABEL: Record<string, string> = {
  thinking: "思考",
  tool_call: "工具调用",
  todo: "待办",
  round: "回合",
  system: "系统",
  background: "后台",
  teammate_report: "队友汇报",
  protocol: "协议",
  worktree: "工作树",
  log: "日志",
};

/** 从工具事件文本提取工具名："write_file | 参数..." → "write_file" */
function parseToolText(content: string): string {
  const idx = content.indexOf("|");
  if (idx === -1) return content.trim().slice(0, 40);
  return content.slice(0, idx).trim();
}

/** 事件详细内容（第二个字段） */
function parseToolArgs(content: string): string {
  const idx = content.indexOf("|");
  return idx === -1 ? "" : content.slice(idx + 1).trim();
}

/** 事件类型 → 图标颜色类（思考=琥珀 / 工具=蓝 / 待办=绿 / 其余灰） */
function iconColor(type: AgentEventType): string {
  switch (type) {
    case "thinking":
      return "text-amber-400/80";
    case "tool_call":
      return "text-blue-400/80";
    case "todo":
      return "text-forge-emerald";
    case "round":
      return "text-zinc-500";
    default:
      return "text-zinc-600";
  }
}

/** 检测事件内容是否含错误关键词（回报错的部分用暗红渲染） */
const ERROR_PATTERN =
  /(error|exception|failed|failed:|失败|报错|错误|Traceback|Error)/i;

function isErrorEvent(ev: AgentEvent): boolean {
  if (ERROR_PATTERN.test(ev.content)) return true;
  return false;
}

function SkeletonEvents() {
  return (
    <div className="space-y-2 p-3">
      {[0, 1, 2].map((i) => (
        <div key={i} className="skeleton h-9 rounded-lg" />
      ))}
    </div>
  );
}

interface EventTimelineProps {
  events: AgentEvent[];
  loading: boolean;
}

export default function EventTimeline({ events, loading }: EventTimelineProps) {
  if (loading && events.length === 0) return <SkeletonEvents />;

  if (events.length === 0) {
    return (
      <div className="flex h-full min-h-[240px] items-center justify-center">
        <div className="flex items-center gap-2 font-mono text-sm text-zinc-600">
          <span className="h-2 w-2 animate-pulseSoft rounded-full bg-forge-emerald" />
          等待智能体输出
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-1.5 p-3 font-mono !text-[12.5px]">
      {events.map((ev, idx) => {
        const Icon = TYPE_ICON[ev.type] || FileText;
        const isTool = ev.type === "tool_call";
        const label = TYPE_LABEL[ev.type] || ev.type;
        const isErr = isErrorEvent(ev);

        return (
          <div key={`${ev.id}-${idx}`} className="group animate-fadeUp">
            <div
              className={[
                "flex items-start gap-2 rounded-md px-2 py-1.5 transition-colors",
                isErr
                  ? "bg-rose-500/[0.04] hover:bg-rose-500/[0.08]"
                  : "hover:bg-white/[0.03]",
              ].join(" ")}
            >
              <Icon
                size={13}
                className={`mt-0.5 shrink-0 ${
                  isErr ? "text-rose-400/80" : iconColor(ev.type)
                }`}
              />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span
                    className={
                      isErr
                        ? "text-rose-300/90"
                        : ev.type === "log"
                          ? "text-zinc-500"
                          : "text-zinc-300"
                    }
                  >
                    {label}
                  </span>
                  {ev.peer && (
                    <span className="rounded-full bg-forge-purple/15 px-1.5 py-0.5 text-[10px] text-forge-purple">
                      {ev.peer}
                    </span>
                  )}
                  {ev.source === "agent" && (
                    <span className="rounded-full bg-white/5 px-1.5 py-0.5 text-[10px] text-zinc-600">
                      agent
                    </span>
                  )}
                </div>

                {isTool ? (
                  <div className={isErr ? "mt-0.5 break-all text-rose-300/80" : "mt-0.5 break-all text-zinc-400"}>
                    <span className={isErr ? "text-rose-300/90" : "text-forge-cyan/80"}>
                      {parseToolText(ev.content)}
                    </span>
                    {parseToolArgs(ev.content) && (
                      <span className={isErr ? "text-rose-300/60" : "text-zinc-500"}>
                        {" "}
                        · {parseToolArgs(ev.content).slice(0, 80)}
                      </span>
                    )}
                  </div>
                ) : (
                  <div
                    className={
                      isErr
                        ? "mt-0.5 whitespace-pre-wrap break-words text-rose-300/80"
                        : "mt-0.5 whitespace-pre-wrap break-words text-zinc-400"
                    }
                  >
                    {ev.content}
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}