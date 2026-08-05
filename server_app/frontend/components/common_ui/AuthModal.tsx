"use client";

import { useState } from "react";
import { Eye, EyeOff, KeyRound, Loader2, LogIn, UserPlus, UserRound, X } from "lucide-react";
import { login, register } from "../../lib/auth";

interface AuthModalProps {
  /** 登录/注册成功后回调（携带用户名） */
  onAuthed: (username: string) => void;
  /** 关闭弹窗（点遮罩/×）回调 */
  onClose: () => void;
  /** 初始 Tab（登录/注册按钮手动打开时指定，默认登录） */
  initialMode?: "login" | "register";
}

export default function AuthModal({ onAuthed, onClose, initialMode }: AuthModalProps) {
  const [mode, setMode] = useState<"login" | "register">(initialMode ?? "login");
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
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center bg-zinc-950/80 backdrop-blur-sm"
      onClick={onClose}
    >
      {/* 中央玻璃卡片（阻止冒泡，点卡片内部不关闭） */}
      <div
        className="glass relative w-full max-w-sm p-8 !bg-ink-900/70"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 关闭按钮 */}
        <button
          type="button"
          onClick={onClose}
          className="absolute right-3 top-3 grid h-7 w-7 place-items-center rounded text-zinc-500 transition-colors hover:bg-white/10 hover:text-zinc-200"
          aria-label="关闭"
        >
          <X size={16} />
        </button>
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

      </div>
    </div>
  );
}
