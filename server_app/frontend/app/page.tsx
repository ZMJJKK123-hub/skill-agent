"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Navbar from "../components/common_ui/Navbar";
import Hero from "../components/common_ui/Hero";
import Stepper from "../components/common_ui/Stepper";
import ConfigureStep from "../components/mc_ui/ConfigureStep";
import PromptStep from "../components/mc_ui/PromptStep";
import GenerateStep from "../components/common_ui/GenerateStep";
import HistoryView from "../components/common_ui/HistoryView";
import AuthModal from "../components/common_ui/AuthModal";
import VoxelBackground from "../components/mc_ui/VoxelBackground";
import MouseEffect from "../components/common_ui/MouseEffect";
import { ToastProvider, useToast } from "../components/common_ui/Toast";
import * as API from "../lib/api";
import { useSessionPolling } from "../lib/useSessionPolling";
import { saveHistory } from "../lib/history";
import { checkSession, logout } from "../lib/auth";

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
  /** 保存配置页已填内容：返回配置页时回显（需求 page 返回后不重输） */
  const [savedApiKey, setSavedApiKey] = useState("");
  const [savedLoader, setSavedLoader] = useState("");
  const [savedVersion, setSavedVersion] = useState("");
  const [user, setUser] = useState<string | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  /** 保存需求页已填的 MOD 需求：返回/重新生成后保留 */
  const [savedPrompt, setSavedPrompt] = useState("");

  // 轮询 Hook：事件流 + 状态（去重、AbortController、800ms）
  const polling = useSessionPolling();

  // 组件实例级的最后一次 prompt（历史记录保存用）
  const lastPrompt = useRef("");

  // 会话超时清理：创建会话后未开始任务，10 分钟后删除并回退
  const cleanupTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearCleanupTimer = useCallback(() => {
    if (cleanupTimer.current) {
      clearTimeout(cleanupTimer.current);
      cleanupTimer.current = null;
    }
  }, []);

  const deleteSessionAndReset = useCallback(
    (sid: string, silent: boolean) => {
      clearCleanupTimer();
      API.deleteSession(sid).catch(() => undefined);
      setStep(1);
      setSessionId(null);
      setView("workbench");
      polling.clear();
      if (!silent) toast("会话已超时，自动清理");
    },
    [clearCleanupTimer, polling, toast]
  );

  // 启动时恢复登录态（token 有效则免登）；未登录时自动弹出登录框（可关闭浏览）
  useEffect(() => {
    checkSession()
      .then((name) => {
        if (name) {
          setUser(name);
          setAuthOpen(false);
        } else {
          setAuthOpen(true);
        }
      })
      .finally(() => setAuthChecked(true));
  }, []);

  // 加载游戏模板（仅挂载一次）
  useEffect(() => {
    API.getGames()
      .then((data) => {
        if (data?.games?.length) setGames(data.games);
      })
      .catch(() => toast("游戏模板加载失败", "warn"));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCreated = useCallback(
    (apiKey: string, selectedGame: string, loader?: string, version?: string) => {
      const g = selectedGame || game;
      setGame(g);
      // 保存配置内容，返回配置页时回显
      setSavedApiKey(apiKey);
      setSavedLoader(loader ?? "");
      setSavedVersion(version ?? "");
      return API.createSession(apiKey, g, loader ?? "", version ?? "").then((res) => {
        setSessionId(res.session_id);
        setStep(2);
        clearCleanupTimer();
        cleanupTimer.current = setTimeout(() => {
          deleteSessionAndReset(res.session_id, false);
        }, 10 * 60 * 1000);
        toast("会话创建成功");
      });
    },
    [game, toast, clearCleanupTimer, deleteSessionAndReset]
  );
  const handleRun = useCallback(
    async (prompt: string) => {
      if (!sessionId) return;
      lastPrompt.current = prompt;
      await API.startTask(sessionId, prompt);
      polling.clear();
      polling.start(sessionId);
      setStep(3);
      clearCleanupTimer();
      toast("生成任务已启动");
    },
    [sessionId, polling, toast, clearCleanupTimer]
  );

  // 复用历史会话：hydrate 一次性灌入历史事件+状态；
  // 运行中自动续轮询，已完成静态展示；lastPrompt 清空避免复用被误记历史
  const handleResume = useCallback(
    async (sid: string) => {
      try {
        await polling.hydrate(sid);
        setSessionId(sid);
        setView("workbench");
        setStep(3);
        lastPrompt.current = "";
        clearCleanupTimer();
        setHistoryVersion((v) => v + 1);
        toast("已复用会话");
      } catch (err) {
        toast(err instanceof Error ? err.message : "复用会话失败", "error");
      }
    },
    [polling, toast, clearCleanupTimer]
  );

  // 返回首页（彻底清场）
  const handleHome = useCallback(() => {
    clearCleanupTimer();
    polling.clear();
    setStep(1);
    setSessionId(null);
    setView("workbench");
    setHistoryVersion((v) => v + 1);
  }, [polling, clearCleanupTimer]);

  // 重新生成 = 重置本次会话（保留 session_id/API Key，清空产物回复初始）+ 回需求页
  const handleRegenerate = useCallback(
    async (sid: string) => {
      clearCleanupTimer();
      polling.clear();
      try {
        await API.resetSession(sid);
      } catch {
        /* 网络失败不阻塞，仍回需求页 */
      }
      setStep(2);
    },
    [polling, clearCleanupTimer]
  );

  // 登录/注册成功（AuthModal 回调）
  const handleAuthed = useCallback(
    (name: string) => {
      setUser(name);
      setAuthOpen(false);
      setHistoryVersion((v) => v + 1);
      toast(`欢迎，${name}`);
    },
    [toast]
  );

  // 退出登录：清空本地 token 与页面状态
  const handleLogout = useCallback(async () => {
    await logout();
    clearCleanupTimer();
    polling.clear();
    setUser(null);
    setView("workbench");
    setStep(1);
    setSessionId(null);
    setHistoryVersion((v) => v + 1);
  }, [polling, clearCleanupTimer]);

  // 检测轮询中任务完成 → 写入历史（真正的 useEffect：deps 变化才触发）
  useEffect(() => {
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
  }, [polling.finished, polling.sessionId, polling.status, game]);

  return (
    <div className="relative min-h-screen">
      <VoxelBackground />
      <MouseEffect selectedGame={game} />

      {/* 登录/注册弹窗（首次访问自动弹，也可点右上角按钮打开；可关闭浏览） */}
      {authOpen && (
        <AuthModal
          key={authMode}
          initialMode={authMode}
          onAuthed={handleAuthed}
          onClose={() => setAuthOpen(false)}
        />
      )}

      <div className="relative z-10 flex min-h-screen flex-col">
        <Navbar
          active={view}
          onChange={setView}
          username={user}
          onLoginClick={() => {
            setAuthMode("login");
            setAuthOpen(true);
          }}
          onRegisterClick={() => {
            setAuthMode("register");
            setAuthOpen(true);
          }}
          onLogout={handleLogout}
        />

        <main className="mx-auto w-full max-w-6xl flex-1 px-5 pb-16">
          <Hero />

          {view === "workbench" && (
            <>
              <Stepper current={step} />

              {step === 1 && (
                <ConfigureStep
                  games={games}
                  onCreateSession={handleCreated}
                  savedApiKey={savedApiKey}
                  savedLoader={savedLoader}
                  savedVersion={savedVersion}
                />
              )}
              {step === 2 && sessionId && (
                <PromptStep
                  sessionId={sessionId}
                  onBack={() => deleteSessionAndReset(sessionId, true)}
                  onRun={handleRun}
                  value={savedPrompt}
                  onChange={setSavedPrompt}
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
                  onRegenerate={() => handleRegenerate(sessionId)}
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
      </div>
    </div>
  );
}

/** 兜底游戏列表（接口加载失败时使用） */
const API_GAMES_FALLBACK = [
  { id: "minecraft", name: "minecraft", description: "" },
];

export default function Page() {
  return (
    <ToastProvider>
      <AppInner />
    </ToastProvider>
  );
}