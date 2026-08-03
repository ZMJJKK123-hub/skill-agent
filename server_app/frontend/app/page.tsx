"use client";

import { useCallback, useRef, useState } from "react";
import Navbar from "../components/Navbar";
import Hero from "../components/Hero";
import Stepper from "../components/Stepper";
import ConfigureStep from "../components/ConfigureStep";
import PromptStep from "../components/PromptStep";
import GenerateStep from "../components/GenerateStep";
import HistoryView from "../components/HistoryView";
import VoxelBackground from "../components/VoxelBackground";
import { ToastProvider, useToast } from "../components/Toast";
import * as API from "../lib/api";
import { useSessionPolling } from "../lib/useSessionPolling";
import { saveHistory } from "../lib/history";

type View = "workbench" | "history";
type Step = 1 | 2 | 3;

function AppInner() {
  const toast = useToast();

  const [view, setView] = useState<View>("workbench");
  const [step, setStep] = useState<Step>(1);
  const [games, setGames] = useState(API_GAMES_FALLBACK);
  const [game, setGame] = useState("minecraft");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [historyVersion, setHistoryVersion] = useState(0);

  // 轮询 Hook：事件流 + 状态（去重、AbortController、800ms）
  const polling = useSessionPolling();

  // 组件实例级的最后一次 prompt（历史记录保存用）
  const lastPrompt = useRef("");

  // 加载游戏模板
  const [gamesLoaded, setGamesLoaded] = useState(false);
  useMemoInit(
    () => {
      if (gamesLoaded) return;
      setGamesLoaded(true);
      API.getGames()
        .then((data) => {
          if (data?.games?.length) setGames(data.games);
        })
        .catch(() => toast("游戏模板加载失败", "warn"));
    },
    [gamesLoaded, toast]
  );

  const handleCreated = useCallback(
    (apiKey: string, selectedGame: string) => {
      const g = selectedGame || game;
      setGame(g);
      return API.createSession(apiKey, g).then((res) => {
        setSessionId(res.session_id);
        setStep(2);
        toast("会话创建成功");
      });
    },
    [game, toast]
  );

  const handleRun = useCallback(
    async (prompt: string) => {
      if (!sessionId) return;
      lastPrompt.current = prompt;
      await API.startTask(sessionId, prompt);
      polling.clear();
      polling.start(sessionId);
      setStep(3);
      toast("生成任务已启动");
    },
    [sessionId, polling, toast]
  );

  // 复用历史会话
  const handleResume = useCallback(
    async (sid: string) => {
      try {
        const st = await API.getSession(sid);
        setSessionId(sid);
        setView("workbench");
        setStep(3);
        if (st.state === "running") {
          polling.clear();
          polling.start(sid);
        } else {
          // 已完成的会话直接展示产物（不重复记录历史）
          polling.clear();
        }
        setHistoryVersion((v) => v + 1);
        toast("已复用会话");
      } catch (err) {
        toast(err instanceof Error ? err.message : "复用会话失败", "error");
      }
    },
    [polling, toast]
  );

  // 返回首页（彻底清场）
  const handleHome = useCallback(() => {
    polling.clear();
    setStep(1);
    setSessionId(null);
    setView("workbench");
    setHistoryVersion((v) => v + 1);
  }, [polling]);

  // 重新生成 = 回到需求页
  const handleRegenerate = useCallback(() => {
    polling.clear();
    setStep(2);
  }, [polling]);

  // 检测轮询中任务完成 → 写入历史（仅自然完成触发一次）
  useMemoInit(
    () => {
      if (!polling.finished || !polling.sessionId) return;
      if (lastPrompt.current === "") return;
      saveHistory({
        sessionId: polling.sessionId,
        game,
        prompt: lastPrompt.current,
        elapsed: polling.status?.elapsed ?? null,
        fileCount: polling.status?.file_count ?? null,
        date: new Date().toLocaleString("zh-CN", { hour12: false }),
      });
      lastPrompt.current = ""; // 防重复记录
      setHistoryVersion((v) => v + 1);
    },
    [polling.finished, polling.sessionId, polling.status, game]
  );

  return (
    <div className="relative min-h-screen">
      <VoxelBackground />

      <div className="relative z-10 flex min-h-screen flex-col">
        <Navbar active={view} onChange={setView} />

        <main className="mx-auto w-full max-w-6xl flex-1 px-5 pb-16">
          <Hero />

          {view === "workbench" && (
            <>
              <Stepper current={step} />

              {step === 1 && (
                <ConfigureStep games={games} onCreateSession={handleCreated} />
              )}
              {step === 2 && sessionId && (
                <PromptStep
                  sessionId={sessionId}
                  onBack={() => setStep(1)}
                  onRun={handleRun}
                />
              )}
              {step === 3 && sessionId && (
                <GenerateStep
                  sessionId={sessionId}
                  game={game}
                  events={polling.events}
                  status={polling.status}
                  running={polling.running}
                  finished={polling.finished}
                  onHome={handleHome}
                  onRegenerate={handleRegenerate}
                />
              )}
            </>
          )}

          {view === "history" && (
            <HistoryView
              key={historyVersion}
              onResume={handleResume}
              onClear={() => setHistoryVersion((v) => v + 1)}
            />
          )}
        </main>

        <footer className="border-t border-white/5 py-6 text-center">
          <div className="mb-3 flex flex-wrap justify-center gap-2">
            {["FastAPI", "DeepSeek", "Agent Core", "React"].map((t) => (
              <span
                key={t}
                className="rounded-full border border-white/5 bg-white/[0.03] px-3 py-0.5 text-xs text-zinc-500"
              >
                {t}
              </span>
            ))}
          </div>
          <p className="text-xs text-zinc-600">
            生成的产物仅供学习与本地使用，API Key 不落盘、不共享。
          </p>
        </footer>
      </div>
    </div>
  );
}

/** 兜底游戏列表（接口加载失败时使用） */
const API_GAMES_FALLBACK = [
  { id: "minecraft", name: "minecraft", description: "" },
];

/** 极简 useEffect 封装：仅在依赖变化时执行一次副作用 */
function useMemoInit(fn: () => void, deps: unknown[]) {
  const ref = useRef(false);
  if (!ref.current) {
    ref.current = true;
    fn();
  }
  void deps;
}

export default function Page() {
  return (
    <ToastProvider>
      <AppInner />
    </ToastProvider>
  );
}