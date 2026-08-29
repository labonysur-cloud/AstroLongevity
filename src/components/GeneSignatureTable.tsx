"use client";
import { useEffect, useMemo, useState } from "react";

import type { GeneSignature } from "@/lib/types";

const PAGE_SIZE = 20;

type SortKey = keyof GeneSignature;

function fmt(n: number, digits = 3): string {
  if (Math.abs(n) < 0.001 || Math.abs(n) > 999) return n.toExponential(2);
  return n.toFixed(digits);
}

function fmtP(n: number): string {
  if (n === 0) return "0";
  if (n < 0.001) return n.toExponential(2);
  return n.toFixed(4);
}

export default function GeneSignatureTable() {
  const [rows, setRows] = useState<GeneSignature[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [sortKey, setSortKey] = useState<SortKey>("Average_Log2fc");
  const [sortDesc, setSortDesc] = useState(true);

  useEffect(() => {
    fetch("/data/concordant_signature.json").then(res => res.json()).then((raw: any[]) => {
      const mapped: GeneSignature[] = raw.map((r: any) => ({
        SYMBOL: String(r.SYMBOL ?? ""),
        Average_Log2fc: Number(r.Average_Log2fc ?? 0),
        Adj_p_101: Number(r["Adj.p.value_101"] ?? 1),
        Adj_p_104: Number(r["Adj.p.value_104"] ?? 1),
        Log2fc_101: Number(r.Log2fc_101 ?? 0),
        Log2fc_104: Number(r.Log2fc_104 ?? 0),
      }));
      setRows(mapped);
      setLoading(false);
    });
  }, []);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return rows.filter((r) => r.SYMBOL.toLowerCase().includes(q));
  }, [rows, search]);

  const sorted = useMemo(() => {
    return [...filtered].sort((a, b) => {
      const av = a[sortKey] as number | string;
      const bv = b[sortKey] as number | string;
      if (typeof av === "string") return sortDesc ? bv.toString().localeCompare(av) : av.localeCompare(bv.toString());
      return sortDesc ? (bv as number) - (av as number) : (av as number) - (bv as number);
    });
  }, [filtered, sortKey, sortDesc]);

  const totalPages = Math.ceil(sorted.length / PAGE_SIZE);
  const pageRows = sorted.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  function handleSort(key: SortKey) {
    if (sortKey === key) setSortDesc(!sortDesc);
    else { setSortKey(key); setSortDesc(true); }
    setPage(0);
  }

  const colClass = "px-3 py-2 text-left text-xs font-semibold text-[--muted] uppercase tracking-wider cursor-pointer hover:text-[--accent] select-none whitespace-nowrap";
  const arrow = (key: SortKey) => sortKey === key ? (sortDesc ? " ↓" : " ↑") : "";

  return (
    <section className="card">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-[--foreground]">
            Concordant Atrophy Signature
            <span className="ml-2 rounded-full bg-[--accent] px-2 py-0.5 text-xs font-bold text-[--background]">
              {rows.length} genes
            </span>
          </h2>
          <p className="mt-1 text-sm text-[--muted]">
            Genes significantly dysregulated (adj. p &lt; 0.05) in the same direction across
            both OSD-101 and OSD-104 spaceflight missions.
          </p>
        </div>
        <input
          type="text"
          placeholder="Search gene symbol…"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(0); }}
          className="rounded border border-[--card-border] bg-[--background] px-3 py-1.5 text-sm text-[--foreground] placeholder-[--muted] focus:border-[--accent] focus:outline-none"
        />
      </div>

      {loading ? (
        <div className="flex h-32 items-center justify-center text-[--muted]">Loading gene data…</div>
      ) : (
        <>
          <div className="overflow-x-auto rounded-lg border border-[--card-border]">
            <table className="w-full text-sm">
              <thead className="border-b border-[--card-border] bg-[--background]">
                <tr>
                  <th className={colClass} onClick={() => handleSort("SYMBOL")}>Gene{arrow("SYMBOL")}</th>
                  <th className={colClass} onClick={() => handleSort("Average_Log2fc")}>Avg Log2FC{arrow("Average_Log2fc")}</th>
                  <th className={colClass} onClick={() => handleSort("Log2fc_101")}>Log2FC (OSD-101){arrow("Log2fc_101")}</th>
                  <th className={colClass} onClick={() => handleSort("Log2fc_104")}>Log2FC (OSD-104){arrow("Log2fc_104")}</th>
                  <th className={colClass} onClick={() => handleSort("Adj_p_101")}>Adj.p (101){arrow("Adj_p_101")}</th>
                  <th className={colClass} onClick={() => handleSort("Adj_p_104")}>Adj.p (104){arrow("Adj_p_104")}</th>
                  <th className={colClass}>Direction</th>
                </tr>
              </thead>
              <tbody>
                {pageRows.map((r) => {
                  const up = r.Average_Log2fc > 0;
                  return (
                    <tr
                      key={r.SYMBOL}
                      className="border-b border-[--card-border] transition-colors hover:bg-[--background]"
                    >
                      <td className="px-3 py-2 font-mono font-semibold text-[--foreground]">{r.SYMBOL}</td>
                      <td className={`px-3 py-2 font-mono font-bold ${up ? "text-[--up]" : "text-[--down]"}`}>
                        {up ? "+" : ""}{fmt(r.Average_Log2fc)}
                      </td>
                      <td className={`px-3 py-2 font-mono ${r.Log2fc_101 > 0 ? "text-[--up]" : "text-[--down]"}`}>
                        {r.Log2fc_101 > 0 ? "+" : ""}{fmt(r.Log2fc_101)}
                      </td>
                      <td className={`px-3 py-2 font-mono ${r.Log2fc_104 > 0 ? "text-[--up]" : "text-[--down]"}`}>
                        {r.Log2fc_104 > 0 ? "+" : ""}{fmt(r.Log2fc_104)}
                      </td>
                      <td className="px-3 py-2 font-mono text-xs text-[--muted]">{fmtP(r.Adj_p_101)}</td>
                      <td className="px-3 py-2 font-mono text-xs text-[--muted]">{fmtP(r.Adj_p_104)}</td>
                      <td className="px-3 py-2">
                        <span className={`rounded px-2 py-0.5 text-xs font-semibold ${up ? "bg-red-900/40 text-[--up]" : "bg-blue-900/40 text-[--down]"}`}>
                          {up ? "▲ UP" : "▼ DOWN"}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="mt-3 flex items-center justify-between text-xs text-[--muted]">
            <span>
              Showing {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, sorted.length)} of {sorted.length} genes
            </span>
            <div className="flex gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage(page - 1)}
                className="rounded border border-[--card-border] px-3 py-1 disabled:opacity-30 hover:border-[--accent] hover:text-[--accent]"
              >
                ← Prev
              </button>
              <span className="flex items-center px-2">
                {page + 1} / {totalPages}
              </span>
              <button
                disabled={page >= totalPages - 1}
                onClick={() => setPage(page + 1)}
                className="rounded border border-[--card-border] px-3 py-1 disabled:opacity-30 hover:border-[--accent] hover:text-[--accent]"
              >
                Next →
              </button>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
