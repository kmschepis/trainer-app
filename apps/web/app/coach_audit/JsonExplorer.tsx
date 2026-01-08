"use client";

import { useMemo, useState } from "react";

export type JsonValue = null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue };

function isRecord(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

function isJsonValue(value: unknown): value is JsonValue {
  if (value === null) return true;
  const t = typeof value;
  if (t === "string" || t === "number" || t === "boolean") return true;
  if (Array.isArray(value)) return value.every(isJsonValue);
  if (isRecord(value)) return Object.values(value).every(isJsonValue);
  return false;
}

function parseJsonValue(text: string): { value: JsonValue | null; error: string | null } {
  try {
    const parsed: unknown = JSON.parse(text);
    if (!isJsonValue(parsed)) return { value: null, error: "Unsupported JSON value" };
    return { value: parsed, error: null };
  } catch (e) {
    return { value: null, error: e instanceof Error ? e.message : "Invalid JSON" };
  }
}

function stringifyJson(value: JsonValue): string {
  return JSON.stringify(value, null, 2);
}

function pathKey(path: Array<string | number>): string {
  return path.map((p) => (typeof p === "number" ? `[${p}]` : p)).join(".");
}

function setAtPath(root: JsonValue, path: Array<string | number>, nextLeaf: JsonValue): JsonValue {
  if (!path.length) return nextLeaf;

  const [head, ...rest] = path;

  if (Array.isArray(root)) {
    const idx = typeof head === "number" ? head : Number(head);
    const next = root.slice();
    next[idx] = setAtPath(next[idx] as JsonValue, rest, nextLeaf);
    return next;
  }

  if (root && typeof root === "object") {
    const key = String(head);
    return {
      ...(root as Record<string, JsonValue>),
      [key]: setAtPath((root as Record<string, JsonValue>)[key] as JsonValue, rest, nextLeaf),
    };
  }

  return root;
}

function inferLeaf(value: string, current: JsonValue): JsonValue {
  const trimmed = value.trim();
  if (trimmed === "null") return null;
  if (trimmed === "true") return true;
  if (trimmed === "false") return false;

  if (typeof current === "number") {
    const n = Number(trimmed);
    if (Number.isFinite(n)) return n;
  }

  // Allow quick numeric edit even if current is a string.
  if (/^-?\d+(\.\d+)?$/.test(trimmed)) {
    const n = Number(trimmed);
    if (Number.isFinite(n)) return n;
  }

  return value;
}

type JsonExplorerProps = {
  title: string;
  text: string;
  onTextChange: (next: string) => void;
  heightClassName?: string;
};

export function JsonExplorer({ title, text, onTextChange, heightClassName }: JsonExplorerProps) {
  const [mode, setMode] = useState<"explorer" | "raw">("explorer");

  const parsed = useMemo(() => parseJsonValue(text), [text]);

  function renderNode(label: string, value: JsonValue, path: Array<string | number>, depth: number) {
    const isObj = value && typeof value === "object" && !Array.isArray(value);
    const isArr = Array.isArray(value);

    const key = pathKey(path);

    if (!isObj && !isArr) {
      return (
        <div key={key} className="flex items-center gap-2 py-0.5">
          <div className="min-w-0 flex-1 truncate text-zinc-400">
            <span className="text-zinc-500">{label}</span>
          </div>
          <input
            className="w-64 rounded-lg border border-zinc-800 bg-zinc-900 px-2 py-1 font-mono text-[11px] text-zinc-100 focus:border-red-500 focus:outline-none"
            value={value === null ? "null" : String(value)}
            onChange={(e) => {
              const nextLeaf = inferLeaf(e.target.value, value);
              const nextRoot = setAtPath(parsed.value ?? null, path, nextLeaf);
              onTextChange(stringifyJson(nextRoot));
            }}
          />
        </div>
      );
    }

    return <CompositeNode key={key} label={label} value={value} path={path} depth={depth} onTextChange={onTextChange} rootValue={parsed.value} />;
  }

  if (mode === "raw") {
    return (
      <div>
        <div className="flex items-center justify-between">
          <div className="text-xs font-semibold text-zinc-200">{title}</div>
          <button
            className="rounded-lg border border-zinc-800 bg-zinc-900 px-2 py-1 text-[11px] font-semibold text-zinc-100 hover:bg-zinc-800"
            onClick={() => setMode("explorer")}
            type="button"
          >
            Explorer view
          </button>
        </div>

        <textarea
          className={`${heightClassName ?? "h-40"} mt-3 w-full resize-none rounded-xl border border-zinc-800 bg-zinc-900 p-3 font-mono text-[11px] text-zinc-100 focus:border-red-500 focus:outline-none`}
          value={text}
          onChange={(e) => onTextChange(e.target.value)}
        />
        {parsed.error ? <div className="mt-2 text-[11px] text-red-400">{parsed.error}</div> : null}
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div className="text-xs font-semibold text-zinc-200">{title}</div>
        <button
          className="rounded-lg border border-zinc-800 bg-zinc-900 px-2 py-1 text-[11px] font-semibold text-zinc-100 hover:bg-zinc-800"
          onClick={() => setMode("raw")}
          type="button"
        >
          Raw JSON
        </button>
      </div>

      {parsed.error || parsed.value === null ? (
        <div className="mt-3 text-[11px] text-red-400">{parsed.error ?? "Invalid JSON"}</div>
      ) : (
        <div className={`${heightClassName ?? "h-40"} mt-3 overflow-y-auto rounded-xl border border-zinc-900 bg-black/30 p-3`}
        >
          <div className="space-y-0.5">
            {Array.isArray(parsed.value)
              ? renderNode("(root)", parsed.value, [], 0)
              : renderNode("(root)", parsed.value, [], 0)}
          </div>
        </div>
      )}
    </div>
  );
}

type CompositeNodeProps = {
  label: string;
  value: JsonValue;
  path: Array<string | number>;
  depth: number;
  rootValue: JsonValue | null;
  onTextChange: (next: string) => void;
};

function CompositeNode({ label, value, path, depth, rootValue, onTextChange }: CompositeNodeProps) {
  const [open, setOpen] = useState(depth < 1);
  const isArr = Array.isArray(value);
  const isObj = value && typeof value === "object" && !isArr;

  const summary = isArr ? `[${value.length}]` : `{${Object.keys(value as Record<string, JsonValue>).length}}`;

  function renderChild(childKey: string | number, child: JsonValue) {
    const childPath = [...path, childKey];
    const childLabel = typeof childKey === "number" ? `[${childKey}]` : childKey;

    const isComposite = child && typeof child === "object";

    if (!isComposite) {
      return (
        <div key={pathKey(childPath)} className="flex items-center gap-2 py-0.5">
          <div className="min-w-0 flex-1 truncate text-zinc-400">
            <span className="text-zinc-500">{childLabel}</span>
          </div>
          <input
            className="w-64 rounded-lg border border-zinc-800 bg-zinc-900 px-2 py-1 font-mono text-[11px] text-zinc-100 focus:border-red-500 focus:outline-none"
            value={child === null ? "null" : String(child)}
            onChange={(e) => {
              const nextLeaf = inferLeaf(e.target.value, child);
              const nextRoot = setAtPath((rootValue ?? value) as JsonValue, childPath, nextLeaf);
              onTextChange(stringifyJson(nextRoot));
            }}
          />
        </div>
      );
    }

    return (
      <div key={pathKey(childPath)} className="pl-3">
        <CompositeNode
          label={childLabel}
          value={child}
          path={childPath}
          depth={depth + 1}
          rootValue={(rootValue ?? value) as JsonValue}
          onTextChange={onTextChange}
        />
      </div>
    );
  }

  return (
    <div className={depth === 0 ? "" : "pl-3"}>
      <button
        type="button"
        className="flex w-full items-center justify-between rounded-lg px-2 py-1 text-left hover:bg-zinc-900"
        onClick={() => setOpen((v) => !v)}
      >
        <div className="flex min-w-0 items-center gap-2">
          <span className="text-[11px] font-semibold text-zinc-200">{label}</span>
          <span className="text-[11px] text-zinc-500">{summary}</span>
        </div>
        <span className="text-[11px] text-zinc-500">{open ? "−" : "+"}</span>
      </button>

      {open ? (
        <div className="mt-1">
          {isArr
            ? (value as JsonValue[]).map((v, idx) => renderChild(idx, v))
            : Object.entries(value as Record<string, JsonValue>).map(([k, v]) => renderChild(k, v))}
        </div>
      ) : null}
    </div>
  );
}
