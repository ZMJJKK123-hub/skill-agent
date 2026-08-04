"use client";

import { Boxes, History, LogOut, Wrench } from "lucide-react";

interface NavbarProps {
  active: "workbench" | "history";
  onChange: (view: "workbench" | "history") => void;
  username?: string | null;
  onLogout?: () => void;
}

const TABS = [
  { id: "workbench" as const, label: "制作台", icon: Wrench },
  { id: "history" as const, label: "历史记录", icon: History },
];

export default function Navbar({ active, onChange, username, onLogout }: NavbarProps) {
  return (
    <header className="sticky top-0 z-50 border-b border-white/5 bg-zinc-950/70 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-3 px-5">
        <div className="flex items-center gap-2.5">
          <div className="grid h-7 w-7 place-items-center rounded-md bg-gradient-to-br from-forge-cyan to-forge-emerald shadow-lg shadow-forge-cyan/25">
            <Boxes size={16} className="text-ink-950" strokeWidth={2.5} />
          </div>
          <span className="text-[15px] font-bold tracking-wide text-zinc-100">
            MOD Forge
          </span>
        </div>

        <div className="flex items-center gap-3">
          <nav className="flex items-center gap-1 rounded-full border border-white/5 bg-white/[0.03] p-1">
            {TABS.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => onChange(id)}
                className={`flex items-center gap-1.5 rounded-full px-4 py-1.5 text-sm transition-all duration-200 ${
                  active === id
                    ? "bg-white/10 text-zinc-100 shadow-sm"
                    : "text-zinc-500 hover:text-zinc-200"
                }`}
              >
                <Icon size={14} />
                {label}
              </button>
            ))}
          </nav>

          {username && (
            <div className="flex items-center gap-2">
              <span className="max-w-[100px] truncate font-mono text-xs text-zinc-400">
                {username}
              </span>
              <button
                onClick={onLogout}
                title="退出登录"
                className="grid h-8 w-8 place-items-center rounded-lg border border-white/10 text-zinc-400 transition-all duration-150 hover:border-rose-500/40 hover:text-rose-400"
              >
                <LogOut size={14} />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
