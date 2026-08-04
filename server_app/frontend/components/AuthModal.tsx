"use client";

import { useState } from "react";
import { Eye, EyeOff, KeyRound, Loader2, LogIn, UserPlus, UserRound } from "lucide-react";
import { login, register } from "../lib/auth";

interface AuthModalProps {
  /** 登录/注册成功后回调（携带用户名） */
  onAuthed: (username: string) => void;
}

export default function AuthModal({ onAuthed }: AuthModalProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const switchMode = (m: "login" | "register") => {
    setMode(m);
    setError("");
    setConfirmPwd("");
  };

  async function handleSubmit() {
    if (!username.trim()) {
      setError("请输入用户名");
      return;
    }
    if (password.length < 6) {
      setError("密码至少 6 位");
      return;
    }
    if (mode === "register" && confirmPwd !== password) {
      setError("两次输入的密码不一致");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data =
        mode === "login"
          ? await login(username.trim(), password)
          : await register(username.trim(), password);
      onAuthed(data.username);
    } catch (err) {
      setError(err instanceof Error ? err.message : "操作失败，请重试");
    } finally {
      setLoading(false);
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSubmit();
  };

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center bg-zinc-950/80 backdrop-blur-sm">
      {/* 中央玻璃卡片 */}
      <div className="glass w-full max-w-sm p-8 !bg-ink-900/70">
        {/* 徽标 */}
        <div className="mb-6 flex flex-col items-center gap-3">
          <div className="grid h-14 w-14 place-items-center rounded-xl bg-gradient-to-br from-forge-cyan to-forge-emerald shadow-lg shadow-forge-cyan/25">
            <KeyRound size={26} className="text-ink-950" />
          </div>
          <h1 className="text-lg font-bold text-zinc-100">MOD Forge</h1>
          <p className="font-mono text-xs text-zinc-500">
            {mode === "login" ? "登录以继续" : "创建一个新账号"}
          </p>
        </div>

        {/* Tab 切换 */}
        <div className="mb-6 grid grid-cols-2 gap-1 rounded-full border border-white/5 bg-white/[0.03] p-1">
          <button
            onClick={() => switchMode("login")}
            className={`flex items-center justify-center gap-1.5 rounded-full px-3 py-1.5 text-sm transition-all duration-200 ${
              mode === "login"
                ? "bg-white/10 text-zinc-100 shadow-sm"
                : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            <LogIn size={14} />
            登录
          </button>
          <button
            onClick={() => switchMode("register")}
            className={`flex items-center justify-center gap-1.5 rounded-full px-3 py-1.5 text-sm transition-all duration-200 ${
              mode === "register"
                ? "bg-white/10 text-zinc-100 shadow-sm"
                : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            <UserPlus size={14} />
            注册
          </button>
        </div>

        {/* 表单 */}
        <div className="space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium text-zinc-400">用户名</label>
            <div className="relative">
              <UserRound
                size={16}
                className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-zinc-600"
              />
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="输入用户名"
                autoComplete="username"
                spellCheck={false}
                className="input-forge pl-9"
                aria-label="用户名"
              />
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-zinc-400">密码</label>
            <div className="relative">
              <KeyRound
                size={16}
                className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-zinc-600"
              />
              <input
                type={showPwd ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={mode === "register" ? "至少 6 位" : "输入密码"}
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                className="input-forge pl-9 pr-10"
                aria-label="密码"
              />
              <button
                type="button"
                onClick={() => setShowPwd((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 transition-colors hover:text-zinc-300"
                aria-label={showPwd ? "隐藏密码" : "显示密码"}
              >
                {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {mode === "register" && (
            <div>
              <label className="mb-2 block text-sm font-medium text-zinc-400">
                确认密码
              </label>
              <div className="relative">
                <KeyRound
                  size={16}
                  className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-zinc-600"
                />
                <input
                  type={showPwd ? "text" : "password"}
                  value={confirmPwd}
                  onChange={(e) => setConfirmPwd(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="再次输入密码"
                  autoComplete="new-password"
                  className="input-forge pl-9 pr-10"
                  aria-label="确认密码"
                />
                <button
                  type="button"
                  onClick={() => setShowPwd((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 transition-colors hover:text-zinc-300"
                  aria-label={showPwd ? "隐藏密码" : "显示密码"}
                >
                  {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2.5 text-sm text-red-400">
              {error}
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="btn-primary w-full"
          >
            {loading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : mode === "login" ? (
              <LogIn size={16} />
            ) : (
              <UserPlus size={16} />
            )}
            {mode === "login" ? "登录" : "注册"}
          </button>
        </div>

        <p className="mt-6 text-center text-xs text-zinc-600">
          每个账号的历史记录与生成产物相互隔离
        </p>
      </div>
    </div>
  );
}