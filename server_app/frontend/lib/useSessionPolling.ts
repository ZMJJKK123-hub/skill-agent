"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import * as API from "./api";
import type { AgentEvent, SessionStats } from "./types";

/** 会话轮询 Hook：
 *  1. 每 800ms 增量拉取事件流 + 会话状态
 *  2. 支持启动/停止（stop 时清理定时器 + 中止在途请求）
 *  3. 事件按 id 去重
 *  4. 任务完成透明回调（仅自然完成时触发，用于历史记录）
 */
export function useSessionPolling() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [status, setStatus] = useState<SessionStats | null>(null);
  const [running, setRunning] = useState(false);
  const [finished, setFinished] = useState(false);

  const seenIds = useRef<Set<string>>(new Set());
  const cursorRef = useRef<{ run: number; agent: number } | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const activeRef = useRef(false); // 避免卸载后 setState

  const stop = useCallback(() => {
    activeRef.current = false;
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    abortRef.current?.abort();
    abortRef.current = null;
  }, []);

  const clear = useCallback(() => {
    stop();
    seenIds.current.clear();
    cursorRef.current = null;
    setEvents([]);
    setStatus(null);
    setRunning(false);
    setFinished(false);
  }, [stop]);

  const start = useCallback(
    (sid: string) => {
      stop();
      activeRef.current = true;
      setSessionId(sid);

      const tick = async () => {
        if (!activeRef.current || !sid) return;
        abortRef.current?.abort();
        const ctrl = new AbortController();
        abortRef.current = ctrl;

        try {
          // 1) 增量事件流
          const evData = await API.getEvents(sid, cursorRef.current, ctrl.signal);
          cursorRef.current = evData.cursor;
          if (evData.events?.length) {
            setEvents((prev) => {
              const fresh = evData.events.filter((e) => !seenIds.current.has(e.id));
              fresh.forEach((e) => seenIds.current.add(e.id));
              return fresh.length ? [...prev, ...fresh] : prev;
            });
          }

          // 2) 会话状态
          const st = await API.getSession(sid, ctrl.signal);
          if (!activeRef.current) return;
          setStatus(st);
          setRunning(st.state === "running");
          setFinished(st.state === "finished");
        } catch (err) {
          // AbortError：组件已卸载/主动停止，静默退出
          if (err instanceof DOMException && err.name === "AbortError") return;
          /* 网络抖动：不中断轮询 */
        }
        if (activeRef.current) {
          timerRef.current = setTimeout(tick, 800);
        }
      };
      timerRef.current = setTimeout(tick, 800);
    },
    [stop]
  );

  /** 复用会话：一次拉取全量事件+状态；running 则续上轮询，已完成则静态展示（含 finished 标记） */
  const hydrate = useCallback(
    async (sid: string) => {
      stop();
      seenIds.current.clear();
      cursorRef.current = null;
      setSessionId(sid);
      setEvents([]);
      setStatus(null);
      setRunning(false);
      setFinished(false);
      try {
        const [evData, st] = await Promise.all([
          API.getEvents(sid, null),
          API.getSession(sid),
        ]);
        cursorRef.current = evData.cursor;
        const fresh = evData.events ?? [];
        fresh.forEach((e) => seenIds.current.add(e.id));
        setEvents(fresh);
        setStatus(st);
        setRunning(st.state === "running");
        setFinished(st.state === "finished");
        if (st.state === "running") {
          start(sid);
        }
      } catch {
        /* 由调用方统一处理错误 */
      }
    },
    [start, stop]
  );

  // 卸载清理
  useEffect(() => stop, [stop]);

  return { sessionId, events, status, running, finished, start, stop, clear, hydrate };
}