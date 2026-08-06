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
  error: <XCircle size={16} className="text-red-400" />,
  warn: <AlertTriangle size={16} className="text-forge-amber" />,
} as const;

const TOAST_CLASS = {
  success: "border-emerald-500/30 bg-emerald-950/60 text-emerald-300",
  error: "border-red-500/30 bg-red-950/60 text-red-300",
  warn: "border-amber-500/30 bg-amber-950/60 text-amber-300",
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
            className={`animate-fadeUp pointer-events-auto flex items-start gap-2.5 rounded-lg border px-4 py-2.5 text-sm shadow-lg backdrop-blur-md ${TOAST_CLASS[t.type]}`}
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