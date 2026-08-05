"use client";

import { useEffect, useMemo, useState } from "react";
import hljs from "highlight.js/lib/core";
import java from "highlight.js/lib/languages/java";
import json from "highlight.js/lib/languages/json";
import xml from "highlight.js/lib/languages/xml";
import properties from "highlight.js/lib/languages/properties";
import ini from "highlight.js/lib/languages/ini";
import {
  ChevronRight,
  File,
  FileCode2,
  FileJson,
  FileText,
  Folder,
  FolderOpen,
} from "lucide-react";
import * as API from "../../lib/api";
import type { FilePreview, TreeNode } from "../../lib/types";

// 注册常用语言
hljs.registerLanguage("java", java);
hljs.registerLanguage("json", json);
hljs.registerLanguage("xml", xml);
hljs.registerLanguage("properties", properties);
hljs.registerLanguage("ini", ini);

interface ArtifactExplorerProps {
  sessionId: string;
}

/** 根据文件名/扩展名选择图标 */
function fileIcon(name: string) {
  const lower = name.toLowerCase();
  if (lower.endsWith(".json")) return FileJson;
  if (
    lower.endsWith(".java") ||
    lower.endsWith(".js") ||
    lower.endsWith(".kt") ||
    lower.endsWith(".gradle")
  )
    return FileCode2;
  if (
    lower.endsWith(".xml") ||
    lower.endsWith(".yml") ||
    lower.endsWith(".yaml") ||
    lower.endsWith(".toml") ||
    lower.endsWith(".properties")
  )
    return FileText;
  return File;
}

/** 根据扩展名推断语法语言 */
function langFor(name: string): string | null {
  const lower = name.toLowerCase();
  if (lower.endsWith(".java")) return "java";
  if (lower.endsWith(".json")) return "json";
  if (lower.endsWith(".xml") || lower.endsWith(".mcmeta")) return "xml";
  if (lower.endsWith(".properties")) return "properties";
  if (lower.endsWith(".toml")) return "ini";
  return null;
}

function escapeHtml(s: string): string {
  const div = document.createElement("div");
  div.textContent = s || "";
  return div.innerHTML;
}

interface TreeNodeProps {
  node: TreeNode;
  depth: number;
  selectedPath: string | null;
  collapsed: Record<string, boolean>;
  onSelect: (path: string) => void;
  onToggle: (path: string) => void;
}

