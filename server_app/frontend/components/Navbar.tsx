"use client";

import { Boxes, History, LogIn, UserPlus, Wrench } from "lucide-react";
import UserNavDropdown from "./UserNavDropdown";

interface NavbarProps {
  active: "workbench" | "history";
  onChange: (view: "workbench" | "history") => void;
  username?: string | null;
  onLoginClick?: () => void;
  onRegisterClick?: () => void;
  onLogout?: () => void;
}

const TABS = [
  { id: "workbench" as const, label: "制作台", icon: Wrench },
  { id: "history" as const, label: "历史记录", icon: History },
];

export default function Navbar({
  active,
  onChange,
  username,
  onLoginClick,
  onRegisterClick,
  onLogout,
}: NavbarProps) {
  return (
    <header className="sticky top-0 z-50 border-b border-white/5 bg-zinc-950/70 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-3 px-5">
        {/* 最左：徽标 + 标题 */}
        <div className="flex items-center gap-2.5">
          <div className="grid h-7 w-7 place-items-center rounded-md bg-gradient-to-br from-forge-cyan to-forge-emerald shadow-lg shadow-forge-cyan/25">
            <Boxes size={16} className="text-ink-950" strokeWidth={2.5} />
          </div>
          <span className="text-[15px] font-bold tracking-wide text-zinc-100">
            MOD Forge
          </span>
        </div>

        {/* 右侧：tab（直角 + 竖线分割）+ 登录/用户 */}
        <div className="flex items-center gap-2">
          {/* tab：无胶囊、无圆角，中间竖直线隔离 */}
          <nav className="flex items-center">
            {TABS.map(({ id, label, icon: Icon }, i) => (
              <div key={id} className="flex items-center">
                {i > 0 && <div className="h-5 w-px bg-white/10" />}
                <button
                  onClick={() => onChange(id)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 text-sm transition-colors duration-150 ${
                    active === id
                      ? "bg-white/10 text-zinc-100"
                      : "text-zinc-500 hover:bg-white/[0.06] hover:text-zinc-200"
                  }`}
                >
                  <Icon size={14} />
                  {label}
                </button>
              </div>
            ))}
          </nav>

          <div className="h-5 w-px bg-white/10" />

          {/* 最右：未登录 = 登录/注册按钮；已登录 = 用户名下拉 */}
          {username ? (
            <UserNavDropdown
              username={username}
              onLogout={onLogout || (() => undefined)}
            />
          ) : (
            <div className="flex items-center">
              <button
                onClick={onLoginClick}
                className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-zinc-300 transition-colors duration-150 hover:bg-white/10 hover:text-zinc-50"
              >
                <LogIn size={14} />
                登录
              </button>
              <div className="mx-1 h-5 w-px bg-white/10" />
              <button
                onClick={onRegisterClick}
                className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-zinc-300 transition-colors duration-150 hover:bg-white/10 hover:text-zinc-50"
              >
                <UserPlus size={14} />
                注册
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}