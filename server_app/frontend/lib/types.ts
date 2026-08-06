/** 全局类型定义 —— 唯一事实来源 */

export interface Game {
  id: string;
  name: string;
  description: string;
}

export type SessionState = "pending" | "running" | "finished";

export interface SessionStats {
  session_id: string;
  state: SessionState;
  running: boolean;
  finished: boolean;
  started_at: number | null;
  finished_at: number | null;
  elapsed: number | null;
  file_count: number | null;
  total_bytes: number | null;
  /** 是否已打包出可安装的 jar（mod/dist/*.jar 存在） */
  has_jar?: boolean;
}

export type AgentEventType =
  | "thinking"
  | "tool_call"
  | "todo"
  | "round"
  | "system"
  | "background"
  | "teammate_report"
  | "protocol"
  | "worktree"
  | "log";

export interface AgentEvent {
  id: string;
  ts: number;
  type: AgentEventType;
  source: string;
  content: string;
  peer?: string;
  tool?: string;
}

export interface EventStream {
  events: AgentEvent[];
  cursor: { run: number; agent: number };
}

export interface TreeNode {
  name: string;
  path: string;
  type: "dir" | "file";
  size?: number;
  children?: TreeNode[];
}

export interface FileTree {
  session_id: string;
  tree: TreeNode;
}

export interface FilePreview {
  session_id: string;
  path: string;
  content: string;
  truncated: boolean;
  size: number;
}

export interface HistoryEntry {
  sessionId: string;
  game: string;
  prompt: string;
  elapsed: number | null;
  fileCount: number | null;
  date: string;
  /** 服务端注入：该会话是否已打包 jar */
  has_jar?: boolean;
}