function TreeNode({
  node,
  depth,
  selectedPath,
  collapsed,
  onSelect,
  onToggle,
}: TreeNodeProps) {
  const isDir = node.type === "dir";
  // VS Code 风格：每级固定递增 12px，紧凑且适合深层级
  const indent = depth * 12 + 8;
  const isOpen = !collapsed[node.path];
  const Icon = isDir ? (isOpen ? FolderOpen : Folder) : fileIcon(node.name);

  return (
    <div>
      <button
        onClick={() => (isDir ? onToggle(node.path) : onSelect(node.path))}
        style={{ paddingLeft: indent }}
        className={`flex h-7 w-full items-center gap-1.5 pr-2 text-left font-mono text-[13px] transition-colors duration-100 ${
          selectedPath === node.path
            ? "bg-zinc-800/70 text-zinc-100"
            : "text-zinc-300 hover:bg-zinc-800/50 hover:text-zinc-100"
        }`}
      >
        {isDir ? (
          <ChevronRight
            size={11}
            className={`shrink-0 text-zinc-500 transition-transform duration-150 ${
              isOpen ? "rotate-90" : ""
            }`}
          />
        ) : (
          <span className="w-3.5 shrink-0" />
        )}
        <Icon
          size={14}
          className={`shrink-0 ${
            isDir ? "text-forge-amber/70" : "text-zinc-500"
          }`}
        />
        {/* 不 truncate：深层级也完整显示文件名，超宽时父容器横向滚动 */}
        <span className="flex-1 whitespace-nowrap">{node.name}</span>
        {node.type === "file" && (
          <span className="ml-auto shrink-0 text-xs text-zinc-600">
            {(node.size || 0) / 1024 > 0
              ? `${((node.size || 0) / 1024).toFixed(1)}k`
              : "<1k"}
          </span>
        )}
      </button>
      {isDir && isOpen && node.children && (
        <div>{/* 子节点缩进已由 depth 计算，无需额外容器样式 */}
          {node.children.map((child) => (
            <TreeNode
              key={child.path}
              node={child}
              depth={depth + 1}
              selectedPath={selectedPath}
              collapsed={collapsed}
              onSelect={onSelect}
              onToggle={onToggle}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function CodeViewer({ content, language }: { content: string; language: string | null }) {
  const highlighted = useMemo(() => {
    if (!content) return { __html: "" };
    try {
      if (language && hljs.getLanguage(language)) {
        return { __html: hljs.highlight(content, { language }).value };
      }
      return { __html: hljs.highlightAuto(content).value };
    } catch {
      return { __html: escapeHtml(content) };
    }
  }, [content, language]);

  return (
    <pre className="overflow-x-auto overflow-y-auto p-4 font-mono text-[12.5px] leading-relaxed text-zinc-300">
      <code
        dangerouslySetInnerHTML={highlighted}
        className={language ? `hljs language-${language}` : "hljs"}
      />
    </pre>
  );
}

function countFiles(node: TreeNode): number {
  if (node.type === "file") return 1;
  return (node.children || []).reduce((acc, c) => acc + countFiles(c), 0);
}

export default function ArtifactExplorer({ sessionId }: ArtifactExplorerProps) {
  const [tree, setTree] = useState<TreeNode | null>(null);
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});
  const [selected, setSelected] = useState<string | null>(null);
  const [preview, setPreview] = useState<FilePreview | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let active = true;
    API.getFiles(sessionId)
      .then((data) => {
        if (!active) return;
        if ("tree" in data) setTree(data.tree);
      })
      .catch(() => {
        if (active) setTree(null);
      });
    return () => {
      active = false;
    };
  }, [sessionId]);

  const toggle = (path: string) => {
    setCollapsed((c) => ({ ...c, [path]: !c[path] }));
  };

  const select = async (path: string) => {
    setSelected(path);
    setPreview(null);
    setLoading(true);
    try {
      const data = await API.getFiles(sessionId, path);
      if ("content" in data) setPreview(data as FilePreview);
    } catch {
      /* 预览失败 */
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass overflow-hidden">
      <div className="flex items-center justify-between border-b border-white/5 px-4 py-2.5">
        <span className="text-sm font-semibold text-zinc-200">产物浏览器</span>
        <span className="font-mono text-xs text-zinc-500">
          {tree ? countFiles(tree) : 0} 个文件
        </span>
      </div>

      <div className="grid min-h-[320px] grid-cols-[240px_1fr] max-md:grid-cols-1">
        {/* 左侧文件树（紧凑/高密度/整行交互/横向滚动） */}
        <div className="file-tree-scroll max-h-[480px] overflow-x-auto overflow-y-auto border-r border-white/5 bg-ink-950/40 p-1">
          {!tree ? (
            <div className="flex h-full min-h-[280px] items-center justify-center text-xs text-zinc-600">
              暂无产物文件
            </div>
          ) : (
            tree.children?.map((node) => (
              <TreeNode
                key={node.path}
                node={node}
                depth={0}
                selectedPath={selected}
                collapsed={collapsed}
                onSelect={select}
                onToggle={toggle}
              />
            ))
          )}
        </div>

        {/* 右侧代码预览 */}
        <div className="max-h-[480px] overflow-auto bg-[#0d0d0d]">
          {loading ? (
            <div className="flex h-full min-h-[280px] items-center justify-center">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/10 border-t-forge-cyan" />
            </div>
          ) : selected && preview ? (
            <CodeViewer content={preview.content} language={langFor(selected)} />
          ) : (
            <div className="flex h-full min-h-[280px] items-center justify-center text-sm text-zinc-600">
              选择文件以预览
            </div>
          )}
        </div>
      </div>
    </div>
  );
}