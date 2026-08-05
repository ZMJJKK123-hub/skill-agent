"use client";

import { ChevronDown, LogOut, Settings, UserRound } from "lucide-react";

interface UserNavDropdownProps {
  username: string;
  onLogout: () => void;
}

/**
 * 用户导航下拉菜单（GitHub 风格，暗黑主题精简版）
 *
 * hover 触发：外层 group 包裹触发器 + 菜单，
 * 鼠标移到用户名或菜单上时显示，移走后消失。
 */
export default function UserNavDropdown({ username, onLogout }: UserNavDropdownProps) {
  return (
    <div className="group relative">
      {/* 触发器：用户名 + 箭头 */}
      <button
        className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-zinc-300 transition-colors duration-150 hover:bg-white/10 hover:text-zinc-50"
      >
        <span className="grid h-6 w-6 place-items-center rounded-full bg-gradient-to-br from-forge-cyan to-forge-emerald">
          <UserRound size={14} className="text-ink-950" />
        </span>
        <span className="max-w-[120px] truncate">{username}</span>
        <ChevronDown size={14} className="text-zinc-500" />
      </button>

      {/* 下拉菜单 */}
      <div className="absolute right-0 top-full mt-2 w-64 origin-top-right rounded-lg border border-zinc-800 bg-zinc-950 py-2 opacity-0 shadow-2xl shadow-black/50 transition-all duration-200 invisible group-hover:visible group-hover:opacity-100">
        {/* Header：用户信息 */}
        <div className="flex items-center gap-3 px-4 py-1.5">
          <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-gradient-to-br from-forge-cyan to-forge-emerald">
            <UserRound size={18} className="text-ink-950" />
          </span>
          <span className="min-w-0">
            <span className="block truncate text-sm font-semibold text-zinc-100">
              {username}
            </span>
            <span className="block text-xs text-zinc-500">已在 MOD Forge 登录</span>
          </span>
        </div>
        <div className="my-1.5 h-px bg-zinc-800" />

        {/* Settings（未来可加设置页） */}
        <button
          className="flex w-full items-center gap-3 px-4 py-1.5 text-sm text-zinc-300 transition-colors duration-150 hover:bg-zinc-800/60 hover:text-zinc-50"
        >
          <Settings size={16} className="text-zinc-400" />
          设置
        </button>

        <div className="my-1.5 h-px bg-zinc-800" />

        {/* Sign out */}
        <button
          onClick={onLogout}
          className="flex w-full items-center gap-3 px-4 py-1.5 text-sm text-zinc-300 transition-colors duration-150 hover:bg-rose-950/30 hover:text-rose-400"
        >
          <LogOut size={16} className="text-zinc-400" />
          退出登录
        </button>
      </div>
    </div>
  );
}