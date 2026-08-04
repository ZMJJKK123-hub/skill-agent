"use client";

import {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { AlertTriangle, CheckCircle2, XCircle } from "lucide-react";

interface ToastItem {
  id: number;
  message: string;
  type: "success" | "error" | "warn";
}

type ToastFn = (message: string, type?: ToastItem["type"]) => void;

const ToastContext = createContext<ToastFn>(() => {});

const ICONS = {
  success: <CheckCircle2 size={16} className="text-forge-emerald" />,
  error: <XCircle size={16} className="text-rose-400" />,
  warn: <AlertTriangle size={16} className="text-forge-amber" />,
} as const;

const TOAST_CLASS = {
  success: "border-emerald-500/20 text-emerald-200",
  error: "border-rose-500/20 text-rose-200",
  warn: "border-amber-500/20 text-amber-200",
} as const;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const idRef = useRef(0);

  const push: ToastFn = useCallback((message, type = "success") => {
    const id = ++idRef.current;
    setToasts((list) => [...list, { id, message, type }]);
    setTimeout(() => {
      setToasts((list) => list.filter((t) => t.id !== id));
    }, 3200);
  }, []);

  return (
    <ToastContext.Provider value={push}>
      {children}
      <div className="pointer-events-none fixed right-4 top-16 z-[100] flex flex-col gap-2">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`toast-in pointer-events-auto flex items-start gap-2.5 rounded-xl border bg-zinc-900/90 px-4 py-2.5 text-sm shadow-2xl shadow-black/80 backdrop-blur-md ${TOAST_CLASS[t.type]}`}
          >
            {ICONS[t.type]}
            <span>{t.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast(): ToastFn {
  return useContext(ToastContext);
}